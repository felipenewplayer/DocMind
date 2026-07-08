from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from src.prompt.prompt_template import rag_prompt
from src.retrieval.retriever import get_retriever
from src.llm.llm import get_llm
from src.embeddings.embeddings import load_embeddings
from src.vectordb.vector_manager import get_documentos_disponiveis
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH  = BASE_DIR / "data" / "vectordb"


def format_context(docs):
    return "\n\n".join(d.page_content for d in docs)


def format_documentos_disponiveis():
    docs = get_documentos_disponiveis()
    if not docs:
        return "Nenhum documento disponível no momento."
    return ", ".join(docs)


def construir_query_retrieval(pergunta, historico):
    documentos = get_documentos_disponiveis()
    pergunta_lower = pergunta.lower()
    menciona_documento = any(doc.lower() in pergunta_lower for doc in documentos)
    if menciona_documento:
        return pergunta
    if historico and historico != "Nenhuma conversa anterior.":
        return f"{historico}\nPergunta atual: {pergunta}"
    return pergunta


def buscar_contexto_e_fontes(retriever, pergunta, historico):
    query_busca = construir_query_retrieval(pergunta, historico)
    docs = retriever.invoke(query_busca)
    contexto = "\n\n".join(d.page_content for d in docs)
    fontes = []
    vistos = set()
    for d in docs:
        nome = Path(d.metadata.get("source", "")).stem
        if nome and nome not in vistos:
            vistos.add(nome)
            fontes.append(nome)
    return contexto, fontes


def load_chain():
    embeddings = load_embeddings()
    db = Chroma(persist_directory=str(DB_PATH), embedding_function=embeddings)
    llm = get_llm()
    retriever = get_retriever(db, k=5)

    chain = (
        {
            "context": lambda x: x["context"],
            "question": lambda x: x["question"],
            "chat_history": lambda x: x["chat_history"],
            "documentos_disponiveis": lambda x: format_documentos_disponiveis(),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever