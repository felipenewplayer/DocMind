import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader
)
from src.chunking.chunking import split_into_chunks
from src.embeddings.embeddings import load_embeddings
from src.vectordb.criando import save_to_vectordb
from logs.logs_config import get_logger

logger = get_logger("ingest")

load_dotenv()
BASE_DIR  = Path(__file__).resolve().parent.parent
DOCS_PATH = Path(os.getenv("DOCS_PATH", BASE_DIR / "src" / "docs"))
DB_PATH   = Path(os.getenv("DB_PATH",   BASE_DIR / "src" / "vectordb"))
DOCS_PATH.mkdir(parents=True, exist_ok=True)
DB_PATH.mkdir(parents=True, exist_ok=True)


def load_all_docs(path: Path) -> list:
    docs = []
    for filename in os.listdir(path):
        filepath = path / filename
        logger.info(f"Carregando: {filename}")

        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            docs.extend(loader.load())
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
            docs.extend(loader.load())
        elif filename.endswith(".xlsx"):
            loader = UnstructuredExcelLoader(filepath)
            docs.extend(loader.load())
        else:
            logger.info(f"  ⚠️ Formato não suportado, pulando: {filename}")

    logger.info("📂 Lendo documentos...")
    logger.info(f"✅ {len(docs)} documento(s) carregado(s)\n")
    return docs


def filter_empty_chunks(chunks: list) -> list:
    """Remove chunks com conteúdo vazio ou só com espaço."""
    filtrados = [c for c in chunks if c.page_content.strip()]
    if not filtrados:
        logger.error("Nenhum chunk válido encontrado. Verifique os documentos.")
        return []
    logger.info(f"✅ {len(filtrados)} chunks válidos após filtro\n")
    return filtrados


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