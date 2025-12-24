import streamlit as st
import requests
from src.config import settings
from src.frontend.ui.view_test_cases import test_case_dialog

# FORM IS RENDERED SEPARATELY
def run_evaluatioin():
    selected = st.session_state.run_evaluation
    
    st.subheader(f"Evaluating: {selected['prompt_name']}")

    st.subheader("Test Cases")
    test_case_dialog(selected['prompt_id'])

    with st.form(key="Add test cases form"):
        new_content = st.text_area(
            "Prompt Content",
            value=selected["prompt_content"]
        )
        submit = st.form_submit_button("Update Prompt")

    if submit:
        if not new_content.strip():
            st.error("Prompt content cannot be empty.")
        else:
            update_response = requests.put(
                f"{settings.api_url}/prompts/{selected['prompt_id']}",
                json={"prompt_content": new_content},
            )

            if update_response.status_code == 200:
                st.success("Prompt updated successfully.")
                st.session_state.selected_prompt = None
                st.rerun()
            else:
                st.error(update_response.text)
