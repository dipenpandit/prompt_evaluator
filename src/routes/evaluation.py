from fastapi import APIRouter, status, Depends, HTTPException
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.schemas import EvalOut, EvalQueryIn
from src.utils.fake_rag_api import get_ans
from src.db.models import Prompt, PromptVersion

router = APIRouter(prefix="/eval", tags=["Evaluation"])

# POST
@router.post("/{prompt_id}", response_model=EvalOut, status_code=status.HTTP_200_OK)
async def make_evaluation(prompt_id: str, query: EvalQueryIn, db: Session = Depends(get_db)):
    prompt = db.get(Prompt, prompt_id)  # Ensure prompt exists
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    current_version = db.get(PromptVersion, prompt.current_version_id) 
    
    prompt_content = current_version.prompt_content
    rag_ans = get_ans(query.query)

    # pass prompt_content, query, rag_ans to agent
    

    return EvalOut(
        prompt_id=prompt_id,
        query=query.query,
        quality= "pass"  # Placeholder response
    )