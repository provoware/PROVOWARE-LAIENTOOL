from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from provoware_laientool.capability_registry import (
    SAFETY_EXPLICIT_WRITE_CONFIRMATION,
    STATUS_OPEN,
    get_use_case,
    validate_registry,
)
from provoware_laientool.diagnostic_export import ExportWriteResult, PASS
from provoware_laientool.diagnostic_export_authorization import (
    AUTHORIZED,
    BLOCKED_REPLAY,
    BLOCKED_SEQUENCE,
    BLOCKED_STALE,
    CANCELLED,
    CONFIRMED_STAGE_1,
    DiagnosticExportAuthorizationSession,
    AuthorizedExportRequest,
    preparation_fingerprint,
)
from provoware_laientool.diagnostic_export_plan import FORMAT_JSON, ExportPreparation, prepare_diagnostic_export
from provoware_laientool.diagnostics import DiagnosticEntry, DiagnosticReport


def report() -> DiagnosticReport:
    return DiagnosticReport(
        schema_version="1",
        collection_status="PASS",
        health_status="PASS",
        entries=(DiagnosticEntry("platform", "system", "Linux"),),
        warnings=(),
        redaction_applied=True,
        write_paths_enabled=False,
    )


class I30AuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.prep = prepare_diagnostic_export(
            report(),
            target_dir=self.root,
            export_format=FORMAT_JSON,
            filename="PROVOWARE-Diagnose-I30.json",
        )
        self.assertEqual(self.prep.status, "PASS")
        assert self.prep.plan is not None and self.prep.payload is not None

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_registry_is_open_and_has_dedicated_write_safety_class(self) -> None:
        self.assertEqual(validate_registry(), ())
        entry = get_use_case("diagnostics.export_local")
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.status, STATUS_OPEN)
        self.assertEqual(entry.safety_class, SAFETY_EXPLICIT_WRITE_CONFIRMATION)
        self.assertFalse(entry.gui_available)
        self.assertFalse(entry.cli_available)
        self.assertTrue(entry.preview_required)

    def test_fingerprint_is_stable_for_same_preparation(self) -> None:
        self.assertEqual(preparation_fingerprint(self.prep), preparation_fingerprint(self.prep))

    def test_fingerprint_rejects_payload_tampering(self) -> None:
        assert self.prep.payload is not None
        tampered = ExportPreparation("PASS", (), self.prep.payload + b"x", self.prep.plan)
        self.assertIsNone(preparation_fingerprint(tampered))

    def test_stage2_before_stage1_is_blocked(self) -> None:
        session = DiagnosticExportAuthorizationSession(self.prep)
        self.assertEqual(session.confirm_stage2(self.prep).status, BLOCKED_SEQUENCE)

    def test_changed_plan_after_stage1_invalidates_both_confirmations(self) -> None:
        session = DiagnosticExportAuthorizationSession(self.prep)
        self.assertEqual(session.confirm_stage1(self.prep).status, CONFIRMED_STAGE_1)
        assert self.prep.plan is not None
        stale = ExportPreparation(
            "PASS", (), self.prep.payload,
            replace(self.prep.plan, final_path=str(self.root / "anders.json"), filename="anders.json"),
        )
        self.assertEqual(session.confirm_stage2(stale).status, BLOCKED_STALE)
        self.assertEqual(session.confirm_stage2(self.prep).status, BLOCKED_SEQUENCE)
        self.assertEqual(session.confirm_stage1(self.prep).status, CONFIRMED_STAGE_1)

    def test_cancel_before_confirmation_is_side_effect_free(self) -> None:
        session = DiagnosticExportAuthorizationSession(self.prep)
        self.assertEqual(session.cancel().status, CANCELLED)
        self.assertEqual(session.confirm_stage1(self.prep).status, CANCELLED)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_cancel_after_stage1_prevents_stage2(self) -> None:
        session = DiagnosticExportAuthorizationSession(self.prep)
        session.confirm_stage1(self.prep)
        self.assertEqual(session.cancel().status, CANCELLED)
        self.assertEqual(session.confirm_stage2(self.prep).status, CANCELLED)

    def test_two_confirmations_issue_immutable_request(self) -> None:
        session = DiagnosticExportAuthorizationSession(self.prep)
        self.assertEqual(session.confirm_stage1(self.prep).status, CONFIRMED_STAGE_1)
        decision = session.confirm_stage2(self.prep)
        self.assertEqual(decision.status, AUTHORIZED)
        self.assertIsNotNone(decision.request)
        assert decision.request is not None
        self.assertEqual(decision.request.fingerprint, session.fingerprint)
        self.assertFalse(decision.request.plan.write_enabled)

    def test_writer_is_called_exactly_once_and_only_with_authorized_plan(self) -> None:
        session = DiagnosticExportAuthorizationSession(self.prep)
        session.confirm_stage1(self.prep)
        request = session.confirm_stage2(self.prep).request
        assert request is not None
        fake = ExportWriteResult(PASS, request.plan.final_path, None, len(request.payload), request.plan.payload_sha256, ())
        writer = Mock(return_value=fake)

        first = session.execute(request, writer=writer)
        second = session.execute(request, writer=writer)

        self.assertEqual(first.status, PASS)
        self.assertEqual(second.status, BLOCKED_REPLAY)
        writer.assert_called_once()
        payload, authorized_plan = writer.call_args.args
        self.assertEqual(payload, request.payload)
        self.assertTrue(authorized_plan.write_enabled)
        self.assertFalse(authorized_plan.overwrite_allowed)

    def test_request_from_another_session_is_blocked_without_writer(self) -> None:
        first = DiagnosticExportAuthorizationSession(self.prep)
        first.confirm_stage1(self.prep)
        request = first.confirm_stage2(self.prep).request
        assert request is not None

        second = DiagnosticExportAuthorizationSession(self.prep)
        second.confirm_stage1(self.prep)
        second.confirm_stage2(self.prep)
        writer = Mock()
        result = second.execute(request, writer=writer)
        self.assertEqual(result.status, BLOCKED_STALE)
        writer.assert_not_called()

    def test_tampered_authorized_request_is_blocked_without_writer(self) -> None:
        session = DiagnosticExportAuthorizationSession(self.prep)
        session.confirm_stage1(self.prep)
        request = session.confirm_stage2(self.prep).request
        assert request is not None
        forged = AuthorizedExportRequest(
            session_id=request.session_id,
            fingerprint=request.fingerprint,
            payload=request.payload + b"x",
            plan=request.plan,
        )
        writer = Mock()
        result = session.execute(forged, writer=writer)
        self.assertEqual(result.status, BLOCKED_STALE)
        writer.assert_not_called()

    def test_session_rejects_already_write_enabled_plan(self) -> None:
        assert self.prep.plan is not None
        unsafe = ExportPreparation("PASS", (), self.prep.payload, replace(self.prep.plan, write_enabled=True))
        with self.assertRaises(ValueError):
            DiagnosticExportAuthorizationSession(unsafe)


if __name__ == "__main__":
    unittest.main()
