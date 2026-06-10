# app/schemas/ingestion.py

import uuid
from enum import Enum

from pydantic import BaseModel


class ChunkingStrategy(str, Enum):
    """
    The two strategies the caller can choose between.
    Using an Enum means if someone sends "random_value"
    FastAPI automatically rejects it with a clear error.
    """
    fixed = "fixed"
    recursive = "recursive"


class IngestResponse(BaseModel):
    """
    What we send back after a successful upload.
    """
    document_id: uuid.UUID
    file_name: str
    total_chunks: int
    chunking_strategy: ChunkingStrategy
    message: str