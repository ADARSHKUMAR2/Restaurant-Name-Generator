from confluent_kafka import Consumer
import json

# 1. Connect to our local Docker Kafka server
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'analytics-worker-group',
    'auto.offset.reset': 'earliest'
})

# 2. Subscribe to our specific event channel
consumer.subscribe(['restaurant-events'])
print("🎧 Kafka Consumer is live! Listening for new generations...")

# 3. Create an infinite loop to constantly check for messages
try:
    while True:
        # Check for a new message every 1 second
        msg = consumer.poll(1.0)
        
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        # 4. If we catch a message, decode the JSON and print it!
        event = json.loads(msg.value().decode('utf-8'))
        print(f"🚀 CAUGHT EVENT: Someone just generated a {event['cuisine_requested']} restaurant named '{event['restaurant_generated']}'!")

except KeyboardInterrupt:
    print("Shutting down consumer...")
finally:
    consumer.close()