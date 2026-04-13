"""
Modelos ORM SQLAlchemy mapeados a partir das entidades de domínio.
Separados dos modelos Pydantic para manter o domínio limpo.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ClientORM(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    conversations: Mapped[list["ConversationORM"]] = relationship(back_populates="client")


class SpecialtyProfileORM(Base):
    __tablename__ = "specialty_profiles"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    profession_type: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_persona: Mapped[str] = mapped_column(Text, nullable=False)
    intake_form_schema: Mapped[dict] = mapped_column(JSONB, default=dict)
    escalation_triggers: Mapped[list] = mapped_column(JSONB, default=list)
    chromadb_collection_name: Mapped[str] = mapped_column(String(255), nullable=False)

    faq_entries: Mapped[list["FAQEntryORM"]] = relationship(back_populates="specialty_profile")
    professionals: Mapped[list["ProfessionalORM"]] = relationship(back_populates="specialty_profile")


class FAQEntryORM(Base):
    __tablename__ = "faq_entries"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    specialty_profile_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("specialty_profiles.id"), nullable=False, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    specialty_profile: Mapped["SpecialtyProfileORM"] = relationship(back_populates="faq_entries")


class ProfessionalORM(Base):
    __tablename__ = "professionals"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty_profile_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("specialty_profiles.id"), nullable=False
    )

    specialty_profile: Mapped["SpecialtyProfileORM"] = relationship(back_populates="professionals")


class ConversationORM(Base):
    __tablename__ = "conversations"

    session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    client_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("clients.id"), nullable=False, index=True
    )
    specialty_profile_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("specialty_profiles.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="INIT")
    current_agent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    context_window: Mapped[list] = mapped_column(JSONB, default=list)
    collected_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    escalation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    client: Mapped["ClientORM"] = relationship(back_populates="conversations")
