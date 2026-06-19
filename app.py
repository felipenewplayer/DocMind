import os
import time

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from src.ingest.ingest import main as run_ingest
from pathlib import Path
from src.prompt.prompt_template import rag_prompt
from styles import get_css, render_bot_message, render_header, render_user_message
from logs.logs_config import get_logger

# ---- Log -------------------------------------------------
logger = get_logger("app")
# ───  Configuração ─────────────────────────────────────────
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH  = BASE_DIR / "src" / "vectordb"

@st.cache_resource
def ensure_vectordb():
    if not (DB_PATH / "chroma.sqlite3").exists():
        logger.info("⚙️ vectordb não encontrado, rodando ingest...")
        run_ingest()
    return True

ensure_vectordb()

# ─── Formata histórico para o prompt ──────────────────────
def format_history(messages, limit=6):
    recent = messages[-limit:]
    lines = []
    for m in recent:
        role = "Usuário" if m["role"] == "user" else "Assistente"
        lines.append(f"{role}: {m['content']}")
    return "\n".join(lines) if lines else "Nenhuma conversa anterior."

# ─── Typewriter ───────────────────────────────────────────
def typewriter_stream(chain, query, history, delay=0.01):
    input_data = {
        "question": query,
        "chat_history": format_history(history)
    }
    for token in chain.stream(input_data):
        for char in token:
            yield char
            time.sleep(delay)

# ─── Config ──────────────────────────────────────────────
DOCUMENTS = ["manual_produtos", "relatorio_mensal", "vendas_maio2026"]

st.set_page_config(
    page_title="AI Document Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(get_css(), unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Administração")
    st.divider()
    st.markdown("**Documentos indexados:**")
    for doc in DOCUMENTS:
        st.markdown(f"📄 {doc}")
    st.divider()
    if st.button("🔄 Reindexar documentos"):
        with st.spinner("Reindexando..."):
            run_ingest()
            st.cache_resource.clear()
        st.success("✅ Documentos reindexados com sucesso!")
        st.rerun()

# ─── Pipeline RAG ────────────────────────────────────────
@st.cache_resource
def load_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(persist_directory=str(DB_PATH), embedding_function=embeddings)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    retriever = db.as_retriever(search_kwargs={"k": 10})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    return (
        {
            "context": (lambda x: x["question"]) | retriever | format_docs,
            "question": lambda x: x["question"],
            "chat_history": lambda x: x["chat_history"],
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

rag_chain = load_chain()

# ─── Estado ───────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Header ───────────────────────────────────────────────
title, subtitle = render_header(DOCUMENTS)
st.markdown(title, unsafe_allow_html=True)
st.markdown(subtitle, unsafe_allow_html=True)

# ─── Histórico ────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(render_user_message(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(render_bot_message(msg["content"]), unsafe_allow_html=True)

# ─── Streaming ────────────────────────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]
    history = st.session_state.messages[:-1]

    response = st.write_stream(typewriter_stream(rag_chain, last_query, history))

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ─── Input ────────────────────────────────────────────────
if query := st.chat_input("Pergunte algo sobre os documentos..."):
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()