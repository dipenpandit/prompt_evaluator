import streamlit as st
from src.config import settings 
import requests
from src.frontend.ui.view_test_cases import test_case_dialog
from src.frontend.ui.edit_prompt import edit_prompt
# from src.frontend.ui.run_eval import run_evaluation

def my_prompts():
    if "selected_prompt" not in st.session_state:
        st.session_state.selected_prompt = None
    
    if "run_evaluation" not in st.session_state:
        st.session_state.run_evaluation = None

    response = requests.get(f"{settings.api_url}/prompts/")
    if response.status_code != 200:
        st.error("Failed to fetch prompts")
        return

    prompts = response.json()

    for prompt in prompts:
        with st.expander(f"{prompt['prompt_name']} (v: {prompt['version_number']})"):
            st.write(prompt['prompt_content'])

            if st.button(
                "Edit Prompt",
                key=f"edit_{prompt['prompt_id']}"
            ):
                st.session_state.selected_prompt = prompt

            if st.button(
                "Run Evaluation",
                key=f"eval_{prompt['prompt_id']}"
            ):
                st.session_state.run_evaluation = prompt

            if st.button(
                "Test Cases",
                key=f"test_{prompt['prompt_id']}"
            ):
                test_case_dialog(prompt['prompt_id'])

    # edit prompt func
    if st.session_state.selected_prompt:
        edit_prompt()

    # run test cases func
    # if st.session_state.run_evaluation:
    #     run_evaluation()


    