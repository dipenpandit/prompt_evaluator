from fastapi import APIRouter, Depends, status
from src.schemas import PromptIn, PromptOut
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.db.models import Prompt, PromptVersion
from typing import List


router = APIRouter(prefix="/prompts", tags=["Create Prompt"])

# Create a new Prompt Project
@router.post("/", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
async def create_prompt(prompt: PromptIn,
                       db: Session = Depends(get_db)) -> PromptOut:
    prompt_v0 = PromptVersion(**prompt.model_dump())
    db.add(prompt_v0)
    db.commit()
    db.refresh(prompt_v0)  # refresh to fetch default values properly like the timestamp 

    new_prompt = Prompt(prompt_id=prompt_v0.prompt_id, current_version_id=prompt_v0.version_id)
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return new_prompt

# Get all the existing Prompt Projects
@router.get("/", response_model=List[PromptOut], status_code=status.HTTP_200_OK)
async def get_prompts(db: Session = Depends(get_db)) -> List[PromptOut]:
    prompts = db.query(Prompt).all()
    return prompts

# Get a specific Prompt Project by ID
@router.get("/{prompt_id}", response_model=PromptOut, status_code=status.HTTP_200_OK)
async def get_prompt(prompt_id: str,
                     db: Session = Depends(get_db)) -> PromptOut:
    prompt = db.query(Prompt).filter(Prompt.prompt_id == prompt_id).first()
    return prompt


