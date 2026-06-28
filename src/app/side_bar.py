import streamlit as st
from pathlib import Path
from src.load_docs.upload import load_uploaded_file
from src.chunking.chunking import split_into_chunks, filter_empty_chunks
from src.vectordb.vector_manager import get_documentos_disponiveis,salva_no_vectordb,deleta_do_banco

DOCUMENTS = ["manual_produtos", "relatorio_mensal", "vendas_maio2026"]
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH  = BASE_DIR / "data" / "vectordb"

def side_bar():
 with st.sidebar:
    st.markdown("### **Documentos indexados:**")
    with st.container(height=350):
        documentos = get_documentos_disponiveis()
        for doc in documentos:
            col1, col2 = st.columns([4, 1])
            with col1:
                if not documentos:
                    st.markdown('Lista vazia')
                else:
                    st.markdown(f' - {doc}')
            with col2:
                if st.button("X", key=f"delete_{doc}"):
                    deleta_do_banco(doc)
                    st.cache_resource.clear()
                    st.rerun()

    st.markdown("**Adicionar novo documento:**")
    arquivo_enviado = st.file_uploader(
        "Envie um PDF, TXT ou XLSX",
        type=["pdf", "txt", "xlsx"]
    )
    if arquivo_enviado is not None:
        if st.button("📥 Processar e adicionar"):
            with st.spinner("Processando novo documento..."):
                novos_docs = load_uploaded_file(arquivo_enviado)
                novos_chunks = split_into_chunks(novos_docs)
                novos_chunks = filter_empty_chunks(novos_chunks)

                if novos_chunks:
                    salva_no_vectordb(novos_chunks)
                    st.cache_resource.clear()
                    st.success(f"✅ '{arquivo_enviado.name}' adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Não foi possível extrair conteúdo desse arquivo.")
