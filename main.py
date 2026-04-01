import streamlit as st
import langchain_helper

# Import your newly separated modules!
from events import log_generation_event
from analytics import render_dashboard
from search import perform_semantic_search

st.set_page_config(page_title="Restaurant Generator", page_icon="🍽️")
st.title("Restaurant Name Generator 🍽️")

# --- THE MAGIC: Create two separate tabs ---
tab1, tab2, tab3 = st.tabs(["✨ Generator", "📊 Analytics", "🔍 Semantic Search"])

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

    # --- TAB 3: SEMANTIC SEARCH ---
with tab3:
    st.header("Find the Perfect Restaurant")
    st.write("Don't search by name. Search by vibe, feeling, or specific cravings!")
    
    # 1. The Search Bar
    search_query = st.text_input("What are you looking for?", placeholder="e.g., A cozy, dimly lit place for a romantic date...")
    
    # 2. The Search Action
    if st.button("Search AI Memory"):
        if search_query:
            with st.spinner("Scanning vector database..."):
                # Call our new module
                results = perform_semantic_search(search_query)
                
                if results:
                    st.success(f"Found {len(results)} matches!")
                    
                    # 3. Draw the results
                    for r in results:
                        # Convert the math score to a recognizable percentage
                        match_percentage = round(r['score'] * 100, 1)
                        
                        # Use an expander box to keep the UI clean
                        with st.expander(f"**{r['name']}** ({r['cuisine']}) — {match_percentage}% Match", expanded=True):
                            st.write(f"*{r['review']}*")
                            st.caption(f"Database ID: {r['id']}")
                else:
                    st.warning("No matches found. Try generating a few more restaurants first!")