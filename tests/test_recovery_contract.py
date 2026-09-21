from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from provoware_laientool.recovery_contract import (
    STATE_APPLIED,
    STATE_APPLYING,
    STATE_FAILED,
    STATE_INTERRUPTED,
    STATE_PREPARED,
    STATE_RECOVERED,
    STATE_RECOVERING,
    STATE_UNDO_REQUESTED,
    UNDO_COPY,
    UNDO_MOVE,
    JournalSnapshot,
    RecoveryContract,
    crash_guidance,
    transition,
    validate_journal_snapshot,
    validate_recovery_contract,
)


class RecoveryContractTests(unittest.TestCase):
    def test_contract_is_immutable_and_valid(self) -> None:
        contract = RecoveryContract(
            preview_item_id="op-001",
            operation="move",
            reversible=True,
            undo_strategy=UNDO_MOVE,
        )
        self.assertEqual(validate_recovery_contract(contract), ())
        with self.assertRaises(FrozenInstanceError):
            contract.reversible = False  # type: ignore[misc]

    def test_journal_requirement_cannot_be_disabled(self) -> None:
        contract = RecoveryContract(
            preview_item_id="op-001",
            operation="move",
            reversible=True,
            undo_strategy=UNDO_MOVE,
            journal_required=False,
        )
        self.assertIn(
            "Schreibende Zukunftsaktion darf Journal-Pflicht nicht deaktivieren.",
            validate_recovery_contract(contract),
        )

    def test_mismatched_undo_strategy_is_rejected(self) -> None:
        contract = RecoveryContract(
            preview_item_id="op-001",
            operation="move",
            reversible=True,
            undo_strategy=UNDO_COPY,
        )
        errors = validate_recovery_contract(contract)
        self.assertTrue(
            any("Undo-Strategie passt nicht zu move" in error for error in errors)
        )

    def test_non_reversible_contract_is_rejected(self) -> None:
        contract = RecoveryContract(
            preview_item_id="op-001",
            operation="move",
            reversible=False,
            undo_strategy=UNDO_MOVE,
        )
        self.assertIn(
            "Recovery-Vertrag muss Reversibilität erwarten.",
            validate_recovery_contract(contract),
        )


class JournalTests(unittest.TestCase):
    def test_failed_snapshot_requires_error_reason(self) -> None:
        snapshot = JournalSnapshot(
            "j-1",
            "plan-1",
            "op-001",
            STATE_FAILED,
            1,
            last_error=None,
        )
        self.assertIn(
            "FAILED benötigt einen dokumentierten Fehlergrund.",
            validate_journal_snapshot(snapshot),
        )

    def test_attempt_must_start_at_one(self) -> None:
        snapshot = JournalSnapshot(
            "j-1",
            "plan-1",
            "op-001",
            STATE_PREPARED,
            0,
        )
        self.assertIn(
            "Journal-Versuchszähler muss mindestens 1 sein.",
            validate_journal_snapshot(snapshot),
        )


class TransitionTests(unittest.TestCase):
    def test_happy_path_and_undo_path_are_explicit(self) -> None:
        path = (
            (STATE_PREPARED, STATE_APPLYING),
            (STATE_APPLYING, STATE_APPLIED),
            (STATE_APPLIED, STATE_UNDO_REQUESTED),
            (STATE_UNDO_REQUESTED, STATE_RECOVERING),
            (STATE_RECOVERING, STATE_RECOVERED),
        )
        for current, target in path:
            self.assertTrue(transition(current, target).allowed)

    def test_dangerous_skips_are_blocked(self) -> None:
        self.assertFalse(transition(STATE_PREPARED, STATE_APPLIED).allowed)
        self.assertFalse(transition(STATE_APPLIED, STATE_RECOVERED).allowed)
        self.assertFalse(transition(STATE_FAILED, STATE_APPLYING).allowed)

    def test_interrupted_can_only_recover_or_fail(self) -> None:
        self.assertTrue(transition(STATE_INTERRUPTED, STATE_RECOVERING).allowed)
        self.assertTrue(transition(STATE_INTERRUPTED, STATE_FAILED).allowed)
        self.assertFalse(transition(STATE_INTERRUPTED, STATE_APPLYING).allowed)


class CrashMatrixTests(unittest.TestCase):
    def test_no_state_allows_automatic_retry(self) -> None:
        for state in (
            STATE_PREPARED,
            STATE_APPLYING,
            STATE_APPLIED,
            STATE_UNDO_REQUESTED,
            STATE_RECOVERING,
            STATE_INTERRUPTED,
            STATE_RECOVERED,
            STATE_FAILED,
        ):
            self.assertFalse(crash_guidance(state).may_retry_automatically)

    def test_applying_and_recovering_have_unknown_effect(self) -> None:
        self.assertFalse(crash_guidance(STATE_APPLYING).effect_known)
        self.assertFalse(crash_guidance(STATE_RECOVERING).effect_known)

    def test_unknown_state_fails_closed(self) -> None:
        guidance = crash_guidance("mystery")
        self.assertFalse(guidance.effect_known)
        self.assertFalse(guidance.may_retry_automatically)
        self.assertIn("fail-closed", guidance.action)


if __name__ == "__main__":
    unittest.main()
