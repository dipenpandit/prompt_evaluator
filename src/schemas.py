from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Literal

class PromptIn(BaseModel):
    prompt_name: str
    prompt_content: str

class EditPromptIn(BaseModel):
    prompt_content: str   
    status: str = "inactive"

class FixPromptIn(BaseModel):
    prompt_content: str 
    status: str = "active"

class EvalCaseIn(BaseModel):
    query: str
    correct_answer: str

class EvalOut(BaseModel):
    prompt_id: UUID
    quality: Literal["pass", "fail"]

class PromptOut(BaseModel):
    prompt_id: UUID
    prompt_name: str
    current_version_id: UUID

    model_config = ConfigDict(from_attributes=True)

class DisplayPrompt(BaseModel):
    prompt_id: UUID
    version_number: int
    prompt_name: str
    prompt_content: str
    status: str

class TestCaseIn(BaseModel):
    question: str
    answer: str
    prompt_id: UUID 

class TestCaseOut(BaseModel):
    test_id: UUID
    question: str
    answer: str
    prompt_id: UUID 

    model_config = ConfigDict(from_attributes=True)
 
class EvaluationScore(BaseModel):
    faithfulness: float
    context_relevancy: float
    answer_relevancy: float

class AgentResponse(BaseModel):
    quality: Literal["pass", "fail"]

