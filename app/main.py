# app/main.py

from fastapi import FastAPI

from app.api.v1.ingestion import router as ingestion_router

app = FastAPI(
    title="RAG Backend",
    description="Document ingestion and conversational RAG API",
    version="0.1.0",
)

# Health check
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

# Register the ingestion routes under /api/v1
app.include_router(ingestion_router, prefix="/api/v1", tags=["Ingestion"])