---
title: DocMind
emoji: 🤖
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.58.0
python_version: '3.11'
app_file: app.py
pinned: false
license: mit
short_description: AI Document Chatbot with RAG built from scratch
---

# 🤖 DocMind

Chatbot de RAG (Retrieval-Augmented Generation) construído do zero para responder perguntas sobre documentos PDF, TXT e XLSX, com memória de conversa e pipeline modular testado.

🔗 **App ao vivo:** [Hugging Face Space](https://huggingface.co/spaces/Felipe-2026/ai-agent-demo)
📂 **Código-fonte:** [GitHub](https://github.com/felipenewplayer/DocMind)

---

## 📋 Sobre o projeto

O DocMind responde perguntas em linguagem natural com base no conteúdo de documentos carregados — sem alucinar informações que não estão nos arquivos. O projeto foi construído para praticar um pipeline RAG completo, ponta a ponta: ingestão, chunking, embeddings, vector store, retrieval, prompt engineering, memória de conversa e deploy real.

### Funcionalidades

- 📄 Suporte a múltiplos formatos: PDF, TXT e XLSX
- 🧠 Memória de conversa (lembra do contexto entre perguntas)
- 🚫 Prompt anti-alucinação (não inventa informação fora dos documentos)
- 🔄 Reindexação manual via interface (sem precisar reiniciar o app)
- 📊 Logging estruturado por módulo
- ✅ Suíte de testes automatizados (pytest)

---

## 🛠️ Stack técnica

| Camada | Tecnologia |
|---|---|
| Interface | Streamlit |
| Orquestração | LangChain |
| LLM | Groq (Llama 3.3 70B) |
| Embeddings | HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`) |
| Vector Store | ChromaDB |
| Testes | pytest |

---

## 🏗️ Arquitetura

O pipeline de ingestão é modularizado por responsabilidade, em vez de uma única função fazendo tudo:
src/

├── load_docs/      # Carrega PDF, TXT, XLSX

├── chunking/        # Divide documentos em chunks + filtra vazios

├── embeddings/       # Carrega o modelo de embeddings

├── vectordb/         # Cria e persiste o banco vetorial (Chroma)

├── ingest/           # Orquestra o pipeline (chama os módulos acima)

├── prompt/            # Template do prompt RAG

logs/

├── logs_config.py    # Configuração centralizada de logging

tests/

├── test_app.py        # Testes de format_history()

├── test_chunking.py   # Testes de split_into_chunks() e filter_empty_chunks()

Essa separação permite testar cada etapa isoladamente e facilita a manutenção — um bug no chunking não exige reler todo o pipeline de ingestão.

### Memória de conversa

Implementada manualmente via formatação do histórico (`format_history()`), injetado no prompt como contexto adicional, em vez de usar `RunnableWithMessageHistory`. Essa foi uma escolha deliberada para o estágio atual do projeto — ver seção de Limitações e próximos passos.

---

## ✅ Testes

O projeto conta com testes automatizados usando `pytest`, cobrindo as funções puras e determinísticas do pipeline:

```bash
pytest tests/ -v
```

| Módulo testado | Cenários cobertos |
|---|---|
| `format_history()` | Lista vazia, histórico normal, corte pelo limite de mensagens |
| `split_into_chunks()` | Texto curto (1 chunk), texto longo (múltiplos chunks) |
| `filter_empty_chunks()` | Remoção de chunks vazios ou só com espaço |

---

## 🐛 Desafios de deploy (e como foram resolvidos)

Durante o deploy no Hugging Face Spaces, o app funcionava localmente mas falhava em produção. A investigação revelou dois bugs específicos de ambiente:

1. **Path duplicado**: `BASE_DIR` era calculado com uma quantidade de `.parent` que funcionava localmente, mas resolvia para `/app/src/src/docs` no container do Hugging Face (uma camada de diretório diferente da estrutura local). Resolvido ajustando a contagem de `.parent` e validando com logs de debug temporários.
2. **Dependência faltante**: o `UnstructuredExcelLoader` falhava silenciosamente em produção por falta da biblioteca `msoffcrypto-tool`, que não estava listada no `requirements.txt`.

Esse processo reforçou a importância de testar o ambiente de produção como uma "caixa preta" separada do ambiente local, e de usar logging estratégico para diagnosticar problemas sem acesso direto ao servidor.

---

## 🔮 Limitações e próximos passos

Documentado de forma transparente, como parte do aprendizado:

- **Memória de sessão volátil**: o histórico de conversa vive em `st.session_state`, que é perdido ao fechar a aba. Em produção real, isso seria substituído por `RunnableWithMessageHistory` com um store persistente (Redis ou Postgres) para suportar múltiplos usuários e sessões duradouras.
- **Sem controle de tokens no histórico**: o histórico é limitado por número de mensagens (não por tokens), o que pode não escalar bem para conversas muito longas.
- **Testes cobrem apenas funções puras**: módulos que dependem de API externa (Groq, embeddings) ainda não têm testes com mocks.

---

## 🚀 Rodando localmente

```bash
git clone https://github.com/felipenewplayer/DocMind
cd DocMind
pip install -r requirements.txt
```

Crie um `.env` na raiz com:
GROQ_API_KEY=sua_chave_aqui

Rode o app:
```bash
streamlit run app.py
```

---

## 👤 Autor

Felipe — [GitHub](https://github.com/felipenewplayer)