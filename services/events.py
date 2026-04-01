import json
from datetime import datetime
from confluent_kafka import Producer
import os

# 1. FIX: Use 'redpanda:29092' for internal Docker communication
KAFKA_SERVER = os.getenv('KAFKA_BROKER', 'redpanda:29092')
producer = Producer({'bootstrap.servers': KAFKA_SERVER})

def log_generation_event(cuisine, restaurant_name):
    """Fires a lightweight event to Redpanda/Kafka"""
    
    # 2. FIX: Ensure keys match what the consumer expects
    event_payload = {
        "timestamp": datetime.now().isoformat(),
        "cuisine": cuisine,             # Changed from cuisine_requested
        "restaurant_name": restaurant_name # Changed from restaurant_generated
    }
    
    # 3. FIX: Use the correct topic name 'restaurant_generations'
    topic = 'restaurant_generations' 
    
    try:
        producer.produce(
            topic, 
            value=json.dumps(event_payload).encode('utf-8')
        )
        producer.flush()
        print(f"📡 Event sent to Kafka topic '{topic}': {restaurant_name}")
    except Exception as e:
        print(f"❌ Failed to send Kafka event: {e}")