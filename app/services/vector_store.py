# app/services/vector_store.py

import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    check_compatibility=False,
)

# all-MiniLM-L6-v2 produces 384 dimensional vectors
VECTOR_SIZE = 384


def ensure_collection_exists() -> None:
    existing = [c.name for c in client.get_collections().collections]

    if settings.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"Created Qdrant collection: {settings.QDRANT_COLLECTION}")
    else:
        print(f"Qdrant collection already exists: {settings.QDRANT_COLLECTION}")


def upsert_chunks(
    chunks: list[str],
    vectors: list[list[float]],
    document_id: str,
) -> list[str]:
    """
    Stores chunk vectors in Qdrant.
    Returns a list of vector IDs — one per chunk.
    """
    points = []
    vector_ids = []

    for chunk_text, vector in zip(chunks, vectors):
        vector_id = str(uuid.uuid4())
        vector_ids.append(vector_id)

        points.append(
            PointStruct(
                id=vector_id,
                vector=vector,
                payload={
                    "chunk_text": chunk_text,
                    "document_id": document_id,
                },
            )
        )

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
    )

    return vector_ids


def search_similar_chunks(
    query_vector: list[float],
    top_k: int = 5,
) -> list[dict]:
    """
    Finds the top_k most similar chunks to the query vector.
    Used in the chat pipeline.
    """
    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
    )

    return [
        {
            "chunk_text": hit.payload["chunk_text"],
            "document_id": hit.payload["document_id"],
            "score": hit.score,
        }
        for hit in results.points
    ]