import streamlit as st
from src.config import settings 
import requests
from src.frontend.ui.upload_json import upload_json
from src.frontend.ui.add_test_case import add_test_case

def my_prompts():
    # Session state to track selected prompt
    if "selected_prompt" not in st.session_state:         
        st.session_state.selected_prompt = None

    if "show_tabls" not in st.session_state:
        st.session_state.show_tabs = False

    response = requests.get(f"{settings.api_url}/prompts/")      

    if response.status_code != 200:
        st.error("Failed to fetch prompts")
        return 
    
    prompts = response.json()

    # Render prompts as clickable buttons
    for prompt in prompts:
        with st.expander(f"{prompt['prompt_name']} (v: {prompt['version']})", expanded=False):
            st.session_state.show_tabs = True
            st.write(prompt['prompt_content'])
            if st.button("Add Test Cases", key=prompt['prompt_id']):
                st.session_state.selected_prompt = prompt   
                selected = st.session_state.selected_prompt
  
                if st.session_state.show_tabs:
                    tab1, tab2 = st.tabs(["Upload JSON", "Add Test Case"])
                    # TAB 1 
                    with tab1:
                        upload_json(selected)
                    # TAB 2               
                    with tab2:
                        add_test_case(selected)

