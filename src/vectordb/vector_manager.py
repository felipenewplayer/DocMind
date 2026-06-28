import shutil
import streamlit as st
from pathlib import Path
from langchain_chroma import Chroma
from logs.logs_config import get_logger
from src.embeddings.embeddings import load_embeddings

logger = get_logger("vector_manager")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH  = BASE_DIR / "data" / "vectordb"


# ----- Conexão cacheada com o Chroma ------

@st.cache_resource(show_spinner=False)
def get_db():
    embeddings = load_embeddings()
    return Chroma(persist_directory=str(DB_PATH), embedding_function=embeddings)


# ---- Criação do banco vetorial -------

def create_banco(chunks, embeddings, DB_PATH):
    if Path(DB_PATH).exists():
        shutil.rmtree(DB_PATH)

    logger.info("Criando Vector DB com Chroma...")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_PATH)
    )
    return db


# ----- Busca os documentos no banco (resultado cacheado) ------

def get_documentos_disponiveis() -> list:
    db = get_db()
    all_docs = db.get(include=["metadatas"])
    metadatas = all_docs["metadatas"]

    nomes = set()
    for metadata in metadatas:
        caminho = metadata.get("source", "")
        if caminho:
            nome = Path(caminho).stem
            nomes.add(nome)
    lista_ordenada = sorted(nomes)
    logger.info(f"**** Documentos Diponíveis ****\n {lista_ordenada}")
    return list(nomes)


# ----- Salva documentos no banco  ------

def salva_no_vectordb(novos_chunks):
    embeddings = load_embeddings()
    db = Chroma.from_documents(
        persist_directory=str(DB_PATH),
        embedding=embeddings,
        documents=novos_chunks
    )
    return db


# ----- Deletar documentos do banco -------

def deleta_do_banco(nome_documento):
    db = get_db()

    todos = db.get()

    ids_para_remover = [
        id_doc for id_doc, meta in zip(todos["ids"], todos["metadatas"])
        if Path(meta.get("source", "")).stem == nome_documento
    ]

    if ids_para_remover:
        db.delete(ids=ids_para_remover)
        logger.info(f"🗑️ '{nome_documento}' removido ({len(ids_para_remover)} chunks)")
    else:
        logger.warning(f"Nenhum chunk encontrado para '{nome_documento}'")

    return len(ids_para_remover)