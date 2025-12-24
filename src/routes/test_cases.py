from fastapi import APIRouter, Depends, status
from src.schemas import TestCaseIn, TestCaseOut
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import TestCase
from uuid import UUID
from sqlalchemy import select

router = APIRouter(prefix="/test_cases", tags=["Test Cases"])

# GET 
@router.get("/", response_model=list[TestCaseOut], status_code=status.HTTP_200_OK)
async def get_test_cases(db: Session = Depends(get_db)) -> list[TestCaseOut]:
    stmt = select(TestCase)
    result = db.execute(stmt).scalars().all()
    return result

# GET by prompt_id
@router.get("/{prompt_id}", response_model=list[TestCaseOut], status_code=status.HTTP_200_OK)
async def get_test_cases_by_id(prompt_id: UUID, db: Session = Depends(get_db)) -> list[TestCaseOut]:
    stmt = select(TestCase).where(TestCase.prompt_id == prompt_id)
    result = db.execute(stmt).scalars().all()
    return result

# POST
@router.post("/", response_model=TestCaseOut, status_code=status.HTTP_201_CREATED)
async def create_test_case(qa: TestCaseIn,
                    db: Session = Depends(get_db)) -> TestCaseOut:
    new_qa = TestCase(**qa.model_dump())
    db.add(new_qa)
    db.commit()
    db.refresh(new_qa)  
    return new_qa

