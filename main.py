import streamlit as st
import langchain_helper

# Import your newly separated modules!
from events import log_generation_event
from analytics import render_dashboard

st.set_page_config(page_title="Restaurant Generator", page_icon="🍽️")
st.title("Restaurant Name Generator 🍽️")

# --- THE MAGIC: Create two separate tabs ---
tab1, tab2 = st.tabs(["✨ Generator", "📊 Analytics Dashboard"])

# --- TAB 1: The AI App ---
with tab1:
    cuisine = st.sidebar.selectbox("Pick a Cuisine", ("Indian", "Mexican", "Italian", "American", "Japanese"))

    if cuisine:
        st.info(f"Cooking up a {cuisine} restaurant...") 
        
        # 1. Ask the AI for a name
        response = langchain_helper.generate_restaurant_name_and_items(cuisine)
        
        # 2. Safely extract and display it
        if isinstance(response, dict):
            restaurant_name = response.get('restaurant_name', 'Unknown Name').strip()
            if 'menu_items' in response:
                st.header(restaurant_name)
                st.write("**Menu Items:**")
                st.write(response['menu_items'].strip())
            else:
                st.header(restaurant_name)
        else:
            restaurant_name = response.strip()
            st.header(restaurant_name)
        
        # 3. Fire the Kafka Event (now handled securely in events.py!)
        log_generation_event(cuisine, restaurant_name)

# --- TAB 2: The Database Viewer ---
with tab2:
    render_dashboard()