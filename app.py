import streamlit as st
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from prompt import prompt

st.set_page_config(
    page_title="AI Document Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─── CSS estilo ChatGPT ───────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #212121;
        color: #ececec;
    }

    header, footer { visibility: hidden; }

    .chat-container {
        max-width: 750px;
        margin: 0 auto;
        padding-bottom: 120px;
    }

    .msg-user {
        background-color: #2f2f2f;
        border-radius: 16px;
        padding: 12px 18px;
        margin: 8px 0 8px 80px;
        color: #ececec;
        font-size: 15px;
        line-height: 1.6;
    }

    .msg-bot {
        background-color: #212121;
        border-radius: 16px;
        padding: 12px 18px;
        margin: 8px 80px 8px 0;
        color: #ececec;
        font-size: 15px;
        line-height: 1.6;
    }

    .msg-label {
        font-size: 11px;
        color: #8e8ea0;
        margin-bottom: 4px;
        margin-left: 4px;
    }

    .stChatInput textarea {
        background-color: #2f2f2f !important;
        color: #ececec !important;
        border: 1px solid #3f3f3f !important;
        border-radius: 12px !important;
        font-size: 15px !important;
    }

    .chat-title {
        text-align: center;
        color: #ececec;
        font-size: 22px;
        font-weight: 600;
        padding: 32px 0 8px;
    }

    .chat-subtitle {
        text-align: center;
        color: #8e8ea0;
        font-size: 13px;
        margin-bottom: 32px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Carrega o pipeline RAG ───────────────────────────────
@st.cache_resource
def load_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(
        persist_directory="db",
        embedding_function=embeddings
    )
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.5,
        api_key=os.environ.get("GROQ_API_KEY")
    )
    retriever = db.as_retriever(search_kwargs={"k": 10})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

rag_chain = load_chain()

# ─── Histórico de mensagens ───────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Título ───────────────────────────────────────────────
st.markdown('<div class="chat-title">🤖 AI Document Chatbot</div>', unsafe_allow_html=True)
st.markdown('''<div class="chat-subtitle">
    Documentos disponíveis: 
    <b style="color:#ececec">manual_produtos</b> · 
    <b style="color:#ececec">relatorio_mensal</b> · 
    <b style="color:#ececec">vendas_maio2026</b>
</div>''', unsafe_allow_html=True)

# ─── Exibe histórico ──────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-label">Você</div>'
            f'<div class="msg-user">{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="msg-label">🤖 Assistente</div>'
            f'<div class="msg-bot">{msg["content"]}</div>',
            unsafe_allow_html=True
        )

# ─── Streaming para última mensagem ──────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]

    st.markdown('<div class="msg-label">🤖 Assistente</div>', unsafe_allow_html=True)

    def stream_response():
        for chunk in rag_chain.stream(last_query):
            yield chunk

    response = st.write_stream(stream_response())

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ─── Input fixo no fundo ──────────────────────────────────
query = st.chat_input("Pergunte algo sobre os documentos...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()