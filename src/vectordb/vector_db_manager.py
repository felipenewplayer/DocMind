import shutil
from pathlib import Path
from langchain_chroma import Chroma
from logs.logs_config import get_logger

logger = get_logger("vector_db_manager")


def save_to_vectordb(chunks, embeddings, DB_PATH):
    if Path(DB_PATH).exists():
        shutil.rmtree(DB_PATH)

    logger.info("💾 Criando Vector DB...")

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_PATH)
    )

    logger.info(f"✅ DB salvo em {DB_PATH}")
    return db


def add_to_vectordb(chunks, embeddings, DB_PATH):
    logger.info("➕ Adicionando novos chunks...")

    db = Chroma(
        persist_directory=str(DB_PATH),
        embedding_function=embeddings
    )

    db.add_documents(chunks)

    all_docs = db.get()
    logger.info(f"📦 Total docs no DB: {len(all_docs['documents'])}")

    return db