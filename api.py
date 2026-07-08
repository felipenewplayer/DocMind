from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from src.chain.chain import load_chain, buscar_contexto_e_fontes

load_dotenv()

app = FastAPI()

rag_chain, rag_retriever = load_chain()


class QueryInput(BaseModel):
    question: str
    chat_history: str = "Nenhuma conversa anterior."


@app.get("/")
def root():
    return {"status": "DocMind API rodando"}


@app.post("/query")
def query(input: QueryInput):
    contexto, fontes = buscar_contexto_e_fontes(
        rag_retriever,
        input.question,
        input.chat_history
    )

    input_data = {
        "question": input.question,
        "chat_history": input.chat_history,
        "context": contexto,
    }

    resposta = rag_chain.invoke(input_data)

    sem_resposta = "não encontrei essa informação" in resposta.lower()
    fontes_citadas = [f for f in fontes if f.lower() in resposta.lower()]

    return {
        "answer": resposta,
        "sources": fontes_citadas if not sem_resposta else []
    }