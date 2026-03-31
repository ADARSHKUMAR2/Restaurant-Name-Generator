from confluent_kafka import Consumer
import psycopg2
import json

# 1. Connect to PostgreSQL
print("Connecting to PostgreSQL...")
conn = psycopg2.connect(
    dbname="restaurant_analytics",
    user="admin",
    password="adminpassword",
    host="localhost",
    port="5433"
)
cursor = conn.cursor()

# 2. Create the table automatically if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS generations (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP,
        cuisine_requested VARCHAR(100),
        restaurant_name TEXT
    );
""")

# Force the existing column to upgrade to TEXT just in case it was created as VARCHAR
cursor.execute("""
    ALTER TABLE generations 
    ALTER COLUMN restaurant_name TYPE TEXT;
""")

conn.commit()
print("✅ Database table ready (and upgraded to TEXT)!")

# 3. Connect to Redpanda
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'postgres-writer-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['restaurant-events'])
print("🎧 Kafka Consumer is live! Listening for events to save...")

try:
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        # 4. Decode the message and save to Postgres
        event = json.loads(msg.value().decode('utf-8'))
        
        cursor.execute("""
            INSERT INTO generations (timestamp, cuisine_requested, restaurant_name)
            VALUES (%s, %s, %s)
        """, (event['timestamp'], event['cuisine_requested'], event['restaurant_generated']))
        
        conn.commit() # Lock in the save
        
        print(f"💾 SAVED TO DB: {event['cuisine_requested']} -> {event['restaurant_generated']}")

except KeyboardInterrupt:
    print("Shutting down...")
finally:
    cursor.close()
    conn.close()
    consumer.close()