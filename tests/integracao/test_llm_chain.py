from unittest.mock import  patch, MagicMock
from src.llm.llm import get_llm

@patch("src.llm.llm.ChatGroq")
def test_chat_groq(mock_chatgroq):
    # 1. Cria dois mocks separados (um pro principal, um pro fallback)
    mock_principal = MagicMock()
    mock_fallback = MagicMock()
    
    # 2. Configura o side_effect pra retornar cada um na ordem certa
    mock_chatgroq.side_effect = [mock_principal, mock_fallback]
    
    # 3. Configura o que .with_fallbacks() retorna quando chamado no principal
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "resposta de teste"
    mock_principal.with_fallbacks.return_value = mock_llm  # 👈 o que vai aqui?
    
    # 4. Chama get_llm() e testa
    llm = get_llm()
    resultado = llm.invoke("pergunta de teste")
    
    assert llm is not None
    assert resultado.content == "resposta de teste"