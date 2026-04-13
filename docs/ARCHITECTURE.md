# AtenDAI — Arquitetura

## 1. Visão do Produto

**AtenDAI** é uma plataforma de atendimento inteligente via WhatsApp que conecta
clientes a um sistema de agentes de IA capaz de:

- Responder dúvidas frequentes personalizadas por profissional via RAG
- Coletar e registrar dados dos clientes (anamnese, histórico, etc.)
- Encaminhar pedidos de agendamento e casos complexos ao profissional humano
- Enviar lembretes e acompanhamentos automáticos

**MVP:** Atendimento para clínicas de nutrição.
**Fase 2+:** Plataforma extensível para psicólogos, fisioterapeutas, dentistas, etc.

---

## 2. Diagrama do Sistema

```
[Interface Admin]               ← nutricionista gerencia FAQs
       │  CRUD de perguntas/respostas
       ▼
[API Admin]  ──embed──▶  [ChromaDB]   ← vetores das FAQs (RAG)
                                ▲
WhatsApp (cliente)              │ busca semântica
       │                        │
       ▼                        │
[Evolution API Gateway]         │
       │                        │
       ▼                        │
[Orquestrador de Agentes]  ─────┘
(LangGraph)
       │
   ┌───┴──────────────────────────┐
   ▼           ▼                  ▼
[Agente     [Agente           [Agente
Recepção]   Nutrição IA]      Escalamento]
                                   │
                                   ▼
                          [Profissional Humano]  ← assume a conversa
   │
   ▼
[Memória / Estado da Conversa]  ← Redis + PostgreSQL
```

---

## 3. Agentes do MVP

| Agente | Responsabilidade |
|--------|-----------------|
| **Recepcionista** | Primeiro contato, identificação do cliente, triagem de intenção |
| **Nutricionista IA** | Responde dúvidas via RAG sobre a FAQ cadastrada, coleta anamnese inicial |
| **Escalador** | Detecta pedidos de agendamento, urgência ou confusão e aciona atendimento humano |
| **Notificador** | Envia lembretes, retornos e mensagens proativas agendadas |

### Regra de negócio crítica

**Agendamentos nunca são processados pelo bot.** Qualquer intenção de agendar, cancelar
ou reagendar uma consulta dispara o Agente Escalador imediatamente, que notifica o
profissional humano e transfere a conversa.

---

## 4. Extensibilidade

Cada tipo de profissional é um **Perfil de Especialidade** (`SpecialtyProfile`) com:
- Persona do agente especialista (prompt base)
- FAQs indexadas no ChromaDB em coleção própria (`faq_{profile_id}`)
- Schema de coleta de dados específico (anamnese nutricional, ficha psicológica, etc.)
- Gatilhos de escalamento configuráveis

---

## 5. Stack Tecnológica

### Backend
- Runtime: **Python 3.12+**
- Framework: **FastAPI** (API do bot + rotas admin)
- Agentes: **LangGraph + LangChain**
- LLM: **OpenAI GPT-4o** (fallback: GPT-4o-mini)
- Embeddings: **OpenAI text-embedding-3-small**
- Testes: **pytest + pytest-asyncio**

### Persistência
- **PostgreSQL** — clientes, histórico de conversas, FAQs
- **Redis** — estado de conversa ativo, cache, filas
- **ChromaDB** — vetores das FAQs para RAG (coleção por `specialty_profile_id`)
- ORM: **SQLAlchemy** (async) + **Alembic** para migrations

### Interface Admin (FAQ)
- **FastAPI + Jinja2 + HTMX** — server-side rendering
- HTTP Basic Auth (MVP) → evoluir para JWT na Fase 2
- Ao salvar FAQ: texto é embeddado e indexado no ChromaDB automaticamente

### Infraestrutura
- **Evolution API** — gateway WhatsApp (self-hosted)
- Docker + Docker Compose (desenvolvimento local)
- Pydantic Settings para variáveis de ambiente
- CI: GitHub Actions

---

## 6. Domínio de Negócio

### Entidades

```
Client
  id, phone_number, name, created_at
  └── ConversationHistory[]

Professional
  id, name, specialty_profile_id

SpecialtyProfile
  id, profession_type (NUTRITIONIST | PSYCHOLOGIST | ...)
  agent_persona, intake_form_schema (JSON)
  escalation_triggers[]       ← inclui SCHEDULING por padrão
  chromadb_collection_name    ← "faq_{id}"

FAQEntry                      ← PostgreSQL + ChromaDB
  id, specialty_profile_id
  question, answer, tags[], is_active
  created_at, updated_at

ConversationState
  session_id, client_id, current_agent
  context_window[], collected_data (JSON)
  escalation_reason, last_activity_at
```

### Máquina de Estados

```
INIT → IDENTIFYING_CLIENT → ROUTING →
  ├── FAQ_ANSWERING
  ├── INTAKE_COLLECTION
  └── ESCALATED  ← agendamento, urgência ou confusão
        └── RESOLVED → FOLLOW_UP → CLOSED
```

---

## 7. Estrutura de Pastas

```
atendai/
├── src/
│   ├── agents/
│   │   ├── base_agent.py        ← ABC extensível
│   │   ├── receptionist.py
│   │   ├── specialist.py        ← usa RAG
│   │   └── escalation.py
│   ├── orchestrator/
│   │   ├── graph.py             ← grafo LangGraph
│   │   └── router.py
│   ├── domain/
│   │   ├── models.py            ← Pydantic (entidades puras)
│   │   └── orm.py               ← SQLAlchemy ORM
│   ├── services/
│   │   ├── client_service.py
│   │   ├── faq_service.py       ← CRUD + re-indexação ChromaDB
│   │   ├── rag_service.py       ← busca semântica + contexto
│   │   ├── escalation_service.py
│   │   └── notification_service.py
│   ├── gateways/
│   │   ├── interfaces.py        ← IWhatsAppGateway, IVectorStore, ILLMClient
│   │   ├── whatsapp/            ← evolution_gateway.py, message_formatter.py
│   │   ├── vector_store/        ← chromadb_client.py
│   │   └── llm/                 ← openai_client.py
│   ├── repositories/
│   │   ├── client_repository.py
│   │   ├── conversation_repository.py
│   │   └── faq_repository.py
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── webhook.py       ← recebe mensagens WhatsApp
│   │   │   └── admin/faq.py    ← CRUD de FAQs
│   │   ├── templates/admin/
│   │   └── middleware/auth.py
│   └── config/
│       ├── settings.py
│       └── database.py
├── tests/
│   ├── conftest.py              ← fixtures + mocks dos gateways
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── migrations/                  ← Alembic
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE.md          ← este arquivo
│   ├── GUIDELINES.md
│   └── SPRINTS.md
└── .env.example
```
