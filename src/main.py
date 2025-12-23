from fastapi import FastAPI
from src.routes import prompts, create_qa
from src.db.models import Base
from src.db.database import engine

app = FastAPI() 

Base.metadata.create_all(bind=engine)

app.include_router(prompts.router)
app.include_router(create_qa.router)

