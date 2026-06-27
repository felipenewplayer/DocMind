from langchain_groq import ChatGroq
from dotenv import load_dotenv
from logs.logs_config import get_logger
import os

# ---- Log --------
logger = get_logger("llm")

load_dotenv()

modelo_principal = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

modelo_fallback = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

def get_llm():
    logger.info("Carregando LLM...")
    llm = modelo_principal.with_fallbacks(
        [modelo_fallback
         ],
    )
    logger.info("LLM carregada")
    return llm
    