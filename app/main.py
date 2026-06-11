# app/main.py

from fastapi import FastAPI

from app.api.v1.ingestion import router as ingestion_router
from app.services.vector_store import ensure_collection_exists

app = FastAPI(
    title="RAG Backend",
    description="Document ingestion and conversational RAG API",
    version="0.1.0",
)


@app.on_event("startup")
def startup_event() -> None:
    """
    Runs once when the server starts.
    Makes sure our Qdrant collection exists before
    any requests come in.
    """
    ensure_collection_exists()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(ingestion_router, prefix="/api/v1", tags=["Ingestion"])