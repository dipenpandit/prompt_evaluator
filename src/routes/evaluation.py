from fastapi import APIRouter, status, Depends, HTTPException
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.schemas import EvalOut, EvalCaseIn
from src.db.models import Prompt, PromptVersion
from src.config import settings
from src.evaluator.agent import EvaluatorAgent, agent
import requests 


router = APIRouter(prefix="/eval", tags=["Evaluation"])

# POST
@router.post("/{prompt_id}", response_model=EvalOut, status_code=status.HTTP_200_OK)
async def make_evaluation(prompt_id: str,
                          query: EvalCaseIn, 
                          db: Session = Depends(get_db),
                          agent: EvaluatorAgent = Depends(lambda: agent)):
    prompt = db.get(Prompt, prompt_id)  # Ensure prompt exists
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    current_version = db.get(PromptVersion, prompt.current_version_id) 
    
    rag_response = requests.post(
        f"{settings.rag_api}", json={"query": query.query})
    
    if rag_response.status_code != 200:
        raise HTTPException(status_code=500, detail="RAG API error, check your api url and server status")
    
    rag_data = rag_response.json()

    prompt_content = current_version.prompt_content
    rag_ans = rag_data.get("answer", "")
    rag_context = rag_data.get("context", "")
    correct_answer = query.correct_answer

    # pass prompt_content, query, rag_ans to agent
    agent.evaluate(
        prompt_content=prompt_content,
        query=query.query,
        rag_ans=rag_ans,
        correct_answer=correct_answer,
        context=rag_context
    )
    
    return EvalOut(
        prompt_id=prompt_id,
        query=query.query,
        quality= "pass"  # Placeholder response
    )