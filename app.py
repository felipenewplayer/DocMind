import streamlit as st
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from prompt import prompt

st.title("📄 AI Document Chatbot")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@st.cache_resource
def load_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(
        persist_directory="db",
        embedding_function=embeddings
    )
    llm_groq = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.5,
        api_key=GROQ_API_KEY
    )
    retriever = db.as_retriever(search_kwargs={"k": 10})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm_groq
        | StrOutputParser()
    )
    return chain

rag_chain = load_chain()

query = st.text_input("Pergunte algo sobre os documentos")
if query:
    with st.spinner("Pensando..."):
        response = rag_chain.invoke(query)
        st.write(response)