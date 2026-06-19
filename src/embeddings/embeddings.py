from langchain_huggingface import HuggingFaceEmbeddings
from logs.logs_config import get_logger

logger = get_logger()

def load_embeddings():
    logger.info("🧠 Carregando embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    return embeddings