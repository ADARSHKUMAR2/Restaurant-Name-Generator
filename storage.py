import os
import psycopg2
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

print("🗄️ Connecting to Databases (Postgres & Pinecone)...")

# 1. Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="restaurant_analytics", 
    user="admin", 
    password="adminpassword", 
    host="localhost", 
    port="5433"
)
# This automatically commits every query so we don't have to call conn.commit() manually!
conn.autocommit = True 
cursor = conn.cursor()

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

def save_to_pinecone(db_id, vector, metadata):
    """Links the Postgres ID to the mathematical vector in Pinecone"""
    index.upsert(
        vectors=[{
            "id": str(db_id),
            "values": vector,
            "metadata": metadata
        }]
    )