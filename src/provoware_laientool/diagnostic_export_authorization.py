"""Non-visual two-stage authorization for local diagnostic export.

I30 adds no GUI/CLI adapter. The session binds both confirmations to one exact
I26 ExportPreparation and may invoke the I28 writer at most once.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import secrets
from typing import Callable

from .diagnostic_export import ExportWriteResult, write_diagnostic_export
from .diagnostic_export_plan import ExportPlan, ExportPreparation

OPEN = "OPEN"
CONFIRMED_STAGE_1 = "CONFIRMED_STAGE_1"
AUTHORIZED = "AUTHORIZED"
CANCELLED = "CANCELLED"
BLOCKED_INVALID = "BLOCKED_INVALID"
BLOCKED_SEQUENCE = "BLOCKED_SEQUENCE"
BLOCKED_STALE = "BLOCKED_STALE"
BLOCKED_REPLAY = "BLOCKED_REPLAY"


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    status: str
    fingerprint: str | None = None
    request: "AuthorizedExportRequest | None" = None
    errors: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AuthorizedExportRequest:
    session_id: str
    fingerprint: str
    payload: bytes
    plan: ExportPlan


@dataclass(frozen=True, slots=True)
class AuthorizationExecution:
    status: str
    writer_result: ExportWriteResult | None = None
    errors: tuple[str, ...] = ()


def preparation_fingerprint(preparation: ExportPreparation) -> str | None:
    """Return a stable fingerprint only for an intact, non-authorized I26 plan."""
    if (
        preparation.status != "PASS"
        or preparation.payload is None
        or preparation.plan is None
    ):
        return None

    payload = preparation.payload
    plan = preparation.plan
    actual_digest = hashlib.sha256(payload).hexdigest()
    if len(payload) != plan.payload_size_bytes or actual_digest != plan.payload_sha256:
        return None
    if plan.overwrite_allowed or plan.write_enabled:
        return None

    canonical = json.dumps(
        {
            "final_path": plan.final_path,
            "export_format": plan.export_format,
            "payload_size_bytes": plan.payload_size_bytes,
            "payload_sha256": plan.payload_sha256,
            "overwrite_allowed": plan.overwrite_allowed,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class DiagnosticExportAuthorizationSession:
    """Process-local, fail-closed, one-shot authorization state machine."""

    def __init__(self, preparation: ExportPreparation) -> None:
        fingerprint = preparation_fingerprint(preparation)
        if fingerprint is None:
            raise ValueError("Nur eine intakte I26-PASS-Vorbereitung darf autorisiert werden.")
        assert preparation.payload is not None and preparation.plan is not None
        self._session_id = secrets.token_hex(16)
        self._fingerprint = fingerprint
        self._payload = preparation.payload
        self._plan = preparation.plan
        self._stage = 0
        self._cancelled = False
        self._consumed = False
        self._issued_request: AuthorizedExportRequest | None = None

    @property
    def fingerprint(self) -> str:
        return self._fingerprint

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    @property
    def consumed(self) -> bool:
        return self._consumed

    def _matches(self, current: ExportPreparation) -> bool:
        return preparation_fingerprint(current) == self._fingerprint

    def cancel(self) -> AuthorizationDecision:
        if self._consumed:
            return AuthorizationDecision(
                BLOCKED_REPLAY,
                self._fingerprint,
                errors=("Autorisierung wurde bereits verbraucht.",),
            )
        self._cancelled = True
        self._issued_request = None
        return AuthorizationDecision(CANCELLED, self._fingerprint)

    def confirm_stage1(self, current: ExportPreparation) -> AuthorizationDecision:
        if self._cancelled:
            return AuthorizationDecision(CANCELLED, self._fingerprint)
        if self._consumed:
            return AuthorizationDecision(BLOCKED_REPLAY, self._fingerprint)
        if self._stage != 0:
            return AuthorizationDecision(
                BLOCKED_SEQUENCE,
                self._fingerprint,
                errors=("Bestätigung 1 ist in diesem Zustand nicht zulässig.",),
            )
        if not self._matches(current):
            return AuthorizationDecision(
                BLOCKED_STALE,
                self._fingerprint,
                errors=("Exportzustand hat sich seit der Vorschau verändert.",),
            )
        self._stage = 1
        return AuthorizationDecision(CONFIRMED_STAGE_1, self._fingerprint)

    def confirm_stage2(self, current: ExportPreparation) -> AuthorizationDecision:
        if self._cancelled:
            return AuthorizationDecision(CANCELLED, self._fingerprint)
        if self._consumed:
            return AuthorizationDecision(BLOCKED_REPLAY, self._fingerprint)
        if self._stage != 1:
            return AuthorizationDecision(
                BLOCKED_SEQUENCE,
                self._fingerprint,
                errors=("Bestätigung 2 erfordert zuerst Bestätigung 1.",),
            )
        if not self._matches(current):
            self._stage = 0
            self._issued_request = None
            return AuthorizationDecision(
                BLOCKED_STALE,
                self._fingerprint,
                errors=("Exportzustand hat sich geändert; beide Bestätigungen sind neu erforderlich.",),
            )

        request = AuthorizedExportRequest(
            session_id=self._session_id,
            fingerprint=self._fingerprint,
            payload=self._payload,
            plan=self._plan,
        )
        self._stage = 2
        self._issued_request = request
        return AuthorizationDecision(AUTHORIZED, self._fingerprint, request=request)

    def execute(
        self,
        request: AuthorizedExportRequest,
        *,
        writer: Callable[[bytes, ExportPlan], ExportWriteResult] = write_diagnostic_export,
    ) -> AuthorizationExecution:
        if self._cancelled:
            return AuthorizationExecution(CANCELLED)
        if self._consumed:
            return AuthorizationExecution(
                BLOCKED_REPLAY,
                errors=("Autorisierung darf nur einmal verwendet werden.",),
            )
        if self._stage != 2 or self._issued_request is None:
            return AuthorizationExecution(
                BLOCKED_SEQUENCE,
                errors=("Der Export besitzt keine vollständige Doppelbestätigung.",),
            )
        if request != self._issued_request or request.session_id != self._session_id:
            return AuthorizationExecution(
                BLOCKED_STALE,
                errors=("Autorisierungsanforderung gehört nicht zu dieser Sitzung.",),
            )

        current = ExportPreparation("PASS", (), request.payload, request.plan)
        if preparation_fingerprint(current) != self._fingerprint:
            return AuthorizationExecution(
                BLOCKED_STALE,
                errors=("Autorisierungsanforderung wurde nach der Bestätigung verändert.",),
            )

        self._consumed = True
        authorized_plan = replace(request.plan, write_enabled=True)
        result = writer(request.payload, authorized_plan)
        return AuthorizationExecution(result.status, writer_result=result)
