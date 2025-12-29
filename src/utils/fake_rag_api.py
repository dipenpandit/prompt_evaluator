from fastapi import APIRouter, FastAPI
import json
from random import choice
import uvicorn
from pydantic import BaseModel 
import os

class RagRequest(BaseModel):
    query: str

class RaqResponse(BaseModel):
    answer: str
    context: str

file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'rag_responses.json')

app = FastAPI()

@app.post("/rag/", response_model=RaqResponse)
async def search_rag(query: RagRequest):
    with open(file_path, "r") as file:
        responses = json.load(file).get("responses", [])
    for resp in responses:
        if resp.get("question") == query.query:
            select = choice(["correct", "vague", "incorrect"])
            if select == "correct":
                ans = resp.get("correct", "")
            elif select == "vague":
                ans = resp.get("vague", "")      
            else:
                ans = resp.get("incorrect", "")   
            context = resp.get("context", "")
            return RaqResponse(answer=ans, context=context)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001) 
