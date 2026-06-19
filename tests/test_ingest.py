from src.ingest.ingest import filter_empty_chunks

class FakeChunk:
    """ Simula um objeto Document do LangChain, só com page_content."""
    def __init__(self, content):
        self.page_content = content
        

def test_filter_empty_chunks_remove_chunks():
    chunks = [
        FakeChunk("texto válido"),
        FakeChunk(""),
        FakeChunk("  "),
        FakeChunk("outro texto")
    ]
    
    resultado = filter_empty_chunks(chunks)
    
    assert len(resultado) == 2
    assert resultado[0].page_content == "texto válido"
    assert resultado[1].page_content == "outro texto"   
    
