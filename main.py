import streamlit as st
import langchain_helper
import json
from datetime import datetime
from confluent_kafka import Producer

# Connect our frontend to the Kafka server
producer = Producer({'bootstrap.servers': 'localhost:9092'})

# --- OUR MOCK KAFKA PRODUCER ---
def log_generation_event(cuisine, restaurant_name):
    # This is the exact payload structure Kafka will use later
    event_payload = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "generation_success",
        "cuisine_requested": cuisine,
        "restaurant_generated": restaurant_name
    }
    
    # BROADCAST TO KAFKA
    # We send the payload to the 'restaurant-events' topic
    producer.produce(
        'restaurant-events', 
        value=json.dumps(event_payload).encode('utf-8')
    )
    # Ensure it sends immediately
    producer.flush()

    # We append ("a") the event to a local file so it builds a running log
    with open("analytics_events.jsonl", "a") as f:
        f.write(json.dumps(event_payload) + "\n")
# -------------------------------

st.title("Restaurant Name Generator")
cuisine = st.sidebar.selectbox("Pick a Cuisine", ("Indian", "Italian", "Mexican", "Arabic", "American"))

if cuisine:
    response = langchain_helper.generate_restaurant_name_and_items(cuisine)
    st.header(response['restaurant_name'].strip())
    menu_items = response['menu_item'].strip().split(",")
    st.write("**Menu Items**")
    log_generation_event(cuisine, response['restaurant_name'])
    for item in menu_items:
        st.write("-" , item)