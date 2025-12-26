from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings):
    db: str
    db_host: str 
    db_user: str 
    db_password: str 
    api_url: str = "http://localhost:8000"  
    openrouter_api_key: str
    openrouter_url: str
    llm: str = "gpt-4o-mini" 
    rag_api: str = "http://localhost:8001/rag"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
