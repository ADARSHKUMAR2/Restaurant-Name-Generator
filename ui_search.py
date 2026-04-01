import streamlit as st
from search import perform_semantic_search

def render_search_tab():
    """Renders the UI for the Pinecone Semantic Search"""
    st.header("Find the Perfect Restaurant")
    st.write("Don't search by name. Search by vibe, feeling, or specific cravings!")
    
    # 1. The Search Bar
    search_query = st.text_input("What are you looking for?", placeholder="e.g., A cozy, dimly lit place for a romantic date...")
    
    # 2. The Search Action
    if st.button("Search AI Memory"):
        if search_query:
            with st.spinner("Scanning vector database..."):
                results = perform_semantic_search(search_query)
                
                if results:
                    st.success(f"Found {len(results)} matches!")
                    
                    # 3. Draw the results
                    for r in results:
                        match_percentage = round(r['score'] * 100, 1)
                        with st.expander(f"**{r['name']}** ({r['cuisine']}) — {match_percentage}% Match", expanded=True):
                            st.write(f"*{r['review']}*")
                            st.caption(f"Database ID: {r['id']}")
                else:
                    st.warning("No matches found. Try generating a few more restaurants first!")