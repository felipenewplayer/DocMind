from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template("""
Você receberá trechos de diferentes arquivos.

Resuma cada arquivo separadamente.

Use o nome do arquivo (📄 Arquivo: ...) como referência.
NÃO invente documentos.
Se houver apenas um arquivo, diga isso.

Contexto:
{context}

Pergunta:
{question}
""")