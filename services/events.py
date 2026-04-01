import json
from datetime import datetime
from confluent_kafka import Producer
import os

# Connect our frontend to the Kafka server
producer = Producer({'bootstrap.servers': os.getenv('KAFKA_BROKER', 'localhost:9092')})

def log_generation_event(cuisine, restaurant_name):
    """Fires a lightweight event to Redpanda/Kafka"""
    event_payload = {
        "timestamp": datetime.now().isoformat(),
        "cuisine_requested": cuisine,
        "restaurant_generated": restaurant_name
    }
    producer.produce('restaurant-events', value=json.dumps(event_payload).encode('utf-8'))
    producer.flush()