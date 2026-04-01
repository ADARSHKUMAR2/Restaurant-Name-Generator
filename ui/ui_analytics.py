import streamlit as st
import psycopg2
import pandas as pd
import os

def render_dashboard():
    st.header("Live Generations Database")
    
    if st.button("🔄 Fetch Latest Data"):
        try:
            # 1. Use the Cloud-Ready connection string
            # If DATABASE_URL exists (Cloud), use it. 
            # Otherwise (Local Docker), build the string manually.
            db_url = os.getenv("DATABASE_URL")
            
            if db_url:
                conn = psycopg2.connect(db_url)
            else:
                # Local Docker Fallback
                conn = psycopg2.connect(
                    dbname="restaurant_analytics",
                    user="admin",
                    password="adminpassword",
                    host="postgres", # Must be the service name 'postgres'
                    port="5432"      # Must be 5432 inside Docker!
                )
            
            # 2. Grab the data
            query = "SELECT timestamp, cuisine_requested, restaurant_name FROM generations ORDER BY id DESC"
            df = pd.read_sql(query, conn)
            
            # 3. Stats & Display
            if not df.empty:
                st.subheader("Quick Stats")
                col1, col2 = st.columns(2)
                col1.metric("Total Restaurants Generated", len(df))
                top_cuisine = df['cuisine_requested'].mode()[0]
                col2.metric("Most Popular Cuisine", top_cuisine)
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("The database is currently empty. Go generate a restaurant first!")
            
            conn.close()
            
        except Exception as e:
            st.error(f"Could not connect to the database: {e}")