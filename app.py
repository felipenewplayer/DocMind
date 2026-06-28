import time
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser

from logs.logs_config import get_logger
from src.llm.llm import get_llm
from src.ingest.ingest import main as run_ingest
from src.prompt.prompt_template import rag_prompt
from src.retrieval.retriever import get_retriever
from src.app.header import get_header
from src.app.side_bar import side_bar
from src.vectordb.vector_manager import get_documentos_disponiveis
from src.embeddings.embeddings import load_embeddings
from styles import get_css, render_bot_message, render_user_message

# ---- Log -------------------------------------------------
logger = get_logger("app")

# ───  Configuração ────────────────────────────────────────
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH  = BASE_DIR / "data" / "vectordb"

st.set_page_config(
    page_title="AI Document Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)
# ─── Header ───────────────────────────────────────────────
get_header()

# ─── Sidebar ─────────────────────────────────────────────
side_bar()

st.markdown(get_css(), unsafe_allow_html=True)

# ---- Criando o banco de dados no huggingface ───────────────
@st.cache_resource(show_spinner=False)
def ensure_vectordb():
    if not (DB_PATH / "chroma.sqlite3").exists():
        logger.info("⚙️ vectordb não encontrado, rodando ingest...")
        run_ingest()
    return True

ensure_vectordb()

# ─── Formata histórico para o prompt ──────────────────────
def format_history(messages, limit=6):
    recent = messages[-limit:]
    lines= []
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

# ─── Pipeline RAG ────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_chain():
    embeddings = load_embeddings()
    db = Chroma(persist_directory=str(DB_PATH), embedding_function=embeddings)
    llm = get_llm()
    retriever = get_retriever(db, k=5)
    
    def format_context(docs):
     return "\n\n".join(d.page_content for d in docs)

    def format_documentos_disponiveis():
     docs = get_documentos_disponiveis()
     if not docs:
        return "Nenhum documento disponível no momento."
     return ", ".join(docs)

    def construir_query_retrieval(x):
        pergunta = x["question"]
        historico = x["chat_history"]
    
        if historico and historico != "Nenhuma conversa anterior.":
         return f"{historico}\nPergunta atual: {pergunta}"
        return pergunta
    
    return (
    {
        "context": construir_query_retrieval | retriever | format_context,
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["chat_history"],
        "documentos_disponiveis": lambda x: format_documentos_disponiveis(),
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

rag_chain = load_chain()

# ─── Estado ───────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

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