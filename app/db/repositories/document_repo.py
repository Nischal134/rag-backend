# app/db/repositories/document_repo.py

import uuid
from sqlalchemy.orm import Session
from app.db.models import Document, Chunk


def create_document(
    db: Session,
    file_name: str,
    file_type: str,
    storage_path: str,
    chunking_strategy: str,
) -> Document:
    # create a new document row
    doc = Document(
        id=uuid.uuid4(),
        file_name=file_name,
        file_type=file_type,
        storage_path=storage_path,
        chunking_strategy=chunking_strategy,
        status="processing",
        total_chunks=0,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def save_chunks(
    db: Session,
    document_id: uuid.UUID,
    chunks: list[str],
    vector_ids: list[str],
    chunking_strategy: str,
) -> None:
    # bulk insert all chunks for this document
    # not the most optimized way but works fine for now
    for index, (chunk_text, vector_id) in enumerate(zip(chunks, vector_ids)):
        chunk = Chunk(
            id=uuid.uuid4(),
            document_id=document_id,
            chunk_text=chunk_text,
            chunk_index=index,
            chunk_size=len(chunk_text),
            qdrant_vector_id=vector_id,
            chunking_strategy=chunking_strategy,
        )
        db.add(chunk)

    db.commit()


def mark_document_complete(
    db: Session,
    document_id: uuid.UUID,
    total_chunks: int,
) -> None:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc:
        doc.status = "complete"
        doc.total_chunks = total_chunks
        db.commit()