# AtenDAI — Roteiro de Sprints

## Estratégia: Walking Skeleton

Cada sprint entrega um fluxo end-to-end funcional, começando com tudo mockado
e substituindo progressivamente por implementações reais.
O sistema deve ser demonstrável no WhatsApp desde o Sprint 1.

```
Sprint 0  →  Sprint 1  →  Sprint 2  →  Sprint 3
Fundação     E2E Mockado   Agentes Reais  RAG + Admin

Sprint 4  →  Sprint 5  →  Sprint 6
Escalamento  Notificações   Hardening
```

---

## Sprint 0 — Fundação e Contratos ✅ Concluído

> Infraestrutura pronta e contratos do domínio definidos com testes.
> Nenhuma lógica de negócio — apenas estrutura e contratos.

- [x] Docker Compose: PostgreSQL, Redis, ChromaDB, Evolution API
- [x] `pyproject.toml` com dependências e configuração do pytest
- [x] Modelos de domínio com testes: `Client`, `ConversationState`, `SpecialtyProfile`, `FAQEntry`
- [x] ABCs dos gateways: `IWhatsAppGateway`, `IVectorStore`, `ILLMClient`
- [x] Migrations iniciais (Alembic) e conexão assíncrona com o banco
- [x] `GET /health` com status de cada dependência
- [x] CI no GitHub Actions

**Critério de aceite:** 24/24 testes unitários passando, lint limpo.

---

## Sprint 1 — Walking Skeleton E2E (tudo mockado)

> Mensagem entra pelo WhatsApp, percorre todo o sistema e volta uma resposta.
> Todos os agentes são mocks — o fluxo de dados é real.

- [ ] Webhook `/webhook/whatsapp` recebe evento da Evolution API e valida assinatura
- [ ] `evolution_gateway.py` — envia mensagem de volta ao cliente
- [ ] Estado da conversa persistido no Redis (`INIT → IDENTIFYING → ROUTING → FAQ_ANSWERING`)
- [ ] Grafo LangGraph com agentes mockados (respostas fixas por estado)
- [ ] `client_service.py` — identifica ou cria cliente por número de telefone
- [ ] Teste e2e: mensagem entra → estado muda → resposta mock enviada de volta

**Critério de aceite:** enviar "oi" pelo WhatsApp real recebe resposta automática (mesmo que fixa).

---

## Sprint 2 — Agentes Reais: Recepcionista e Especialista

> Substituir mocks dos dois agentes principais por LLM real.
> ChromaDB ainda mockado com FAQs hardcoded.

- [ ] `openai_client.py` — integração real com GPT-4o (chat + embeddings)
- [ ] Agente Recepcionista: classifica intenção via LLM (dúvida / agendamento / outro)
- [ ] Roteamento real no LangGraph baseado na intenção classificada
- [ ] `rag_service.py` com ChromaDB mockado (FAQs fixas hardcoded)
- [ ] Agente Especialista: usa contexto do RAG (mock) + GPT-4o para responder
- [ ] Coleta de anamnese via conversa (campos do `SpecialtyProfile.intake_form_schema`)
- [ ] Testes unitários com mock do LLM; integração com LLM real marcada `@pytest.mark.integration`

**Critério de aceite:** perguntas reais de nutrição recebem respostas contextualizadas.

---

## Sprint 3 — RAG Real: ChromaDB + Interface Admin FAQ

> Substituir FAQs hardcoded por base vetorial real gerenciada pelo profissional.

- [ ] `chromadb_client.py` — embed, upsert, query, delete por coleção
- [ ] `faq_repository.py` — persistência das FAQs no PostgreSQL
- [ ] `faq_service.py` — CRUD: salva no banco + indexa no ChromaDB atomicamente
- [ ] `rag_service.py` real — busca semântica e injeção de contexto no prompt
- [ ] Interface Admin `/admin/faq` — Jinja2 + HTMX: listar, criar, editar, excluir
- [ ] HTTP Basic Auth nas rotas admin
- [ ] Testes de integração: `test_chromadb_gateway.py`, `test_admin_faq_routes.py`
- [ ] Teste e2e: `test_faq_rag_answer_flow.py`

