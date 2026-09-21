"""Immutable B06 recovery/journal state contract.

Domain-only: no filesystem writes, no journal persistence, no executor.
"""

from __future__ import annotations

from dataclasses import dataclass

from .preview_model import ACTION_COPY, ACTION_MOVE, ACTION_TRASH

STATE_PREPARED = "prepared"
STATE_APPLYING = "applying"
STATE_APPLIED = "applied"
STATE_UNDO_REQUESTED = "undo-requested"
STATE_RECOVERING = "recovering"
STATE_RECOVERED = "recovered"
STATE_INTERRUPTED = "interrupted"
STATE_FAILED = "failed"

VALID_STATES = {
    STATE_PREPARED,
    STATE_APPLYING,
    STATE_APPLIED,
    STATE_UNDO_REQUESTED,
    STATE_RECOVERING,
    STATE_RECOVERED,
    STATE_INTERRUPTED,
    STATE_FAILED,
}

UNDO_COPY = "remove-created-copy"
UNDO_MOVE = "move-back"
UNDO_TRASH = "restore-from-trash"
VALID_UNDO_STRATEGIES = {UNDO_COPY, UNDO_MOVE, UNDO_TRASH}
EXPECTED_UNDO_BY_OPERATION = {
    ACTION_COPY: UNDO_COPY,
    ACTION_MOVE: UNDO_MOVE,
    ACTION_TRASH: UNDO_TRASH,
}

_ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    STATE_PREPARED: frozenset({STATE_APPLYING, STATE_FAILED}),
    STATE_APPLYING: frozenset({STATE_APPLIED, STATE_INTERRUPTED, STATE_FAILED}),
    STATE_APPLIED: frozenset({STATE_UNDO_REQUESTED}),
    STATE_UNDO_REQUESTED: frozenset({STATE_RECOVERING}),
    STATE_RECOVERING: frozenset({STATE_RECOVERED, STATE_INTERRUPTED, STATE_FAILED}),
    STATE_INTERRUPTED: frozenset({STATE_RECOVERING, STATE_FAILED}),
    STATE_FAILED: frozenset(),
    STATE_RECOVERED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class RecoveryContract:
    preview_item_id: str
    operation: str
    reversible: bool
    undo_strategy: str
    journal_required: bool = True


@dataclass(frozen=True, slots=True)
class JournalSnapshot:
    entry_id: str
    preview_plan_id: str
    preview_item_id: str
    state: str
    attempt: int
    last_error: str | None = None


@dataclass(frozen=True, slots=True)
class TransitionDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class CrashGuidance:
    state: str
    effect_known: bool
    may_retry_automatically: bool
    action: str


def validate_recovery_contract(contract: RecoveryContract) -> tuple[str, ...]:
    errors: list[str] = []
    if not contract.preview_item_id.strip():
        errors.append("Recovery-Vertrag benötigt eine Preview-Aktions-ID.")
    if not contract.reversible:
        errors.append("Recovery-Vertrag muss Reversibilität erwarten.")
    if contract.operation not in EXPECTED_UNDO_BY_OPERATION:
        errors.append(f"Unbekannte Recovery-Operation: {contract.operation}")
    if contract.undo_strategy not in VALID_UNDO_STRATEGIES:
        errors.append(f"Unbekannte Undo-Strategie: {contract.undo_strategy}")
    elif contract.operation in EXPECTED_UNDO_BY_OPERATION:
        expected = EXPECTED_UNDO_BY_OPERATION[contract.operation]
        if contract.undo_strategy != expected:
            errors.append(
                f"Undo-Strategie passt nicht zu {contract.operation}: "
                f"erwartet {expected}, erhalten {contract.undo_strategy}"
            )
    if not contract.journal_required:
        errors.append("Schreibende Zukunftsaktion darf Journal-Pflicht nicht deaktivieren.")
    return tuple(errors)


def validate_journal_snapshot(snapshot: JournalSnapshot) -> tuple[str, ...]:
    errors: list[str] = []
    if not snapshot.entry_id.strip():
        errors.append("Journal-Eintrag benötigt eine ID.")
    if not snapshot.preview_plan_id.strip():
        errors.append("Journal-Eintrag benötigt eine Preview-Plan-ID.")
    if not snapshot.preview_item_id.strip():
        errors.append("Journal-Eintrag benötigt eine Preview-Aktions-ID.")
    if snapshot.state not in VALID_STATES:
        errors.append(f"Unbekannter Recovery-Zustand: {snapshot.state}")
    if snapshot.attempt < 1:
        errors.append("Journal-Versuchszähler muss mindestens 1 sein.")
    if snapshot.state == STATE_FAILED and not (snapshot.last_error or "").strip():
        errors.append("FAILED benötigt einen dokumentierten Fehlergrund.")
    return tuple(errors)


def transition(current: str, target: str) -> TransitionDecision:
    if current not in VALID_STATES:
        return TransitionDecision(False, f"Unbekannter Ausgangszustand: {current}")
    if target not in VALID_STATES:
        return TransitionDecision(False, f"Unbekannter Zielzustand: {target}")
    if target in _ALLOWED_TRANSITIONS[current]:
        return TransitionDecision(True, f"Übergang {current} → {target} ist erlaubt.")
    return TransitionDecision(False, f"Übergang {current} → {target} ist gesperrt.")


def crash_guidance(state: str) -> CrashGuidance:
    """Return fail-closed guidance for restart/recovery orchestration."""
    if state == STATE_PREPARED:
        return CrashGuidance(
            state,
            effect_known=True,
            may_retry_automatically=False,
            action="Keine Wirkung annehmen; vor neuem Versuch Preview und Pfadgrenzen erneut prüfen.",
        )
    if state == STATE_APPLYING:
        return CrashGuidance(
            state,
            effect_known=False,
            may_retry_automatically=False,
            action="Wirkung ist unklar; Ist-Zustand prüfen, niemals blind wiederholen.",
        )
    if state == STATE_APPLIED:
        return CrashGuidance(
            state,
            effect_known=True,
            may_retry_automatically=False,
            action="Wirkung als ausgeführt behandeln; bei Wunsch kontrolliertes Undo anbieten.",
        )
    if state == STATE_UNDO_REQUESTED:
        return CrashGuidance(
            state,
            effect_known=True,
            may_retry_automatically=False,
            action="Undo-Wunsch erhalten; Zustand erneut prüfen, bevor Recovery startet.",
        )
    if state == STATE_RECOVERING:
        return CrashGuidance(
            state,
            effect_known=False,
            may_retry_automatically=False,
            action="Recovery wurde unterbrochen; Ist-Zustand prüfen, niemals blind fortsetzen.",
        )
    if state == STATE_INTERRUPTED:
        return CrashGuidance(
            state,
            effect_known=False,
            may_retry_automatically=False,
            action="Unterbrechung dokumentieren; manuell/reproduzierbar entscheiden, ob Recovery fortgesetzt wird.",
        )
    if state == STATE_RECOVERED:
        return CrashGuidance(
            state,
            effect_known=True,
            may_retry_automatically=False,
            action="Recovery abgeschlossen; keine weitere Aktion automatisch ausführen.",
        )
    if state == STATE_FAILED:
        return CrashGuidance(
            state,
            effect_known=False,
            may_retry_automatically=False,
            action="Fehlerzustand einfrieren; Ursache dokumentieren und keine automatische Wiederholung starten.",
        )
    return CrashGuidance(
        state,
        effect_known=False,
        may_retry_automatically=False,
        action="Unbekannter Zustand; fail-closed stoppen.",
    )
