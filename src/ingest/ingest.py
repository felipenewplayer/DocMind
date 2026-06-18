import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader
)

# ─── Configurações ───────────────────────────────────────
load_dotenv()
BASE_DIR  = Path(__file__).resolve().parent.parent
DOCS_PATH = Path(os.getenv("DOCS_PATH", BASE_DIR / "src" / "docs"))
DB_PATH   = Path(os.getenv("DB_PATH",   BASE_DIR / "src" / "vectordb"))
DOCS_PATH.mkdir(parents=True, exist_ok=True)
DB_PATH.mkdir(parents=True, exist_ok=True)

# ─── Carrega todos os documentos da pasta docs/ ──────────
def load_all_docs(path: Path) -> list:
    docs = []
    for filename in os.listdir(path):
        filepath = path / filename
        print(f"Carregando: {filename}")

        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            docs.extend(loader.load())

        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
            docs.extend(loader.load())

        elif filename.endswith(".xlsx"):
            loader = UnstructuredExcelLoader(filepath)
            docs.extend(loader.load())

        else:
            print(f"  ⚠️ Formato não suportado, pulando: {filename}")

    return docs

# ─── Pipeline principal ──────────────────────────────────
def main():
    print("📂 Lendo documentos...")
    all_docs = load_all_docs(DOCS_PATH)
    print(f"✅ {len(all_docs)} documento(s) carregado(s)\n")

    print("✂️  Dividindo em chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(all_docs)
    print(f"✅ {len(chunks)} chunks gerados\n")
    
    chunks = [c for c in chunks if c.page_content.strip()]
    print(f"✅ {len(chunks)} chunks válidos após filtro\n")

    if not chunks:
        print("❌ Nenhum chunk válido encontrado. Verifique os documentos.")
        return

    print("🧠 Carregando embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("💾 Criando Vector DB com Chroma...")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_PATH)
    )
    print(f"✅ Vector DB salvo em '{DB_PATH}'\n")
    print("🎉 Ingest concluído! Pronto para subir no Hugging Face.")

if __name__ == "__main__":
    main()