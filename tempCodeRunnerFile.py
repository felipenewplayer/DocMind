from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(persist_directory="data/vectordb", embedding_function=embeddings)

all_docs = db.get()
docs = all_docs["documents"]
print(f"Total de chunks no banco: {len(docs)}")
for i, doc in enumerate(docs):
    print(f"--- Chunk {i} ---")
    print(doc[:150])