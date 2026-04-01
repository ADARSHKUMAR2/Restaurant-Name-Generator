import json
from confluent_kafka import Consumer
import os

# Import our customized toolboxes!
from services.storage import save_to_postgres, save_to_pinecone
from services.ai_agents import write_review, generate_vector
from services.alerts import send_discord_alert

# --- SETUP KAFKA ---
consumer = Consumer({
    # Use the environment variable, but default to localhost if it's missing
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'localhost:9092'), 
    'group.id': 'ai-analytics-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['restaurant-events'])

print("🎧 Clean Multi-Agent Consumer is LIVE! Waiting for data...")

# --- THE EVENT LOOP ---
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        # 1. Catch the Event
        event = json.loads(msg.value().decode('utf-8'))
        cuisine = event['cuisine_requested']
        name = event['restaurant_generated']
        
        print(f"\n📥 CAUGHT: {name} ({cuisine})")

        # 2. Save to Relational DB
        db_id = save_to_postgres(event['timestamp'], cuisine, name)
        print(f"   💾 Saved to Postgres (ID: {db_id})")

        # 3. AI Writes the Review
        print("   🧠 Llama 3.1 is writing a review...")
        review_text = write_review(cuisine, name)

        # 4. AI Does the Math (Embeddings)
        print("   🔢 Vectorizing and saving to Pinecone...")
        vector = generate_vector(review_text)
        
        # 5. Save to Vector DB
        metadata = {"name": name, "cuisine": cuisine, "review": review_text}
        save_to_pinecone(db_id, vector, metadata)
        print("   ✅ Vector Pipeline Complete!")
        
        # 6. Fire the Discord Alert
        print("   📢 Sending Alert...")
        send_discord_alert(name, cuisine, db_id)

except KeyboardInterrupt:
    print("\nShutting down gracefully...")
finally:
    consumer.close()