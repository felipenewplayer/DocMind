import time
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings

from logs.logs_config import get_logger
from src.llm.llm import get_llm
from src.ingest.ingest import main as run_ingest
from src.prompt.prompt_template import rag_prompt
from src.retrieval.retriever import get_retriever, get_documentos_disponiveis
from src.app.header import get_header
from src.app.side_bar import side_bar

from styles import get_css, render_bot_message, render_user_message

logger = get_logger("app")

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "vectordb"

DOCUMENTS = ["manual_produtos", "relatorio_mensal", "vendas_maio2026"]

st.set_page_config(
    page_title="AI Document Chatbot",
    page_icon="🤖",
    layout="centered"
)

get_header(DOCUMENTS)
side_bar()

st.markdown(get_css(), unsafe_allow_html=True)


# ─── INICIALIZA VECTOR DB ────────────────────────────────
@st.cache_resource
def ensure_vectordb():
    if not (DB_PATH / "chroma.sqlite3").exists():
        logger.info("⚙️ VectorDB não encontrado, rodando ingest...")
        run_ingest()
    return True


ensure_vectordb()


# ─── HISTÓRICO ───────────────────────────────────────────
def format_history(messages, limit=6):
    recent = messages[-limit:]

    lines = []
    for m in recent:
        role = "Usuário" if m["role"] == "user" else "Assistente"
        lines.append(f"{role}: {m['content']}")

    return "\n".join(lines) if lines else "Nenhuma conversa anterior."


# ─── CHAIN ───────────────────────────────────────────────
@st.cache_resource
def load_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(
        persist_directory=str(DB_PATH),
        embedding_function=embeddings
    )

    retriever = get_retriever(db, k=20)
    llm = get_llm()

    def retrieve_and_format(x):
        query = x["question"]

        docs = retriever.invoke(query)

        # 🔥 DEBUG IMPORTANTE
        logger.info("\n🔎 CHUNKS RECUPERADOS:")
        for i, d in enumerate(docs):
            logger.info(f"\n--- {i} ---")
            logger.info(d.page_content[:500])

        return "\n\n".join(d.page_content for d in docs)


    return (
        {
            "context": retrieve_and_format,
            "question": lambda x: x["question"],
            "chat_history": lambda x: x["chat_history"],
            "documentos_disponiveis":lambda x: get_documentos_disponiveis(db)
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )


rag_chain = load_chain()


# ─── STREAM CHAT ─────────────────────────────────────────
def typewriter_stream(chain, query, history, delay=0.01):
    input_data = {
        "question": query,
        "chat_history": format_history(history)
    }

    for token in chain.stream(input_data):
        for char in token:
            yield char
            time.sleep(delay)


# ─── STATE ───────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []


# ─── RENDER HISTORY ───────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(render_user_message(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(render_bot_message(msg["content"]), unsafe_allow_html=True)


# ─── RESPONSE FLOW ───────────────────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]
    history = st.session_state.messages[:-1]

    response = st.write_stream(
        typewriter_stream(rag_chain, last_query, history)
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()


# ─── INPUT ───────────────────────────────────────────────
if query := st.chat_input("Pergunte algo sobre os documentos..."):
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()