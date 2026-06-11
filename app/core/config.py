# app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "rag_documents"
    REDIS_URL: str = "redis://localhost:6379"
    OPENAI_API_KEY: str = ""        # no longer required
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    GROQ_API_KEY: str = ""          # we'll fill this in step 9

    class Config:
        env_file = ".env"


settings = Settings()