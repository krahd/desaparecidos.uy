import pytest

from desaparecidos.conversation import (
    Certainty,
    ClaimStatus,
    ConversationSession,
    Speaker,
)


def test_claim_requires_capture_consent():
    session = ConversationSession()
    turn = session.add_turn(Speaker.PARTICIPANT, "I remember a blue house.")

    with pytest.raises(ValueError, match="capture consent"):
        session.add_claim("There was a blue house.", [turn.id])


def test_claim_preserves_participant_turn_provenance():
    session = ConversationSession(consent_to_capture=True)
    participant = session.add_turn(Speaker.PARTICIPANT, "I think it was near the station.")
    agent = session.add_turn(Speaker.AGENT, "Do you remember which station?")

    claim = session.add_claim(
        "The remembered location may have been near a station.",
        [participant.id, agent.id],
        certainty=Certainty.UNCERTAIN,
    )

    assert claim.source_turn_ids == [participant.id, agent.id]
    assert claim.certainty == Certainty.UNCERTAIN
    assert claim.status == ClaimStatus.ACTIVE


def test_claim_cannot_be_grounded_only_in_agent_turns():
    session = ConversationSession(consent_to_capture=True)
    agent = session.add_turn(Speaker.AGENT, "Perhaps it happened in 1975?")

    with pytest.raises(ValueError, match="participant turn"):
        session.add_claim("It happened in 1975.", [agent.id])


def test_correction_keeps_original_claim_and_links_replacement():
    session = ConversationSession(consent_to_capture=True)
    first_turn = session.add_turn(Speaker.PARTICIPANT, "I remember it being in winter.")
    original = session.add_claim("The event was in winter.", [first_turn.id])

    correction_turn = session.add_turn(
        Speaker.PARTICIPANT,
        "No, I want to correct that: I am not sure which season it was.",
    )
    replacement = session.correct_claim(
        original.id,
        "The participant is unsure which season it was.",
        [correction_turn.id],
        certainty=Certainty.UNCERTAIN,
    )

    assert original.status == ClaimStatus.CORRECTED
    assert original.corrected_by == replacement.id
    assert replacement.status == ClaimStatus.ACTIVE
    assert replacement.certainty == Certainty.UNCERTAIN


def test_withdraw_session_prevents_further_capture():
    session = ConversationSession(consent_to_capture=True)
    turn = session.add_turn(Speaker.PARTICIPANT, "Synthetic test memory.")
    claim = session.add_claim("Synthetic test claim.", [turn.id])

    session.withdraw_session()

    assert session.is_withdrawn
    assert claim.status == ClaimStatus.WITHDRAWN
    assert claim.withdrawal_reason == "session withdrawn"
    with pytest.raises(ValueError, match="session has been withdrawn"):
        session.add_turn(Speaker.PARTICIPANT, "Another turn")
