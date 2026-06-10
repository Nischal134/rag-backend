# app/api/v1/ingestion.py

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.params import Form

from app.schemas.ingestion import ChunkingStrategy, IngestResponse

# A router is like a mini-app — it holds a group of related endpoints.
# We'll register it with the main app in main.py.
router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "txt"}


def get_file_extension(filename: str) -> str:
    """Extracts the extension from a filename."""
    return filename.rsplit(".", 1)[-1].lower()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkingStrategy = Form(ChunkingStrategy.recursive),
) -> IngestResponse:
    """
    Accepts a PDF or TXT file and a chunking strategy choice.
    Validates the file type and returns a confirmation.
    Full processing pipeline will be wired in later steps.
    """
    # Validate the file has a name
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # Validate the file type
    extension = get_file_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{extension}' not supported. Use PDF or TXT."
        )

    # Placeholder response — real processing comes in Step 4 onwards
    import uuid
    return IngestResponse(
        document_id=uuid.uuid4(),
        file_name=file.filename,
        total_chunks=0,
        chunking_strategy=chunking_strategy,
        message="File received successfully. Processing pipeline coming soon."
    )