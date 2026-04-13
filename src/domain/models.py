"""
Modelos de domínio — entidades puras, sem dependência de framework.
Usam Pydantic para validação e servem como base para os modelos ORM.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class ProfessionType(StrEnum):
    NUTRITIONIST = "NUTRITIONIST"
    PSYCHOLOGIST = "PSYCHOLOGIST"
    PHYSIOTHERAPIST = "PHYSIOTHERAPIST"
    DENTIST = "DENTIST"


class IntentType(StrEnum):
    FAQ = "FAQ"
    SCHEDULING = "SCHEDULING"
    URGENT = "URGENT"
    INTAKE = "INTAKE"
    UNKNOWN = "UNKNOWN"


class ConversationStatus(StrEnum):
    INIT = "INIT"
    IDENTIFYING_CLIENT = "IDENTIFYING_CLIENT"
    ROUTING = "ROUTING"
    FAQ_ANSWERING = "FAQ_ANSWERING"
    INTAKE_COLLECTION = "INTAKE_COLLECTION"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    FOLLOW_UP = "FOLLOW_UP"
    CLOSED = "CLOSED"


_VALID_TRANSITIONS: dict[ConversationStatus, set[ConversationStatus]] = {
    ConversationStatus.INIT: {ConversationStatus.IDENTIFYING_CLIENT},
    ConversationStatus.IDENTIFYING_CLIENT: {ConversationStatus.ROUTING},
    ConversationStatus.ROUTING: {
        ConversationStatus.FAQ_ANSWERING,
        ConversationStatus.INTAKE_COLLECTION,
        ConversationStatus.ESCALATED,
    },
    ConversationStatus.FAQ_ANSWERING: {
        ConversationStatus.ROUTING,
        ConversationStatus.ESCALATED,
        ConversationStatus.RESOLVED,
    },
    ConversationStatus.INTAKE_COLLECTION: {
        ConversationStatus.ROUTING,
        ConversationStatus.ESCALATED,
        ConversationStatus.RESOLVED,
    },
    ConversationStatus.ESCALATED: {ConversationStatus.RESOLVED},
    ConversationStatus.RESOLVED: {ConversationStatus.FOLLOW_UP, ConversationStatus.CLOSED},
    ConversationStatus.FOLLOW_UP: {ConversationStatus.CLOSED},
    ConversationStatus.CLOSED: set(),
}


class Client(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    phone_number: str
    name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"frozen": False}


class SpecialtyProfile(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    profession_type: ProfessionType
    agent_persona: str
    intake_form_schema: dict[str, Any] = Field(default_factory=dict)
    escalation_triggers: list[IntentType] = Field(
        default_factory=lambda: [IntentType.SCHEDULING]
    )
    chromadb_collection_name: str = Field(default="")

    model_config = {"frozen": False}

    @model_validator(mode="after")
    def set_collection_name(self) -> Self:
        if not self.chromadb_collection_name:
            self.chromadb_collection_name = f"faq_{self.id}"
        return self


class FAQEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    specialty_profile_id: str
    question: str
    answer: str
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"frozen": False}


class Professional(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    specialty_profile_id: UUID

    model_config = {"frozen": False}


class ConversationState(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    client_id: str
    specialty_profile_id: str
    status: ConversationStatus = ConversationStatus.INIT
    current_agent: str | None = None
    context_window: list[dict[str, Any]] = Field(default_factory=list)
    collected_data: dict[str, Any] = Field(default_factory=dict)
    escalation_reason: str | None = None
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"frozen": False}

    def transition_to(
        self,
        new_status: ConversationStatus,
        reason: str | None = None,
    ) -> None:
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Transição inválida: {self.status} → {new_status}. "
                f"Permitidas: {[s.value for s in allowed]}"
            )
        self.status = new_status
        self.last_activity_at = datetime.now(UTC)
        if reason is not None:
            self.escalation_reason = reason
