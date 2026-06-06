import streamlit as st
import os, time
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from prompt import prompt
from dotenv import load_dotenv
from styles import get_css, render_user_message, render_bot_message, render_header

load_dotenv()


# ─── Typewriter ───────────────────────────────────────────
def typewriter_stream(chain, query,delay=0.02):
    for token in chain.stream(query):
        for char in token:
            yield char
            time.sleep(delay)

# ─── Config ──────────────────────────────────────────────
DOCUMENTS = ["manual_produtos", "relatorio_mensal", "vendas_maio2026"]

st.set_page_config(
    page_title="AI Document Chatbot",
    page_icon="🤖",
    layout="centered"
)
st.markdown(get_css(), unsafe_allow_html=True)

# ─── Pipeline RAG ────────────────────────────────────────
@st.cache_resource
def load_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(persist_directory="db", embedding_function=embeddings)
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.3,
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
    
    response = st.write_stream(typewriter_stream(rag_chain,last_query))

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ─── Input ────────────────────────────────────────────────
if query := st.chat_input("Pergunte algo sobre os documentos..."):
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()