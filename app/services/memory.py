# app/services/memory.py

import json
import redis

from app.core.config import settings

# one shared connection
client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# how long to keep chat history — 2 hours
TTL_SECONDS = 60 * 60 * 2


def get_history(session_id: str) -> list[dict]:
    """
    Fetches chat history for a session.
    Returns empty list if session doesn't exist yet.
    History is a list of dicts like:
    [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    """
    raw = client.get(session_id)
    if not raw:
        return []
    return json.loads(raw)


def save_history(session_id: str, history: list[dict]) -> None:
    """
    Saves updated history back to Redis as a JSON string.
    Resets the expiry timer on every save.
    """
    client.setex(
        name=session_id,
        time=TTL_SECONDS,
        value=json.dumps(history),
    )


def add_turn(session_id: str, user_message: str, assistant_reply: str) -> None:
    """
    Convenience function — adds one full conversation turn.
    Keeps only the last 10 turns to avoid huge prompts.
    """
    history = get_history(session_id)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": assistant_reply})

    # only keep last 10 turns (20 messages)
    if len(history) > 20:
        history = history[-20:]

    save_history(session_id, history)


def clear_history(session_id: str) -> None:
    """Wipes the session. Useful for testing."""
    client.delete(session_id)