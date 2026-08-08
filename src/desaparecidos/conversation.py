"""Core state model for conversational collective-memory capture.

This module intentionally contains no LLM provider, speech service, or persistence
backend. It defines the auditable state transitions that a future real-time
conversational interface must preserve: utterance provenance, uncertainty,
correction, and withdrawal.

Tests and examples must use synthetic or already-public material. Do not place
real participant testimony in the repository.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4


class Speaker(StrEnum):
    PARTICIPANT = "participant"
    AGENT = "agent"
    SYSTEM = "system"


class Certainty(StrEnum):
    REMEMBERED = "remembered"
    UNCERTAIN = "uncertain"
    HEARSAY = "heard-from-others"
    UNKNOWN = "unknown"


class ClaimStatus(StrEnum):
    ACTIVE = "active"
    CORRECTED = "corrected"
    WITHDRAWN = "withdrawn"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class Turn:
    id: str
    speaker: Speaker
    text: str
    created_at: str


@dataclass(slots=True)
class MemoryClaim:
    id: str
    text: str
    source_turn_ids: list[str]
    certainty: Certainty = Certainty.UNKNOWN
    status: ClaimStatus = ClaimStatus.ACTIVE
    created_at: str = field(default_factory=_utcnow)
    corrected_by: str | None = None
    withdrawal_reason: str | None = None


@dataclass(slots=True)
class ConversationSession:
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_utcnow)
    consent_to_capture: bool = False
    turns: list[Turn] = field(default_factory=list)
    claims: list[MemoryClaim] = field(default_factory=list)
    withdrawn_at: str | None = None

    @property
    def is_withdrawn(self) -> bool:
        return self.withdrawn_at is not None

    def _require_active(self) -> None:
        if self.is_withdrawn:
            raise ValueError("session has been withdrawn")

    def add_turn(self, speaker: Speaker, text: str) -> Turn:
        self._require_active()
        clean = text.strip()
        if not clean:
            raise ValueError("turn text cannot be empty")
        turn = Turn(
            id=str(uuid4()),
            speaker=speaker,
            text=clean,
            created_at=_utcnow(),
        )
        self.turns.append(turn)
        return turn

    def add_claim(
        self,
        text: str,
        source_turn_ids: list[str],
        certainty: Certainty = Certainty.UNKNOWN,
    ) -> MemoryClaim:
        self._require_active()
        if not self.consent_to_capture:
            raise ValueError("capture consent is required before creating claims")
        clean = text.strip()
        if not clean:
            raise ValueError("claim text cannot be empty")
        if not source_turn_ids:
            raise ValueError("claims require at least one source turn")

        turns = {turn.id: turn for turn in self.turns}
        missing = [turn_id for turn_id in source_turn_ids if turn_id not in turns]
        if missing:
            raise ValueError(f"unknown source turn ids: {missing}")
        if not any(turns[turn_id].speaker == Speaker.PARTICIPANT for turn_id in source_turn_ids):
            raise ValueError("claims must be grounded in at least one participant turn")

        claim = MemoryClaim(
            id=str(uuid4()),
            text=clean,
            source_turn_ids=list(dict.fromkeys(source_turn_ids)),
            certainty=certainty,
        )
        self.claims.append(claim)
        return claim

    def correct_claim(
        self,
        claim_id: str,
        replacement_text: str,
        source_turn_ids: list[str],
        certainty: Certainty | None = None,
    ) -> MemoryClaim:
        self._require_active()
        original = self._claim(claim_id)
        if original.status == ClaimStatus.WITHDRAWN:
            raise ValueError("withdrawn claims cannot be corrected")

        replacement = self.add_claim(
            replacement_text,
            source_turn_ids,
            certainty=certainty or original.certainty,
        )
        original.status = ClaimStatus.CORRECTED
        original.corrected_by = replacement.id
        return replacement

    def withdraw_claim(self, claim_id: str, reason: str | None = None) -> None:
        self._require_active()
        claim = self._claim(claim_id)
        claim.status = ClaimStatus.WITHDRAWN
        claim.withdrawal_reason = reason.strip() if reason and reason.strip() else None

    def withdraw_session(self) -> None:
        if self.is_withdrawn:
            return
        self.withdrawn_at = _utcnow()
        for claim in self.claims:
            if claim.status == ClaimStatus.ACTIVE:
                claim.status = ClaimStatus.WITHDRAWN
                claim.withdrawal_reason = "session withdrawn"

    def _claim(self, claim_id: str) -> MemoryClaim:
        for claim in self.claims:
            if claim.id == claim_id:
                return claim
        raise ValueError(f"unknown claim id: {claim_id}")

    def export(self) -> dict:
        """Return an auditable JSON-serialisable session record."""
        return asdict(self)
