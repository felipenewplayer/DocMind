from langchain_groq import ChatGroq
from dotenv import load_dotenv
from logs.logs_config import get_logger
import os


load_dotenv()

def get_llm():
    
    modelo_principal = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY")
    )   
    
    modelo_fallback = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.5,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    return modelo_principal.with_fallbacks([modelo_fallback])