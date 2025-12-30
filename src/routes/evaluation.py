from fastapi import APIRouter, status, Depends, HTTPException
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.schemas import TestCaseIn, TestResultIn, EvaluationAPIOut, EditPromptIn
from src.db.models import Prompt, PromptVersion, TestCase, TestResults
from src.config import settings
from src.evaluator.agent import EvaluatorAgent, agent
from src.services.update_prompt import update_prompt_version, set_prompt_active
from src.services.add_test_case import add_result
from uuid import UUID
import requests 
import re
import json

router = APIRouter(prefix="/eval", tags=["Evaluation"])

# POST
@router.post("/version/{prompt_version_id}/test_case/{t_id}", response_model=EvaluationAPIOut, status_code=status.HTTP_200_OK)
async def make_evaluation(prompt_version_id: UUID,
                          t_id: UUID,
                          db: Session = Depends(get_db),
                          agent: EvaluatorAgent = Depends(lambda: agent)): 
    """Evaluate the prompt based on the retrieved answer and context from RAG and update the prompt content if necessary (quality: bad)
       1. Get the prompt content from the database
       2. Call RAG API with the provided query
       3. Pass prompt_content, query, rag_ans, correct_answer, context to agent to evaluate the prompt
       4. If the quality is "fail" and a fixed prompt_content is provided, update the prompt in the database and set it active
       5. If the quality is "pass", set the prompt status to active"""
    
    # Get the the target version and it's prompt id from db
    target_version = db.get(PromptVersion, prompt_version_id)  
    if not target_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt version not found")
    
    prompt_content = target_version.prompt_content

    prompt = db.get(Prompt, target_version.prompt_id) 
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    
    # Get the test case details
    test_case = db.get(TestCase, t_id)
    if not test_case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")

    # Call RAG API
    rag_response = requests.post(f"{settings.rag_api}", json={"query": test_case.question})
    
    if rag_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RAG API error, check your api url and server status")
    
    rag_data = rag_response.json()

    # Context for agent to evaluate prompt
    rag_ans = rag_data.get("answer", "")
    rag_context = rag_data.get("context", "")
    correct_answer = test_case.answer

    ### Agent Evaluation: Replace with OpenAI's prompt optimizer
    # Pass prompt_content, query, rag_ans, correct_answer, context to agent
    agent_result = agent.evaluate(
        prompt_content=prompt_content,
        query=test_case.question,
        rag_ans=rag_ans,
        correct_answer=correct_answer,
        context=rag_context
    )

    if not agent_result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Evaluator Agent failed to provide a response.")
        
    # Parse the agent response to extract JSON
    match = re.search(r'\{.*\}', agent_result)
    if match:
        json_str = match.group(0)  # still a string
        agent_json = json.loads(json_str) # convert to dictionary


    # FAIL CASE: Add the updated prompt to the databse with status active and set the current version in prompts table to the new version
    if agent_json.get("quality") == "fail":
       new_prompt_content = EditPromptIn(prompt_content=agent_json.get("prompt_content"))
       # 1. Creates a new prompt version and updates the prompt_id to point to it
       update_prompt_version(prompt, new_prompt_content, db)
       
       # 2. Set the new version (latest version) to active
       updated_prompt_details = set_prompt_active(prompt_version_id, db)

    # PASS CASE: Set the status flag to active in prompt_versions table for the passed prompt
    elif agent_json.get("quality") == "pass":
        updated_prompt_details = set_prompt_active(prompt_version_id, db)

    # Save the test result with reason
    test_result = add_result(TestResultIn(
        test_id=t_id,
        prompt_version_id=prompt_version_id,
        result=agent_json.get("quality"),
        reason=agent_json.get("reason")
        ), db)

    return EvaluationAPIOut(
        test_id=t_id,
        prompt_id = prompt.prompt_id,
        prompt_version_id=prompt_version_id,
        result=test_result.result,
        reason=test_result.reason,
        new_prompt_content=agent_json.get("prompt_content") if agent_json.get("quality") == "fail" else None  # change this logic
    )


