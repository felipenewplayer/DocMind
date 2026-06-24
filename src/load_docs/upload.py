import tempfile
from pathlib import Path
from src.load_docs.load_docs import load_single_doc
from logs.logs_config import get_logger
# --- Log ----
logger = get_logger("upload")

def load_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix  # pega a extensão (.pdf, .txt, etc)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        caminho_temporario = Path(tmp.name)
    
    documentos = load_single_doc(caminho_temporario)
    for d in documentos:
        d.metadata["source"]  = uploaded_file.name
        logger.info(d)
    return documentos