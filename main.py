import streamlit as st
import langchain_helper
import json
from datetime import datetime
from confluent_kafka import Producer
import psycopg2
import pandas as pd
import time

# Connect our frontend to the Kafka server
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def log_generation_event(cuisine, restaurant_name):
    event_payload = {
        "timestamp": datetime.now().isoformat(),
        "cuisine_requested": cuisine,
        "restaurant_generated": restaurant_name
    }
    producer.produce('restaurant-events', value=json.dumps(event_payload).encode('utf-8'))
    producer.flush()

st.title("Restaurant Name Generator 🍽️")

# --- THE MAGIC: Create two separate tabs ---
tab1, tab2 = st.tabs(["✨ Generator", "📊 Analytics Dashboard"])

# --- TAB 1: Your Existing App ---
with tab1:
    cuisine = st.sidebar.selectbox("Pick a Cuisine", ("Indian", "Mexican", "Italian", "American", "Japanese"))

    if cuisine:
        st.info(f"Cooking up a {cuisine} restaurant...") # Quick visual feedback for the user
        # ⏱️ TIMER 1: The AI Generation
        start_ai = time.time()
        # Generate the restaurant
        response = langchain_helper.generate_restaurant_name_and_items(cuisine)
        end_ai = time.time()
        print(f"\n⏱️ AI Generation took: {end_ai - start_ai:.2f} seconds")
        
        # Safely extract the restaurant name (handling both string and dict responses)
        if isinstance(response, dict):
            # If your helper returns a dictionary, grab the name (default to 'Unknown Name' if key is missing)
            restaurant_name = response.get('restaurant_name', 'Unknown Name').strip()
            
            # ONLY try to print menu items if your helper actually generates them!
            if 'menu_items' in response:
                st.header(restaurant_name)
                st.write("**Menu Items:**")
                st.write(response['menu_items'].strip())
            else:
                st.header(restaurant_name)
        else:
            # If your helper just returns a plain string, use that directly!
            restaurant_name = response.strip()
            st.header(restaurant_name)
        
        # ⏱️ TIMER 2: The Kafka Handoff
        start_kafka = time.time()
        # Fire the Kafka Event!
        log_generation_event(cuisine, restaurant_name)
        end_kafka = time.time()
        print(f"⏱️ Kafka routing took: {end_kafka - start_kafka:.2f} seconds")

# --- TAB 2: The Database Viewer ---
with tab2:
    st.header("Live Generations Database")
    
    # We use a button so it doesn't constantly query the DB on every minor click
    if st.button("🔄 Fetch Latest Data"):
        try:
            # 1. Connect to Postgres
            conn = psycopg2.connect(
                dbname="restaurant_analytics",
                user="admin",
                password="adminpassword",
                host="localhost",
                port="5433" # Using our updated port!
            )
            
            # 2. Grab the data and turn it into a Pandas DataFrame
            query = "SELECT timestamp, cuisine_requested, restaurant_name FROM generations ORDER BY timestamp DESC"
            df = pd.read_sql(query, conn)
            
            # 3. Display Quick Stats
            st.subheader("Quick Stats")
            col1, col2 = st.columns(2)
            col1.metric("Total Restaurants Generated", len(df))
            
            if not df.empty:
                top_cuisine = df['cuisine_requested'].mode()[0]
                col2.metric("Most Popular Cuisine", top_cuisine)
            
            # 4. Draw the interactive table
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            conn.close()
            
        except Exception as e:
            st.error(f"Could not connect to the database: {e}")