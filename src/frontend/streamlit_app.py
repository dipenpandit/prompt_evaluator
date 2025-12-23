import streamlit as st  
from src.frontend.ui.add_prompt import add_new_prompt
from src.frontend.ui.my_prompts import my_prompts
from src.config import settings

API_URL = settings.api_url

st.set_page_config(page_title="Prompt Evaluator")

st.title("Prompt Evaluator")

## --- SIDEBAR ---
page = st.sidebar.radio(
    "Select Page", 
    ["Create Project", "My Projects"]
)

# Create Project
if page == "Create Project":
    st.subheader("Add New Prompt Project")
    add_new_prompt()

# My Projects 
if page == "My Projects":
    st.subheader("My Prompt Projects")
    my_prompts()





