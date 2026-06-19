from langchain_chroma import Chroma
from logs.logs_config import get_logger

logger = get_logger("criando")

def save_to_vectordb(chunks , embeddings, DB_PATH):
    logger.info("💾 Criando Vector DB com Chroma...")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_PATH)
    )
    
    logger.info(f"✅ Vector DB salvo em '{DB_PATH}'\n")
    logger.info("🎉 Ingest concluído! Pronto para subir no Hugging Face.")
    return Chroma