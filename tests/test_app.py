# Código para testar funções do app.py
from app import format_history

def test_format_history_vazio():
    texto_vazio = [] #Arrange
    
    resultado = format_history(texto_vazio) #Act
    
    assert resultado == "Nenhuma conversa anterior." #Assert

def test_format_history_com_mensagens():
    texto_com_message = [
        {"role":"user","content": "oi"},
        {"role":"assistant", "content": "olá"}
    ]
    #Arrange
    resultado = format_history(texto_com_message) #Act
    
    assert resultado == "Usuário: oi\nAssistente: olá"#Assert

def test_limite_de_mensagens():
    teste_limit_message = [
    {"role": "user", "content": "msg1"},
    {"role": "assistant", "content": "msg2"},
    {"role": "user", "content": "msg3"},
    {"role": "assistant", "content": "msg4"},
    {"role": "user", "content": "msg5"},
    {"role": "assistant", "content": "msg6"},
    {"role": "user", "content": "msg7"},
    {"role": "assistant", "content": "msg8"},
    ] #Arrange
    
    resultado = format_history(teste_limit_message) # Act
    
    assert "msg3" in resultado #Assert
    assert "msg1" not in resultado #Assert