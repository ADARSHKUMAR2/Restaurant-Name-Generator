import os
import psycopg2
from pinecone import Pinecone
from dotenv import load_dotenv
import time

load_dotenv()

print("🗄️ Connecting to Databases (Postgres & Pinecone)...")

# 1. Connect to PostgreSQL
MAX_RETRIES = 5
for attempt in range(MAX_RETRIES):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="restaurant_analytics", 
            user="admin", 
            password="adminpassword", 
            host=os.getenv("DB_HOST", "localhost"), 
            port=os.getenv("DB_PORT", "5432") # Notice it defaults to Docker's 5432 port now!
        )
        conn.autocommit = True 
        cursor = conn.cursor()
        print("   ✅ Connected to Postgres!")
        
        # --- Automatically create the table if it was wiped! ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generations (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                cuisine_requested TEXT,
                restaurant_name TEXT
            )
        """)
        print("   ✅ Verified 'generations' table exists!")
        break # If successful, break out of the loop!

    except psycopg2.OperationalError as e:
        if attempt < MAX_RETRIES - 1:
            print(f"   ⏳ Postgres is still booting. Retrying in 3 seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
            time.sleep(3)
        else:
            print("   ❌ FATAL: Could not connect to Postgres after multiple attempts.")
            raise e

# 2. Connect to Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("restaurant-reviews")

def save_to_postgres(timestamp, cuisine, name):
    """Saves basic info to Postgres and returns the new Database ID"""
    cursor.execute("""
        INSERT INTO generations (timestamp, cuisine_requested, restaurant_name)
        VALUES (%s, %s, %s) RETURNING id;
    """, (timestamp, cuisine, name))
    
    return cursor.fetchone()[0]

def save_to_pinecone(db_id, name, cuisine, review, vector):
    """
    Saves the restaurant data and its embedding to Pinecone.
    Matches the 5 arguments called in consumer.py
    """
    # Initialize index (ensure this is at the top of your storage.py)
    # pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    # index = pc.Index("restaurant-reviews")
    
    index.upsert(
        vectors=[
            (
                str(db_id), # ID must be a string
                vector, 
                {
                    "name": name, 
                    "cuisine": cuisine, 
                    "review": review
                } # Metadata for filtering and display
            )
        ]
    )
    print(f"   🌲 Vector saved to Pinecone for ID: {db_id}")