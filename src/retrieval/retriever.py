from logs.logs_config import get_logger

# --- Log ----
logger = get_logger("retriever")

def get_retriever(db, k=5):
    return db.as_retriever(search_kwargs={"k": k})
