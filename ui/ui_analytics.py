import streamlit as st
import psycopg2
import pandas as pd

def render_dashboard():
    """Connects to Postgres and draws the Streamlit Analytics Dashboard"""
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
                port="5433" 
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