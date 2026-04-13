"""
Implementações mock das interfaces de gateway para uso nos testes.
Usam apenas memória — sem dependências de serviços externos.
"""

from typing import Any

from src.gateways.interfaces import ILLMClient, IVectorStore, IWhatsAppGateway


class MockWhatsAppGateway(IWhatsAppGateway):
    def __init__(self) -> None:
        self.sent_messages: list[dict[str, Any]] = []
        self.paused_numbers: set[str] = set()

    async def send_message(self, phone_number: str, text: str) -> dict[str, Any]:
        payload = {"phone_number": phone_number, "text": text}
        self.sent_messages.append(payload)
        return {"status": "sent", **payload}

    async def send_template(
        self,
        phone_number: str,
        template_name: str,
        variables: dict[str, str],
    ) -> dict[str, Any]:
        payload = {"phone_number": phone_number, "template": template_name, "vars": variables}
        self.sent_messages.append(payload)
        return {"status": "sent", **payload}

    async def pause_bot(self, phone_number: str) -> None:
        self.paused_numbers.add(phone_number)

    async def resume_bot(self, phone_number: str) -> None:
        self.paused_numbers.discard(phone_number)


class MockVectorStore(IVectorStore):
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def upsert(
        self,
        collection: str,
        doc_id: str,
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        self._store[f"{collection}:{doc_id}"] = {"text": text, "metadata": metadata}

    async def query(
        self,
        collection: str,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        prefix = f"{collection}:"
        results = [
            {"id": k.removeprefix(prefix), **v, "score": 0.9}
            for k, v in self._store.items()
            if k.startswith(prefix)
        ]
        return results[:n_results]

    async def delete(self, collection: str, doc_id: str) -> None:
        self._store.pop(f"{collection}:{doc_id}", None)

    async def delete_collection(self, collection: str) -> None:
        keys = [k for k in self._store if k.startswith(f"{collection}:")]
        for k in keys:
            del self._store[k]


class MockLLMClient(ILLMClient):
    def __init__(self, default_response: str = "Resposta mock do LLM.") -> None:
        self.default_response = default_response
        self.calls: list[dict[str, Any]] = []

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        self.calls.append({"messages": messages, "model": model})
        return self.default_response

    async def embed(self, text: str) -> list[float]:
        return [0.1] * 1536

    async def classify_intent(self, text: str, possible_intents: list[str]) -> str:
        return possible_intents[0] if possible_intents else "UNKNOWN"
