import streamlit as st
from src.config import settings 
import requests
import json

def my_prompts():
    # Session state to track selected prompt
    if "selected_prompt" not in st.session_state:         
        st.session_state.selected_prompt = None

    response = requests.get(f"{settings.api_url}/prompts/")      

    if response.status_code != 200:
        st.error("Failed to fetch prompts")
        return 
    
    prompts = response.json()

    # Render prompts as clickable buttons
    for prompt in prompts:
        with st.expander(f"{prompt['prompt_name']} (V: {prompt['version']})", expanded=False):
            if st.button("Add Test Cases", key=prompt['prompt_id']):
                st.session_state.selected_prompt = prompt   
                selected = st.session_state.selected_prompt
                tab1, tab2 = st.tabs(["Upload JSON", "Add Test Case"])

                # ================= TAB 1 =================
                with tab1:
                    uploaded_file = st.file_uploader(
                        "Upload JSON file",
                        type=["json"],
                        key=f"json_{selected['prompt_id']}"
                    )
                
                # ================= TAB 2 =================
                with tab2:
                    question = st.text_input("Question")

                    answer = st.text_area("Answer")

                    if st.button(
                        "Save Test Case",
                        key=f"save_single_{selected['prompt_id']}"
                    ):
                        if not question or not answer:
                            st.error("Both Question and Answer are required")
                        else:
                            payload = {
                                "prompt_id": selected["prompt_id"],
                                "question": question,
                                "answer": answer
                            }

                            res = requests.post(
                                f"{settings.api_url}/test-cases/",
                                json=payload
                            )

                            if res.status_code == 201:
                                st.success("Test case saved successfully ✅")

                                st.session_state[
                                    f"question_{selected['prompt_id']}"
                                ] = ""
                                st.session_state[
                                    f"answer_{selected['prompt_id']}"
                                ] = ""

                    
            
