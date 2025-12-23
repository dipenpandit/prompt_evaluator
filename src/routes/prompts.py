from fastapi import APIRouter, Depends, status
from src.schemas import PromptIn, PromptOut, DisplayPrompt
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.db.models import Prompt, PromptVersion
from typing import List
from sqlalchemy import select

router = APIRouter(prefix="/prompts", tags=["Create Prompt"])

# POST
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

# GET
@router.get("/", response_model=List[DisplayPrompt], status_code=status.HTTP_200_OK)
async def get_prompts(db: Session = Depends(get_db)) -> List[DisplayPrompt]:
    stmt = (
        select(
            Prompt.prompt_id,
            PromptVersion.version_number,
            PromptVersion.prompt_name,
            PromptVersion.prompt_content,
            PromptVersion.status
        )
        .join(
            PromptVersion,
            Prompt.current_version_id == PromptVersion.version_id
        )
    )

    result = db.execute(stmt).all()

    prompts = [
        DisplayPrompt(
            prompt_id=row.prompt_id,
            version_number=row.version_number,
            prompt_name=row.prompt_name,
            prompt_content=row.prompt_content,
            status=row.status,
        )
        for row in result
    ]

    return prompts


