import streamlit as st

# Import our modular UI components!
from ui_generator import render_generator_tab
from analytics import render_dashboard
from ui_search import render_search_tab

# 1. Global Page Configuration
st.set_page_config(page_title="Restaurant Generator", page_icon="🍽️", layout="centered")
st.title("Restaurant Name Generator 🍽️")

# 2. Setup the Router (Tabs)
tab1, tab2, tab3 = st.tabs(["✨ Generator", "📊 Analytics", "🔍 Semantic Search"])

# 3. Mount the Components
with tab1:
    render_generator_tab()

with tab2:
    render_dashboard()

with tab3:
    render_search_tab()