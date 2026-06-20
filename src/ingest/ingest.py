import os
from pathlib import Path
from dotenv import load_dotenv

from src.load_docs.load_docs import load_all_docs
from src.chunking.chunking import split_into_chunks, filter_empty_chunks
from src.embeddings.embeddings import load_embeddings
from src.vectordb.criando import save_to_vectordb
from logs.logs_config import get_logger

# ---- Log -----
logger = get_logger("ingest")

# ----- Configuração -----------
load_dotenv()

BASE_DIR  = Path(__file__).resolve().parent.parent.parent
DOCS_PATH = Path(os.getenv("DOCS_PATH", BASE_DIR / "src" / "docs"))
DB_PATH   = Path(os.getenv("DB_PATH",   BASE_DIR / "src" / "vectordb"))
DOCS_PATH.mkdir(parents=True, exist_ok=True)
DB_PATH.mkdir(parents=True, exist_ok=True)


def main():
    docs = load_all_docs(DOCS_PATH)
    chunks = split_into_chunks(docs)
    chunks = filter_empty_chunks(chunks)
    if not chunks:
        return
    embeddings = load_embeddings()
    save_to_vectordb(chunks, embeddings, DB_PATH)


if __name__ == "__main__":
    main()