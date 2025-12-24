import streamlit as st
import requests
from src.config import settings

# FORM IS RENDERED SEPARATELY
def edit_prompt():
    selected = st.session_state.selected_prompt
    st.subheader(f"Editing: {selected['prompt_name']}")

    with st.form(key="edit_prompt_form"):
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
