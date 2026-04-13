"""
TDD — Sprint 0: contratos do domínio.
Estes testes devem falhar antes de qualquer implementação.
"""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.domain.models import (
    Client,
    ConversationState,
    ConversationStatus,
    FAQEntry,
    IntentType,
    ProfessionType,
    SpecialtyProfile,
)


class TestClient:
    def test_client_is_identified_by_phone_number(self):
        client = Client(phone_number="+5511999999999", name="João Silva")
        assert client.phone_number == "+5511999999999"
        assert client.name == "João Silva"

    def test_client_has_uuid_id(self):
        client = Client(phone_number="+5511999999999", name="João Silva")
        assert isinstance(client.id, UUID)

    def test_client_has_created_at(self):
        client = Client(phone_number="+5511999999999", name="João Silva")
        assert isinstance(client.created_at, datetime)

    def test_client_phone_number_is_required(self):
        with pytest.raises(ValidationError):
            Client(name="João Silva")

    def test_two_clients_with_same_phone_are_equal(self):
        c1 = Client(phone_number="+5511999999999", name="João")
        c2 = Client(phone_number="+5511999999999", name="João")
        assert c1.phone_number == c2.phone_number


class TestSpecialtyProfile:
    def test_specialty_profile_has_profession_type(self):
        profile = SpecialtyProfile(
            profession_type=ProfessionType.NUTRITIONIST,
            agent_persona="Você é uma nutricionista especializada...",
        )
        assert profile.profession_type == ProfessionType.NUTRITIONIST

    def test_specialty_profile_has_chromadb_collection_name(self):
        profile = SpecialtyProfile(
            profession_type=ProfessionType.NUTRITIONIST,
            agent_persona="Você é uma nutricionista...",
        )
        assert profile.chromadb_collection_name is not None
        assert len(profile.chromadb_collection_name) > 0

    def test_chromadb_collection_name_is_derived_from_id(self):
        profile = SpecialtyProfile(
            profession_type=ProfessionType.NUTRITIONIST,
            agent_persona="Você é uma nutricionista...",
        )
        assert str(profile.id) in profile.chromadb_collection_name

    def test_scheduling_intent_is_in_default_escalation_triggers(self):
        profile = SpecialtyProfile(
            profession_type=ProfessionType.NUTRITIONIST,
            agent_persona="Você é uma nutricionista...",
        )
        assert IntentType.SCHEDULING in profile.escalation_triggers

    def test_specialty_profile_accepts_custom_escalation_triggers(self):
        profile = SpecialtyProfile(
            profession_type=ProfessionType.NUTRITIONIST,
            agent_persona="Você é uma nutricionista...",
            escalation_triggers=[IntentType.SCHEDULING, IntentType.URGENT],
        )
        assert IntentType.URGENT in profile.escalation_triggers

    def test_intake_form_schema_defaults_to_empty(self):
        profile = SpecialtyProfile(
            profession_type=ProfessionType.NUTRITIONIST,
            agent_persona="Você é uma nutricionista...",
        )
        assert isinstance(profile.intake_form_schema, dict)


class TestFAQEntry:
    def test_faq_entry_requires_question_and_answer(self):
        entry = FAQEntry(
            specialty_profile_id="some-profile-id",
            question="Quantas refeições devo fazer por dia?",
            answer="O ideal são de 5 a 6 refeições por dia.",
        )
        assert entry.question == "Quantas refeições devo fazer por dia?"
        assert entry.answer == "O ideal são de 5 a 6 refeições por dia."

    def test_faq_entry_without_question_raises_error(self):
        with pytest.raises(ValidationError):
            FAQEntry(
                specialty_profile_id="some-profile-id",
                answer="O ideal são de 5 a 6 refeições por dia.",
            )

    def test_faq_entry_is_active_by_default(self):
        entry = FAQEntry(
            specialty_profile_id="some-profile-id",
            question="Posso comer carboidrato à noite?",
            answer="Depende do seu objetivo e metabolismo.",
        )
        assert entry.is_active is True

    def test_faq_entry_has_empty_tags_by_default(self):
        entry = FAQEntry(
            specialty_profile_id="some-profile-id",
            question="O que é IMC?",
            answer="Índice de Massa Corporal.",
        )
        assert entry.tags == []

    def test_faq_entry_has_uuid_id(self):
        entry = FAQEntry(
            specialty_profile_id="some-profile-id",
            question="O que é IMC?",
            answer="Índice de Massa Corporal.",
        )
        assert isinstance(entry.id, UUID)


class TestConversationState:
    def test_conversation_state_starts_as_init(self):
        state = ConversationState(
            client_id="some-client-id",
            specialty_profile_id="some-profile-id",
        )
        assert state.status == ConversationStatus.INIT

    def test_conversation_state_transitions_to_identifying(self):
        state = ConversationState(
            client_id="some-client-id",
            specialty_profile_id="some-profile-id",
        )
        state.transition_to(ConversationStatus.IDENTIFYING_CLIENT)
        assert state.status == ConversationStatus.IDENTIFYING_CLIENT

    def test_conversation_state_transitions_to_routing(self):
        state = ConversationState(
            client_id="some-client-id",
            specialty_profile_id="some-profile-id",
            status=ConversationStatus.IDENTIFYING_CLIENT,
        )
        state.transition_to(ConversationStatus.ROUTING)
        assert state.status == ConversationStatus.ROUTING

    def test_invalid_transition_raises_error(self):
        state = ConversationState(
            client_id="some-client-id",
            specialty_profile_id="some-profile-id",
            status=ConversationStatus.CLOSED,
        )
        with pytest.raises(ValueError, match="Transição inválida"):
            state.transition_to(ConversationStatus.ROUTING)

    def test_scheduling_intent_triggers_escalation(self):
        state = ConversationState(
            client_id="some-client-id",
            specialty_profile_id="some-profile-id",
            status=ConversationStatus.ROUTING,
        )
        state.transition_to(ConversationStatus.ESCALATED, reason="scheduling")
        assert state.status == ConversationStatus.ESCALATED
        assert state.escalation_reason == "scheduling"

    def test_conversation_state_has_session_id(self):
        state = ConversationState(
            client_id="some-client-id",
            specialty_profile_id="some-profile-id",
        )
        assert isinstance(state.session_id, UUID)

    def test_collected_data_starts_empty(self):
        state = ConversationState(
            client_id="some-client-id",
            specialty_profile_id="some-profile-id",
        )
        assert state.collected_data == {}

    def test_last_activity_is_updated_on_transition(self):
        state = ConversationState(
            client_id="some-client-id",
            specialty_profile_id="some-profile-id",
        )
        before = state.last_activity_at
        state.transition_to(ConversationStatus.IDENTIFYING_CLIENT)
        assert state.last_activity_at >= before
