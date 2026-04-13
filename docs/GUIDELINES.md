# AtenDAI — Orientações de Desenvolvimento

## 1. Princípio Central: Código Simples e Objetivo

> **Implemente apenas o necessário para o teste passar. Nada mais.**

- Não antecipe funcionalidades que não estão no sprint atual
- Prefira a solução mais simples que resolve o problema
- Se você não tem um teste para isso, não escreva o código
- Código que não existe não tem bugs

```python
# ❌ Evitar — implementação que antecipa o futuro sem necessidade
class ClientService:
    async def find(self, id, include_history=True, include_appointments=True,
                   eager_load=True, cache_ttl=300):
        ...

# ✅ Preferir — o mínimo que faz o teste passar
class ClientService:
    async def find_by_phone(self, phone_number: str) -> Client | None:
        return await self.repo.get_by_phone(phone_number)
```

---

## 2. TDD — Red → Green → Refactor

**Regra de ouro: nunca escreva código de produção sem um teste falhando antes.**

### Ciclo

1. **Red** — escreva o teste descrevendo o comportamento esperado. Rode. Deve falhar.
2. **Green** — escreva o mínimo de código para o teste passar. Sem over-engineering.
3. **Refactor** — melhore o código sem quebrar os testes.

### Estrutura de testes

```
tests/
  unit/          ← sem dependências externas, rápidos, sempre com mocks
  integration/   ← marcados @pytest.mark.integration, dependem de serviços reais
  e2e/           ← marcados @pytest.mark.e2e, fluxo completo
```

### Convenções

- **Nomes descritivos:** `test_should_escalate_to_human_when_client_asks_for_appointment`
- **Arrange / Act / Assert** explícito em cada teste
- Mocks para dependências externas via `pytest-mock` — nunca chamar LLM/WhatsApp nos testes unitários
- Fixtures reutilizáveis em `conftest.py`
- Cobertura mínima: **80%** para merge em `main`

```python
# ✅ Estrutura padrão de teste
async def test_should_create_client_when_not_found(client_service, mock_repo):
    # Arrange
    mock_repo.get_by_phone.return_value = None
    phone = "+5511999999999"

    # Act
    client = await client_service.get_or_create(phone)

    # Assert
    assert client.phone_number == phone
    mock_repo.save.assert_called_once()
```

---

## 3. Interfaces Antes de Implementações

Todas as dependências externas (LLM, WhatsApp, ChromaDB) têm uma **ABC** em
`src/gateways/interfaces.py`. Os agentes e serviços dependem apenas dessas interfaces.

Isso garante que:
- Testes unitários usam mocks sem nenhuma configuração de ambiente
- Implementações reais podem ser trocadas sem alterar o código dos agentes
- Cada sprint pode avançar substituindo um mock por vez

```python
# ✅ Agente depende da interface, não da implementação
class SpecialistAgent:
    def __init__(self, llm: ILLMClient, vector_store: IVectorStore):
        self.llm = llm
        self.vector_store = vector_store
```

---

## 4. Convenções de Código

### Estilo
- **Linting:** Ruff + Black (linha máxima: 100 caracteres)
- **Tipos:** Pydantic models em todo o domínio; type hints obrigatórios em funções públicas
- **Enums:** usar `StrEnum` (Python 3.11+) em vez de `str, Enum`
- **Datas:** sempre `datetime.now(UTC)` — nunca `datetime.utcnow()` (deprecated)
- **Segredos:** nunca no código — sempre via variáveis de ambiente em `settings.py`

### Organização
- **Domínio puro:** `src/domain/models.py` não importa FastAPI, SQLAlchemy nem LangChain
- **Gateways:** toda I/O externa fica em `src/gateways/` — nunca direto nos agentes
- **Repositórios:** toda lógica de banco fica em `src/repositories/` — nunca nos serviços

### Comentários
- Não comente o óbvio — o código deve ser autoexplicativo
- Comente apenas decisões não óbvias, trade-offs ou restrições de negócio

```python
# ❌ Comentário inútil
# Retorna o cliente
return client

# ✅ Comentário útil
# Evolution API exige delay mínimo de 1s entre mensagens para evitar bloqueio
await asyncio.sleep(1)
await self.gateway.send_message(phone, text)
```

### Git
- **Commits:** Conventional Commits (`feat:`, `test:`, `fix:`, `refactor:`, `docs:`)
- **Branches:** `main` / `develop` / `feature/nome-curto`
- **PR:** nenhum merge sem testes passando e lint limpo

---

## 5. O que Não Fazer

| ❌ Evitar | ✅ Preferir |
|-----------|------------|
| Implementar para "o futuro" | Implementar para o teste atual |
| Classe com 10+ responsabilidades | Uma classe, uma responsabilidade |
| Chamar LLM em teste unitário | Mock do `ILLMClient` |
| Lógica de banco no serviço | Repositório para lógica de banco |
| Hardcoded strings/configs | `settings.py` + `.env` |
| `except Exception` genérico | Capturar exceção específica |
