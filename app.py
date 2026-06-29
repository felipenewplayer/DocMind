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

logger = get_logger("app")

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH  = BASE_DIR / "data" / "vectordb"

st.set_page_config(
    page_title="AI Document Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

get_header()
side_bar()
st.markdown(get_css(), unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def ensure_vectordb():
    if not (DB_PATH / "chroma.sqlite3").exists():
        logger.info("⚙️ vectordb não encontrado, rodando ingest...")
        run_ingest()
    return True

ensure_vectordb()


def format_history(messages, limit=6):
    recent = messages[-limit:]
    lines = []
    for m in recent:
        role = "Usuário" if m["role"] == "user" else "Assistente"
        lines.append(f"{role}: {m['content']}")
    return "\n".join(lines) if lines else "Nenhuma conversa anterior."


def construir_query_retrieval(pergunta, historico):
    documentos = get_documentos_disponiveis()
    pergunta_lower = pergunta.lower()

    menciona_documento = any(doc.lower() in pergunta_lower for doc in documentos)

    if menciona_documento:
        return pergunta  # já é específica, busca direta sem ruído do histórico

    if historico and historico != "Nenhuma conversa anterior.":
        return f"{historico}\nPergunta atual: {pergunta}"
    return pergunta


def buscar_contexto_e_fontes(retriever, pergunta, historico):
    """Busca os chunks relevantes e retorna o texto de contexto + lista de fontes únicas."""
    query_busca = construir_query_retrieval(pergunta, historico)
    docs = retriever.invoke(query_busca)

    contexto = "\n\n".join(d.page_content for d in docs)

    fontes = []
    vistos = set()
    for d in docs:
        nome = Path(d.metadata.get("source", "")).stem
        if nome and nome not in vistos:
            vistos.add(nome)
            fontes.append(nome)

    return contexto, fontes


def format_documentos_disponiveis():
    docs = get_documentos_disponiveis()
    if not docs:
        return "Nenhum documento disponível no momento."
    return ", ".join(docs)


@st.cache_resource(show_spinner=False)
def load_chain():
    embeddings = load_embeddings()
    db = Chroma(persist_directory=str(DB_PATH), embedding_function=embeddings)
    llm = get_llm()
    retriever = get_retriever(db, k=5)

    chain = (
        {
            "context": lambda x: x["context"],
            "question": lambda x: x["question"],
            "chat_history": lambda x: x["chat_history"],
            "documentos_disponiveis": lambda x: format_documentos_disponiveis(),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever


rag_chain, rag_retriever = load_chain()


def typewriter_stream(chain, retriever, query, history, delay=0.01):
    historico_str = format_history(history)
    contexto, fontes = buscar_contexto_e_fontes(retriever, query, historico_str)

    input_data = {
        "question": query,
        "chat_history": historico_str,
        "context": contexto,
    }

    resposta_completa = ""
    for token in chain.stream(input_data):
        resposta_completa += token
        for char in token:
            yield char
            time.sleep(delay)

    sem_resposta = "não encontrei essa informação" in resposta_completa.lower()

    # 👇 só cita o que o LLM mencionou de fato na resposta
    fontes_citadas = [f for f in fontes if f.lower() in resposta_completa.lower()]

    if fontes_citadas and not sem_resposta:
        rodape = f"\n\n*Fonte: {', '.join(fontes_citadas)}*"
        for char in rodape:
            yield char
            time.sleep(delay)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(render_user_message(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(render_bot_message(msg["content"]), unsafe_allow_html=True)

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]
    history = st.session_state.messages[:-1]

    response = st.write_stream(
        typewriter_stream(rag_chain, rag_retriever, last_query, history)
    )

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.processando = False
    st.rerun()

processando = st.session_state.get("processando", False)

if query := st.chat_input("Pergunte algo sobre os documentos...", disabled=processando):
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.processando = True
    st.rerun()