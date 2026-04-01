import streamlit as st
from services import langchain_helper
from services.events import log_generation_event

def render_generator_tab():
    """Renders the UI for generating new restaurants"""
    cuisine = st.sidebar.selectbox("Pick a Cuisine", ("Indian", "Mexican", "Italian", "American", "Japanese"))

    if cuisine:
        st.info(f"Cooking up a {cuisine} restaurant...") 
        response = langchain_helper.generate_restaurant_name_and_items(cuisine)
        
        if isinstance(response, dict):
            restaurant_name = response.get('restaurant_name', 'Unknown Name').strip()
            if 'menu_items' in response:
                st.header(restaurant_name)
                st.write("**Menu Items:**")
                for item in response['menu_items']:
                    st.write(f"- {item}")
            else:
                st.header(restaurant_name)
        else:
            restaurant_name = response.strip()
            st.header(restaurant_name)
        
        # Fire the Kafka Event!
        log_generation_event(cuisine, restaurant_name)