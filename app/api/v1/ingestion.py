# app/api/v1/ingestion.py

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.params import Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.repositories.document_repo import (
    create_document,
    mark_document_complete,
    save_chunks,
)
from app.schemas.ingestion import ChunkingStrategy, IngestResponse
from app.services.chunker import chunk_text
from app.services.embedder import generate_embeddings
from app.services.extractor import extract_text
from app.services.vector_store import upsert_chunks

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "txt"}


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkingStrategy = Form(ChunkingStrategy.recursive),
    db: Session = Depends(get_db),
) -> IngestResponse:
    """
    Full ingestion pipeline:
    extract → chunk → embed → store vectors → save metadata
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    extension = get_file_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{extension}' not supported. Use PDF or TXT."
        )

    # step 1 - pull text out of the file
    raw_text = await extract_text(file)

    if not raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from this file."
        )

    # step 2 - cut into chunks
    chunks = chunk_text(raw_text, chunking_strategy)

    # step 3 - save document record first so we have an ID
    # storage_path is just the filename for now
    # TODO: wire up actual file storage (S3 etc) later
    doc = create_document(
        db=db,
        file_name=file.filename,
        file_type=extension,
        storage_path=file.filename,
        chunking_strategy=chunking_strategy.value,
    )

    # step 4 - generate embeddings for all chunks at once
    vectors = generate_embeddings(chunks)

    # step 5 - push vectors to qdrant
    vector_ids = upsert_chunks(
        chunks=chunks,
        vectors=vectors,
        document_id=str(doc.id),
    )

    # step 6 - save chunks to postgres
    save_chunks(
        db=db,
        document_id=doc.id,
        chunks=chunks,
        vector_ids=vector_ids,
        chunking_strategy=chunking_strategy.value,
    )

    # step 7 - mark document as done
    mark_document_complete(db, doc.id, len(chunks))

    return IngestResponse(
        document_id=doc.id,
        file_name=file.filename,
        total_chunks=len(chunks),
        chunking_strategy=chunking_strategy,
        message="Document ingested successfully.",
    )