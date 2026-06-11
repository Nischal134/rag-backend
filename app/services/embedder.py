# app/services/embedder.py

from sentence_transformers import SentenceTransformer

# loads the model once when the app starts
# first run downloads it (~90MB), after that it's cached
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Takes a list of text chunks.
    Returns a list of vectors — one vector per chunk.
    Runs locally, no API key needed.
    """
    embeddings = model.encode(chunks, show_progress_bar=False)
    return embeddings.tolist()


def generate_single_embedding(text: str) -> list[float]:
    """
    Embeds a single string.
    Used when embedding the user's search query.
    """
    return generate_embeddings([text])[0]