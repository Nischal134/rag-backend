# app/services/booking_extractor.py

import json
import uuid

from groq import Groq
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import InterviewBooking

groq_client = Groq(api_key=settings.GROQ_API_KEY)


def extract_booking(
    message: str,
    session_id: str,
    db: Session,
) -> dict | None:
    """
    Checks if a message contains interview booking details.
    If yes, extracts them and saves to PostgreSQL.
    Returns the booking dict if found, None otherwise.
    """

    # ask the LLM to extract booking info as JSON
    prompt = f"""Look at this message and check if it contains all four of these:
- A person's name
- An email address  
- A date for an interview
- A time for an interview

Message: "{message}"

If ALL four are present, respond with ONLY this JSON and nothing else:
{{"name": "...", "email": "...", "date": "YYYY-MM-DD", "time": "HH:MM"}}

If anything is missing, respond with ONLY the word: null"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=100,
    )

    raw = response.choices[0].message.content.strip()

    if raw == "null" or not raw:
        return None

    # try to parse the JSON response
    try:
        # sometimes the LLM wraps it in ```json blocks despite instructions
        clean = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean)
    except json.JSONDecodeError:
        # LLM didn't return valid JSON — no booking found
        return None

    # validate all four fields exist
    required = ["name", "email", "date", "time"]
    if not all(k in data for k in required):
        return None

    # save to postgres
    try:
        from datetime import date, time
        interview_date = date.fromisoformat(data["date"])
        interview_time = time.fromisoformat(data["time"])

        booking = InterviewBooking(
            id=uuid.uuid4(),
            session_id=session_id,
            candidate_name=data["name"],
            candidate_email=data["email"],
            interview_date=interview_date,
            interview_time=interview_time,
            status="confirmed",
        )
        db.add(booking)
        db.commit()

        return data

    except Exception:
        # bad date/time format from LLM — skip saving
        return None