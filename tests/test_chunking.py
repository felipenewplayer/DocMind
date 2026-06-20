#Código que testa as funções de chunking.py
from langchain_core.documents import Document
from src.chunking.chunking import split_into_chunks, filter_empty_chunks

def test_split_into_chunks_texto_curto():
    documento = [Document(page_content="Este é um texto de teste.")] #Arrange
    
    resultado = split_into_chunks(documento) #Act
    
    assert len(resultado) == 1


def test_split_into_chunks_texto_longo():
    texto_longo = "abc"* 833
    
    documento = [Document(page_content=texto_longo)] #Arrange
    
    resultado = split_into_chunks(documento) #Act
    
    assert len(resultado) > 1
    
def test_filter_empty_chunks_remove_chunks():
    chunks = [
        Document(page_content="texto válido"),
        Document(page_content=""),
        Document(page_content="  "),
        Document(page_content="outro texto")
    ]
    
    resultado = filter_empty_chunks(chunks)
    
    assert len(resultado) == 2
    assert resultado[0].page_content == "texto válido"
    assert resultado[1].page_content == "outro texto" 