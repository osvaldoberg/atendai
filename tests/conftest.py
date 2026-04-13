"""
Fixtures globais reutilizáveis em todos os testes.
"""

import pytest

from src.domain.models import (
    Client,
    ConversationState,
    FAQEntry,
    IntentType,
    ProfessionType,
    SpecialtyProfile,
)
from tests.mocks import MockLLMClient, MockVectorStore, MockWhatsAppGateway


@pytest.fixture
def nutritionist_profile() -> SpecialtyProfile:
    return SpecialtyProfile(
        profession_type=ProfessionType.NUTRITIONIST,
        agent_persona=(
            "Você é uma assistente virtual de uma clínica de nutrição. "
            "Responda dúvidas sobre alimentação de forma clara e acolhedora. "
            "Nunca substitua a consulta com o profissional."
        ),
        intake_form_schema={
            "age": {"type": "integer", "label": "Idade"},
            "weight_kg": {"type": "float", "label": "Peso (kg)"},
            "height_cm": {"type": "float", "label": "Altura (cm)"},
            "goal": {"type": "string", "label": "Objetivo"},
        },
        escalation_triggers=[IntentType.SCHEDULING, IntentType.URGENT],
    )


@pytest.fixture
def sample_client() -> Client:
    return Client(phone_number="+5511999999999", name="Maria Oliveira")


@pytest.fixture
def sample_conversation(sample_client: Client, nutritionist_profile: SpecialtyProfile) -> ConversationState:
    return ConversationState(
        client_id=str(sample_client.id),
        specialty_profile_id=str(nutritionist_profile.id),
    )


@pytest.fixture
def sample_faq_entry(nutritionist_profile: SpecialtyProfile) -> FAQEntry:
    return FAQEntry(
        specialty_profile_id=str(nutritionist_profile.id),
        question="Quantas refeições devo fazer por dia?",
        answer="O ideal são de 5 a 6 refeições por dia, respeitando seu ritmo e rotina.",
        tags=["alimentação", "rotina"],
    )


@pytest.fixture
def mock_whatsapp() -> MockWhatsAppGateway:
    return MockWhatsAppGateway()


@pytest.fixture
def mock_vector_store() -> MockVectorStore:
    return MockVectorStore()


@pytest.fixture
def mock_llm() -> MockLLMClient:
    return MockLLMClient()
