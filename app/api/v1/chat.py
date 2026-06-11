# app/api/v1/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.booking_extractor import extract_booking
from app.services.rag_pipeline import run_rag_pipeline

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Conversational RAG endpoint with automatic booking detection.
    Uses the same session_id to maintain conversation memory.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if not request.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id cannot be empty.")

    # check for booking info before running RAG
    booking = extract_booking(
        message=request.message,
        session_id=request.session_id,
        db=db,
    )

    # run the main RAG pipeline regardless
    reply = run_rag_pipeline(
        session_id=request.session_id,
        user_message=request.message,
    )

    # if a booking was found, acknowledge it in the reply
    if booking:
        reply = f"I've booked your interview! Details saved:\n- Name: {booking['name']}\n- Email: {booking['email']}\n- Date: {booking['date']}\n- Time: {booking['time']}\n\n{reply}"

    return ChatResponse(
        session_id=request.session_id,
        reply=reply,
        sources_used=3,
    )