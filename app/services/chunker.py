# app/services/chunker.py

from app.schemas.ingestion import ChunkingStrategy


def chunk_text(
    text: str,
    strategy: ChunkingStrategy,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Splits a long string into overlapping chunks.
    Returns a list of strings — one per chunk.
    """
    if strategy == ChunkingStrategy.fixed:
        return _fixed_chunking(text, chunk_size, overlap)
    else:
        return _recursive_chunking(text, chunk_size, overlap)


def _fixed_chunking(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """
    Slides a window of chunk_size characters across the text.
    Each step moves forward by (chunk_size - overlap) characters.
    Simple, predictable, ignores sentence boundaries.
    """
    chunks = []
    step = chunk_size - overlap
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def _recursive_chunking(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """
    Tries to split on natural boundaries in this order:
    1. Double newlines  (paragraph breaks)
    2. Single newlines  (line breaks)
    3. Periods          (sentence endings)
    4. Spaces           (word boundaries)
    5. Characters       (last resort — same as fixed)

    If a split produces a piece still larger than chunk_size,
    it recurses and tries the next separator down the list.
    """
    separators = ["\n\n", "\n", ". ", " ", ""]
    return _split_recursive(text, chunk_size, overlap, separators)


def _split_recursive(
    text: str,
    chunk_size: int,
    overlap: int,
    separators: list[str],
) -> list[str]:
    # Base case — text fits in one chunk, just return it
    if len(text) <= chunk_size:
        stripped = text.strip()
        return [stripped] if stripped else []

    # Try each separator in order
    separator = separators[0]
    remaining_separators = separators[1:]

    if separator == "":
        # Last resort — fall back to fixed chunking
        return _fixed_chunking(text, chunk_size, overlap)

    parts = text.split(separator)

    chunks = []
    current = ""

    for part in parts:
        candidate = current + separator + part if current else part

        if len(candidate) <= chunk_size:
            # Still fits — keep building
            current = candidate
        else:
            # Doesn't fit — save what we have
            if current.strip():
                chunks.append(current.strip())

            # Is this single part still too big?
            if len(part) > chunk_size:
                # Recurse with the next separator down
                sub_chunks = _split_recursive(
                    part, chunk_size, overlap, remaining_separators
                )
                chunks.extend(sub_chunks)
                current = ""
            else:
                current = part

    # Don't forget the last piece
    if current.strip():
        chunks.append(current.strip())

    # Add overlap — take the tail of each chunk and
    # prepend it to the next one
    if overlap > 0 and len(chunks) > 1:
        chunks = _apply_overlap(chunks, overlap)

    return chunks


def _apply_overlap(chunks: list[str], overlap: int) -> list[str]:
    """
    Takes the last `overlap` characters of each chunk
    and prepends them to the next chunk.
    """
    overlapped = [chunks[0]]

    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-overlap:]
        overlapped.append(tail + " " + chunks[i])

    return overlapped