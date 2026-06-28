from langchain_huggingface import HuggingFaceEmbeddings
from logs.logs_config import get_logger
import streamlit as st
import os

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

# --- Log -----
logger = get_logger("embeddings")

@st.cache_resource(show_spinner=False)
def load_embeddings():
    logger.info("🧠 Carregando embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    return embeddings