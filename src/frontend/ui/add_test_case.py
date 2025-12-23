import streamlit as st 
import requests 
from src.config import settings

def add_test_case(selected):
    with st.form("Add a test case", clear_on_submit=False):
        question = st.text_input("Question")
        answer = st.text_area("Answer")
        submitted = st.form_submit_button("Save Test Case")

        if submitted:
            print("Submitting test case...")
            if not question or not answer:
                st.error("Both Question and Answer are required")
            else:
                payload = {
                    "question": question,
                    "answer": answer,
                    "prompt_id": selected["prompt_id"],
                }
                try:
                    response = requests.post(f"{settings.api_url}/ques_ans/",json=payload)
                    if response.status_code == 201:
                        st.success("Test case saved successfully!")
                        st.session_state.show_tabs = False

                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred: {e}")

        
            
