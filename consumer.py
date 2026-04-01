import os
import json
from dotenv import load_dotenv
from confluent_kafka import Consumer
import psycopg2
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
from alerts import send_discord_alert

# Load environment variables
load_dotenv()

# --- 1. INITIALIZE DATABASES & AI ---
print("Connecting to PostgreSQL...")
conn = psycopg2.connect(dbname="restaurant_analytics", user="admin", password="adminpassword", host="localhost", port="5433")
cursor = conn.cursor()

print("Connecting to Pinecone & AI Models...")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("restaurant-reviews")

# The New "Brain" of our background worker
print("Loading Llama 3.1 & Hugging Face Embeddings...")
llm = ChatGroq(model_name="llama-3.1-8b-instant") 
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") # Free, local embedding model

# --- 2. SETUP KAFKA ---
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'ai-analytics-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['restaurant-events'])
print("🎧 Multi-Agent Consumer is LIVE! Waiting for data...")

# --- 3. THE EVENT LOOP ---
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        event = json.loads(msg.value().decode('utf-8'))
        cuisine = event['cuisine_requested']
        name = event['restaurant_generated']
        
        print(f"\n📥 CAUGHT: {name} ({cuisine})")

        # STEP A: Save to Postgres and get the ID
        cursor.execute("""
            INSERT INTO generations (timestamp, cuisine_requested, restaurant_name)
            VALUES (%s, %s, %s) RETURNING id;
        """, (event['timestamp'], cuisine, name))
        
        db_id = cursor.fetchone()[0]
        conn.commit()
        print(f"   💾 Saved to Postgres (ID: {db_id})")

        # STEP B: Llama 3.1 writes a review
        print("   🧠 Llama 3.1 is writing a review...")
        prompt = f"Write a vivid, 2-sentence food critic review for a {cuisine} restaurant named '{name}'."
        review_text = llm.invoke(prompt).content

        # STEP C: Hugging Face converts to Embeddings & Saves to Pinecone
        print("   🔢 Vectorizing and saving to Pinecone...")
        vector = embeddings.embed_query(review_text)
        
        index.upsert(
            vectors=[
                {
                    "id": str(db_id), # Link Pinecone to Postgres!
                    "values": vector,
                    "metadata": {
                        "name": name,
                        "cuisine": cuisine,
                        "review": review_text
                    }
                }
            ]
        )
        print("   ✅ Full AI Pipeline Complete!")

        # --- STEP D: Fire the Alert! ---
        print("   📢 Sending Discord Alert...")
        send_discord_alert(name, cuisine, db_id)

except KeyboardInterrupt:
    print("Shutting down...")
finally:
    cursor.close()
    conn.close()
    consumer.close()