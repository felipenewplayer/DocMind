import shutil
from pathlib import Path
from langchain_chroma import Chroma
from logs.logs_config import get_logger
from src.embeddings.embeddings import load_embeddings
logger = get_logger("criando")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH  = BASE_DIR / "data" / "vectordb"


# ---- Criação do banco vetorial -------

def create_banco(chunks,embeddings, DB_PATH):
    if Path(DB_PATH).exists():
         shutil.rmtree(DB_PATH)
         
    logger.info("Criando Vector DB com Chroma...")
    db = Chroma.from_documents(
         documents=chunks,
         embedding=embeddings,
         persist_directory=str(DB_PATH))
    return db     


# ----- Busca os documentos no banco ------

def get_documentos_disponiveis() -> list:
    embeddings = load_embeddings()
    db = Chroma(persist_directory=str(DB_PATH), embedding_function=embeddings)
    all_docs = db.get()
    metadatas = all_docs["metadatas"]
    
    nomes = set()
    for metadata in metadatas:
        caminho = metadata.get("source", "")
        if caminho:
            nome = Path(caminho).stem
            nomes.add(nome)
    lista_ordenada = sorted(nomes)
    logger.info(f"**** Documentos Diponíveis ****\n {lista_ordenada}")
    return list(nomes)

# ----- Salva documentos no banco  ------

def salva_no_vectordb(novos_chunks):
    embeddings = load_embeddings()
    db = Chroma.from_documents(
        persist_directory=str(DB_PATH),
        embedding=embeddings,
        documents=novos_chunks
    )
    return db

# ----- Deletar documentos do banco -------
def deleta_do_banco():
    pass

# def add_to_vectordb(chunks, embeddings, DB_PATH):
#     logger.info("➕ Adicionando novos documentos ao Vector DB existente...")
    
#     db = Chroma(
#         persist_directory=str(DB_PATH),
#         embedding_function=embeddings
#     )
#     db.add_documents(chunks)
    
#     logger.info(f"✅ {len(chunks)} novo(s) chunk(s) adicionado(s) com sucesso!")
#     return db