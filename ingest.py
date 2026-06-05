import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader
)

# ─── Configurações ───────────────────────────────────────
DOCS_PATH = "docs"
DB_PATH = "db"

# ─── Carrega todos os documentos da pasta docs/ ──────────
def load_all_docs(path: str):
    docs = []
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
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

    print("🧠 Carregando embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("💾 Criando Vector DB com Chroma...")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    print(f"✅ Vector DB salvo em '{DB_PATH}'\n")
    print("🎉 Ingest concluído! Pronto para subir no Hugging Face.")

if __name__ == "__main__":
    main()