**Critério de aceite:** nutricionista cadastra FAQ na interface → cliente recebe resposta baseada nela.

---

## Sprint 4 — Agente Escalador e Handoff

> Fluxo de escalamento end-to-end — bot passa a conversa ao profissional humano.

- [ ] Agente Escalador: detecta intenção de agendamento via LLM
- [ ] Urgência e confusão como gatilhos adicionais
- [ ] `escalation_service.py` — notifica profissional com resumo do contexto
- [ ] Evolution API — modo pausa do bot; bot silencioso enquanto humano atende
- [ ] Estado `ESCALATED` persistido no banco
- [ ] Retorno ao bot após encerramento do atendimento humano
- [ ] Teste e2e: `test_scheduling_escalation_flow.py`

**Critério de aceite:** "quero marcar uma consulta" → profissional notificado → bot silencioso.

---

## Sprint 5 — Notificações e Acompanhamento

> Comunicação proativa — follow-ups automáticos.

- [ ] Scheduler (APScheduler)
- [ ] Mensagem de acompanhamento pós-atendimento humano (configurável por perfil)
- [ ] Follow-ups automáticos configuráveis no `SpecialtyProfile`
- [ ] Reativação do bot após encerramento do atendimento humano
- [ ] Testes unitários do scheduler com mocks de tempo

**Critério de aceite:** após atendimento humano encerrado, cliente recebe follow-up automático.

---

## Sprint 6 — Hardening e Extensibilidade

> Sistema robusto, observável e pronto para segundo tipo de profissional.

- [ ] Rate limiting por número de telefone (`slowapi`)
- [ ] Logging estruturado (`structlog`) com correlation ID por conversa
- [ ] Tratamento centralizado de erros e retries com backoff
- [ ] Segundo `SpecialtyProfile` (ex: psicólogo) sem alterar código dos agentes
- [ ] Testes e2e completos de todos os fluxos
- [ ] Documentação da API (`/docs` + README de deploy)
- [ ] Cobertura mínima 80% verificada

---

## Decisões em Aberto

1. ~~**Stack**~~ ✅ Python 3.12 + FastAPI + LangGraph + PostgreSQL + Redis + ChromaDB
2. ~~**WhatsApp**~~ ✅ Evolution API (self-hosted)
3. **LLM:** OpenAI GPT-4o ou outro (Anthropic Claude, Gemini, local)?
4. ~~**Agendamento**~~ ✅ Escalamento para humano — sem integração com calendário
5. ~~**FAQ/RAG**~~ ✅ Interface admin (Jinja2 + HTMX) + ChromaDB
6. **Deploy MVP:** Railway/Fly.io ou VPS própria?
7. **Multi-tenant MVP:** um nutricionista ou múltiplos profissionais desde o início?

---

## Prompt de Início de Sprint

> Cole em uma nova conversa ao iniciar cada sprint.

```
Projeto: AtenDAI — sistema multiagente de atendimento via WhatsApp.
Leia os documentos de contexto antes de começar:
- docs/ARCHITECTURE.md  — visão, arquitetura, stack, domínio
- docs/GUIDELINES.md    — TDD, princípio de simplicidade, convenções
- docs/SPRINTS.md       — roteiro e critérios de aceite

Stack: Python 3.12 + FastAPI + LangGraph + LangChain + PostgreSQL + Redis
       + ChromaDB + SQLAlchemy (async) + Alembic + Evolution API

Estamos no [SPRINT X — NOME DO SPRINT].
Objetivo: [COPIE O OBJETIVO DO SPRINT AQUI]

Tarefas:
[COPIE OS ITENS DO SPRINT AQUI]

Critério de aceite:
[COPIE O CRITÉRIO DO SPRINT AQUI]

Siga TDD estritamente: escreva o teste → rode e veja falhar → implemente → verde → refatore.
Implemente apenas o necessário para o teste passar. Sem antecipações.
```
