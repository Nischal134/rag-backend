# streamlit_app.py

import streamlit as st
import requests
import uuid

# your FastAPI backend URL
API_URL = "http://localhost:8000"

# page config — must be first streamlit call
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="🤖",
    layout="wide",
)

# generate a session ID once per browser session
# this is how we maintain chat memory across messages
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# store chat messages for display
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── sidebar navigation ──────────────────────────────────────
with st.sidebar:
    st.title("🤖 RAG Assistant")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["📄 Upload Document", "💬 Chat"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"Session: {st.session_state.session_id[:8]}...")


# ── page 1: upload document ──────────────────────────────────
if page == "📄 Upload Document":
    st.title("📄 Upload Document")
    st.markdown("Upload a PDF or TXT file to add it to the knowledge base.")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt"],
        help="Supported formats: PDF, TXT",
    )

    chunking_strategy = st.selectbox(
        "Chunking Strategy",
        options=["recursive", "fixed"],
        help="Recursive respects sentence boundaries. Fixed splits by character count.",
    )

    if st.button("Upload", type="primary", disabled=uploaded_file is None):
        with st.spinner("Processing document..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/ingest",
                    files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                    data={"chunking_strategy": chunking_strategy},
                    timeout=60,
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("Document uploaded successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("File", result["file_name"])
                    col2.metric("Chunks Created", result["total_chunks"])
                    col3.metric("Strategy", result["chunking_strategy"])
                else:
                    st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Is the FastAPI server running?")


# ── page 2: chat ─────────────────────────────────────────────
elif page == "💬 Chat":
    st.title("💬 Chat with your Documents")

    # display existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # chat input box — appears at the bottom
    user_input = st.chat_input("Ask a question about your documents...")

    if user_input:
        # show user message immediately
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # call the backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/v1/chat",
                        json={
                            "session_id": st.session_state.session_id,
                            "message": user_input,
                        },
                        timeout=30,
                    )

                    if response.status_code == 200:
                        reply = response.json()["reply"]
                        st.markdown(reply)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": reply,
                        })
                    else:
                        st.error("Backend returned an error. Check the FastAPI server.")

                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Is the FastAPI server running?")