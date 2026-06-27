import shutil
from pathlib import Path
from langchain_chroma import Chroma
from logs.logs_config import get_logger

logger = get_logger("criando")

def save_to_vectordb(chunks, embeddings, DB_PATH):
    if Path(DB_PATH).exists():
        shutil.rmtree(DB_PATH)
    
    logger.info("💾 Criando Vector DB com Chroma...")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_PATH)
    )
    logger.info(f"✅ Vector DB salvo em '{DB_PATH}'\n")
    logger.info("🎉 Ingest concluído! Pronto para subir no Hugging Face.")
    return db

def add_to_vectordb(chunks, embeddings, DB_PATH):
    logger.info("➕ Adicionando novos documentos ao Vector DB existente...")
    
    db = Chroma(
        persist_directory=str(DB_PATH),
        embedding_function=embeddings
    )
    db.add_documents(chunks)
    
    logger.info(f"✅ {len(chunks)} novo(s) chunk(s) adicionado(s) com sucesso!")
    return db