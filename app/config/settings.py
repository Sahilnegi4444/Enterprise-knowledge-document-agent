import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str = "mock_groq_api_key"
    FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    PLANNER_MODEL: str = "llama-3.1-8b-instant"
    GENERATOR_MODEL: str = "llama-3.3-70b-versatile"
    REFLECTION_MODEL: str = "llama-3.1-8b-instant"
    TAVILY_API_KEY: Optional[str] = None
    
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DB_DIR: str = "./data/chroma"
    RAG_TOP_K: int = 3
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    TEMPERATURE: float = 0.2
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
