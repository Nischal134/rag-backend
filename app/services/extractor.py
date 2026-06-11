# app/services/extractor.py

from pypdf import PdfReader
from fastapi import UploadFile
import io


async def extract_text(file: UploadFile) -> str:
    """
    Reads raw text from an uploaded PDF or TXT file.
    Returns a single string of all the text content.
    """
    # Read the raw bytes from the uploaded file
    raw_bytes = await file.read()

    if file.filename.endswith(".pdf"):
        return _extract_from_pdf(raw_bytes)
    else:
        return _extract_from_txt(raw_bytes)


def _extract_from_pdf(raw_bytes: bytes) -> str:
    """
    Loops through every page of the PDF and
    joins all the text together with newlines.
    """
    # PdfReader needs a file-like object, not raw bytes
    # io.BytesIO wraps the bytes to behave like a file
    pdf = PdfReader(io.BytesIO(raw_bytes))

    pages_text = []
    for page in pdf.pages:
        text = page.extract_text()
        if text:  # some pages are images with no text layer
            pages_text.append(text)

    return "\n".join(pages_text)


def _extract_from_txt(raw_bytes: bytes) -> str:
    """
    Decodes raw bytes into a plain string.
    errors='ignore' silently skips any weird characters.
    """
    return raw_bytes.decode("utf-8", errors="ignore")