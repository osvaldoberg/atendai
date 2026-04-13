# AtenDAI

Sistema multiagente de atendimento via WhatsApp para profissionais de saúde.
Responde dúvidas via RAG, coleta dados dos clientes e encaminha pedidos de
agendamento ao profissional humano.

**MVP:** nutricionistas. **Extensível** para psicólogos, fisioterapeutas e outros.

---

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- Conta OpenAI com acesso à API

---

## Início rápido

```bash
# 1. Clone e acesse o projeto
git clone <repo-url>
cd atendai

# 2. Crie o ambiente virtual e instale as dependências
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves (OPENAI_API_KEY, etc.)

# 4. Suba a infraestrutura
docker compose -f docker/docker-compose.yml up -d postgres redis chromadb

# 5. Rode as migrations
alembic upgrade head

# 6. Inicie a aplicação
uvicorn src.api.main:app --reload
```

Acesse `http://localhost:8000/health` para verificar o status dos serviços.

---

## Desenvolvimento

```bash
# Rodar testes unitários
pytest tests/unit

# Rodar testes com cobertura
pytest tests/unit --cov=src --cov-report=term-missing

# Lint
ruff check src tests
black --check src tests

# Testes de integração (requerem serviços rodando)
pytest tests/integration -m integration
```

---

## Arquitetura

```
WhatsApp (cliente)
       │
       ▼
[Evolution API Gateway]
       │
       ▼
[Orquestrador LangGraph]
       │
   ┌───┴──────────────────┐
   ▼         ▼            ▼
Recepção  Especialista  Escalador
          (RAG + LLM)      │
                           ▼
                   Profissional Humano

[ChromaDB] ← FAQs indexadas via interface admin
[PostgreSQL + Redis] ← estado e histórico
```

Veja [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) para detalhes completos.

---

## Documentação

| Arquivo | Conteúdo |
|---------|----------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Diagrama, agentes, stack, domínio, estrutura de pastas |
| [`docs/GUIDELINES.md`](docs/GUIDELINES.md) | TDD, princípio de simplicidade, convenções de código |
| [`docs/SPRINTS.md`](docs/SPRINTS.md) | Roteiro de sprints e critérios de aceite |

---

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `OPENAI_API_KEY` | Chave da API OpenAI |
| `DATABASE_URL` | URL de conexão PostgreSQL |
| `REDIS_URL` | URL de conexão Redis |
| `CHROMA_HOST` / `CHROMA_PORT` | Endereço do ChromaDB |
| `EVOLUTION_API_URL` / `EVOLUTION_API_KEY` | Gateway WhatsApp |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Acesso à interface admin de FAQ |

Consulte [`.env.example`](.env.example) para a lista completa.

---

## Stack

- **Python 3.12** · FastAPI · LangGraph · LangChain
- **PostgreSQL** · Redis · ChromaDB
- **Evolution API** (WhatsApp gateway)
- **OpenAI** GPT-4o + text-embedding-3-small
- pytest · Ruff · Black
