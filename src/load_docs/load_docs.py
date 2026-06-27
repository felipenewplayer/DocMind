# Código para fazer o carregamento dos documentos da pasta docs 
import os
from pathlib import Path
from logs.logs_config import get_logger
from src.load_docs.loader import LOADERS
# ----- Log ------ 
logger = get_logger("load_docs")

def load_single_doc(filepath: Path):
    logger.info(f"Carregando: {filepath.name}")
    
    loader_classe = LOADERS.get(filepath.suffix)
    
    if loader_classe is None:
         logger.warning(f"Formato não suportado: {filepath.suffix}")
         return []
    
    loader = loader_classe(str(filepath))
    return loader.load()

def load_all_docs(path: Path) -> list:
    docs = []
    for filename in os.listdir(path):
        filepath = path / filename
        docs.extend(load_single_doc(filepath))
    return docs

