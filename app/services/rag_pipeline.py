# app/services/rag_pipeline.py

from groq import Groq

from app.core.config import settings
from app.services.embedder import generate_single_embedding
from app.services.memory import add_turn, get_history
from app.services.vector_store import search_similar_chunks

# one shared groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)

GROQ_MODEL = "llama-3.1-8b-instant"


def build_prompt(
    user_message: str,
    context_chunks: list[dict],
    chat_history: list[dict],
) -> list[dict]:
    """
    Combines retrieved context, chat history, and user message
    into a list of messages for the LLM.
    """
    if context_chunks:
        context_text = "\n\n".join(
            f"[Chunk {i+1}]: {chunk['chunk_text']}"
            for i, chunk in enumerate(context_chunks)
        )
    else:
        context_text = "No relevant context found."

    system_message = f"""You are a helpful assistant that answers questions based on the provided document context.
Use the context below to answer the user's question. If the answer isn't in the context, say so honestly.

CONTEXT:
{context_text}
"""

    messages = [{"role": "system", "content": system_message}]

    # add previous chat turns so the LLM has memory
    messages.extend(chat_history)

    # add current question
    messages.append({"role": "user", "content": user_message})

    return messages


def run_rag_pipeline(session_id: str, user_message: str) -> str:
    """
    Main function — takes a session ID and user message,
    returns the assistant's reply.
    """
    # step 1 - embed the question
    query_vector = generate_single_embedding(user_message)

    # step 2 - find relevant chunks from qdrant
    context_chunks = search_similar_chunks(query_vector, top_k=3)

    # step 3 - get chat history from redis
    chat_history = get_history(session_id)

    # step 4 - build the prompt
    messages = build_prompt(user_message, context_chunks, chat_history)

    # step 5 - call the LLM
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )

    assistant_reply = response.choices[0].message.content

    # step 6 - save this turn to redis
    add_turn(session_id, user_message, assistant_reply)

    return assistant_reply