# app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Reads every value automatically from the .env file.
    If a required key is missing, the app will refuse to start
    and tell you exactly which key is missing.
    """

    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "rag_documents"
    REDIS_URL: str = "redis://localhost:6379"
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"


# This creates one shared instance the whole app imports.
# Every other file will do: from app.core.config import settings
settings = Settings()