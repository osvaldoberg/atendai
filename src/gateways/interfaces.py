"""
Interfaces (ABCs) de todos os gateways externos.
Agentes e serviços dependem apenas destas abstrações — nunca de implementações concretas.
"""

from abc import ABC, abstractmethod
from typing import Any


class IWhatsAppGateway(ABC):
    @abstractmethod
    async def send_message(self, phone_number: str, text: str) -> dict[str, Any]:
        """Envia uma mensagem de texto ao número informado."""

    @abstractmethod
    async def send_template(
        self,
        phone_number: str,
        template_name: str,
        variables: dict[str, str],
    ) -> dict[str, Any]:
        """Envia uma mensagem baseada em template."""

    @abstractmethod
    async def pause_bot(self, phone_number: str) -> None:
        """Pausa o bot para que o profissional humano assuma a conversa."""

    @abstractmethod
    async def resume_bot(self, phone_number: str) -> None:
        """Retoma o bot após o atendimento humano."""


class IVectorStore(ABC):
    @abstractmethod
    async def upsert(
        self,
        collection: str,
        doc_id: str,
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        """Insere ou atualiza um documento na coleção."""

    @abstractmethod
    async def query(
        self,
        collection: str,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Busca semântica na coleção. Retorna lista de documentos com score."""

    @abstractmethod
    async def delete(self, collection: str, doc_id: str) -> None:
        """Remove um documento da coleção pelo ID."""

    @abstractmethod
    async def delete_collection(self, collection: str) -> None:
        """Remove uma coleção inteira."""


class ILLMClient(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Envia mensagens ao LLM e retorna o conteúdo da resposta."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Gera embedding de um texto. Retorna vetor de floats."""

    @abstractmethod
    async def classify_intent(
        self,
        text: str,
        possible_intents: list[str],
    ) -> str:
        """Classifica a intenção do texto entre as opções fornecidas."""
