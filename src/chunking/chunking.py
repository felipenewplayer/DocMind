from langchain_text_splitters import RecursiveCharacterTextSplitter
from logs.logs_config import get_logger

logger = get_logger("chunking")
def split_into_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"✅ {len(chunks)} chunks gerados\n")
    return chunks