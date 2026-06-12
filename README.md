# RAG Backend — Document Assistant

A backend system for uploading documents and having contextual AI conversations about them. Built with FastAPI, Qdrant, PostgreSQL, Redis, and Groq LLM.

## What It Does
- Upload PDFs/TXT files → extract text → chunk → embed → store in vector DB
- Ask questions → semantic search retrieves relevant chunks → LLM answers grounded in your documents
- Multi-turn memory per session via Redis
- Automatically extracts and saves interview booking details from conversation

## Tech Stack
FastAPI · Qdrant (vector DB) · PostgreSQL (metadata) · Redis (chat memory) · sentence-transformers/all-MiniLM-L6-v2 (local embeddings) · Groq llama-3.1-8b · Streamlit (UI)

## Key Decisions
- **No LangChain** — RAG pipeline built from scratch: embed → search → prompt → LLM
- **Two chunking strategies** — Fixed (character-based) and Recursive (respects paragraph/sentence boundaries, produces cleaner embeddings)
- **Redis as plain JSON** — chat history stored as a JSON string per session key, simple and debuggable
- **Local embeddings** — no OpenAI dependency or per-request cost

## Project Structure
```
app/
├── api/v1/        # ingestion.py, chat.py
├── core/          # config.py (pydantic settings)
├── db/            # models.py, session.py, repositories/
├── services/      # extractor, chunker, embedder, vector_store,
│                  # rag_pipeline, memory, booking_extractor
├── schemas/       # pydantic request/response models
└── main.py
streamlit_app.py   # frontend UI
```

## Running Locally
```bash
python3 -m venv venv && source venv/bin/activate
pip3 install -r requirements.txt
cp .env.example .env
python3 -c "from app.db.session import engine; from app.db.models import Base; Base.metadata.create_all(bind=engine)"
uvicorn app.main:app --reload
streamlit run streamlit_app.py
```

## Environment Variables
```
DATABASE_URL      postgresql://user:password@localhost:5432/ragdb
QDRANT_URL        https://your-cluster.qdrant.io
QDRANT_API_KEY    your_key
GROQ_API_KEY      your_key
REDIS_URL         redis://localhost:6379
EMBEDDING_MODEL   all-MiniLM-L6-v2
```

## API Endpoints
`POST /api/v1/ingest` — upload PDF/TXT, returns document_id and chunk count  
`POST /api/v1/chat` — send message + session_id, returns grounded AI reply

## Known Limitations
- No auth on endpoints — demo use only
- CPU-based embeddings, slow on large documents
- Booking extraction can miss ambiguous date/time formats
