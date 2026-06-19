from langchain_text_splitters import RecursiveCharacterTextSplitter
from logs.logs_config import get_logger

logger = get_logger()
def split_into_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter(docs)
    logger.info(f"✅ {len(chunks)} chunks gerados\n")