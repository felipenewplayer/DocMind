from pathlib import Path
from logs.logs_config import get_logger

# --- Log ----
logger = get_logger("retriever")

def get_retriever(db, k=5):
    logger.info("Fazendo o retriever...")
    return db.as_retriever(search_kwargs={"k": k})


def get_documentos_disponiveis(db) -> list:
    all_docs = db.get()
    metadatas = all_docs["metadatas"]
    
    nomes = set()
    for metadata in metadatas:
        caminho = metadata.get("source", "")
        if caminho:
            nome = Path(caminho).stem
            nomes.add(nome)
    
    return list(nomes)