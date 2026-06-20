from langchain_text_splitters import RecursiveCharacterTextSplitter
from logs.logs_config import get_logger

# --- Log ----
logger = get_logger("chunking")

def split_into_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"✅ {len(chunks)} chunks gerados\n")
    return chunks

def filter_empty_chunks(chunks: list) -> list:
    """Remove chunks com conteúdo vazio ou só com espaço."""
    filtrados = [c for c in chunks if c.page_content.strip()]
    if not filtrados:
        logger.error("Nenhum chunk válido encontrado. Verifique os documentos.")
        return []
    logger.info(f"✅ {len(filtrados)} chunks válidos após filtro\n")
    return filtrados