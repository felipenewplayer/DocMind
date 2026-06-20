# Código para fazer o carregamento dos documentos da pasta docs 
import os
from pathlib import Path
from logs.logs_config import get_logger
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader
)

logger = get_logger("load_docs")

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
