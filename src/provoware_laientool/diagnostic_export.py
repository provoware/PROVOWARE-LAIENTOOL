"""Create-only diagnostic export writer.

I28 intentionally exposes no GUI/CLI adapter and no registry capability.
The function accepts only an already validated payload and ExportPlan. A write
is attempted only when the immutable plan is explicitly authorized with
write_enabled=True by a higher layer.
"""

from __future__ import annotations

from dataclasses import dataclass
import errno
import hashlib
import os
from pathlib import Path
import secrets

from .diagnostic_export_plan import ExportPlan

PASS = "PASS"
BLOCKED_NOT_AUTHORIZED = "BLOCKED_NOT_AUTHORIZED"
BLOCKED_TARGET_EXISTS = "BLOCKED_TARGET_EXISTS"
BLOCKED_TARGET_UNSAFE = "BLOCKED_TARGET_UNSAFE"
BLOCKED_PAYLOAD_INVALID = "BLOCKED_PAYLOAD_INVALID"
WRITE_PERMISSION_ERROR = "WRITE_PERMISSION_ERROR"
WRITE_NO_SPACE = "WRITE_NO_SPACE"
WRITE_PARTIAL_REMAINS = "WRITE_PARTIAL_REMAINS"
WRITE_COMMIT_RACE = "WRITE_COMMIT_RACE"
WRITE_VERIFY_FAILED = "WRITE_VERIFY_FAILED"
WRITE_IO_ERROR = "WRITE_IO_ERROR"


@dataclass(frozen=True, slots=True)
class ExportWriteResult:
    status: str
    final_path: str
    partial_path: str | None
    bytes_written: int
    payload_sha256: str | None
    errors: tuple[str, ...]


def _result(
    status: str,
    final_path: Path,
    *,
    partial_path: Path | None = None,
    bytes_written: int = 0,
    payload_sha256: str | None = None,
    error: str | None = None,
) -> ExportWriteResult:
    return ExportWriteResult(
        status=status,
        final_path=str(final_path),
        partial_path=str(partial_path) if partial_path is not None else None,
        bytes_written=bytes_written,
        payload_sha256=payload_sha256,
        errors=(error,) if error else (),
    )


def _cleanup_owned_partial(partial_path: Path) -> bool:
    try:
        os.unlink(partial_path)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return True


def _verify_payload_file(partial_path: Path, plan: ExportPlan) -> bool:
    try:
        if partial_path.stat().st_size != plan.payload_size_bytes:
            return False
        digest = hashlib.sha256()
        with open(partial_path, "rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest() == plan.payload_sha256
    except OSError:
        return False


def _validate_runtime_contract(payload: bytes, plan: ExportPlan) -> tuple[str, Path, Path]:
    target_dir = Path(plan.target_dir)
    final_path = Path(plan.final_path)
    if not plan.write_enabled:
        return BLOCKED_NOT_AUTHORIZED, target_dir, final_path
    if plan.overwrite_allowed:
        return BLOCKED_TARGET_UNSAFE, target_dir, final_path
    if not target_dir.is_absolute() or target_dir.is_symlink() or not target_dir.is_dir():
        return BLOCKED_TARGET_UNSAFE, target_dir, final_path
    try:
        resolved_dir = target_dir.resolve(strict=True)
    except OSError:
        return BLOCKED_TARGET_UNSAFE, target_dir, final_path
    if resolved_dir != target_dir:
        return BLOCKED_TARGET_UNSAFE, target_dir, final_path
    if Path(plan.filename).name != plan.filename:
        return BLOCKED_TARGET_UNSAFE, target_dir, final_path
    if final_path != target_dir / plan.filename or final_path.parent != target_dir:
        return BLOCKED_TARGET_UNSAFE, target_dir, final_path
    if final_path.exists() or final_path.is_symlink():
        return BLOCKED_TARGET_EXISTS, target_dir, final_path
    digest = hashlib.sha256(payload).hexdigest()
    if len(payload) != plan.payload_size_bytes or digest != plan.payload_sha256:
        return BLOCKED_PAYLOAD_INVALID, target_dir, final_path
    return PASS, target_dir, final_path


def write_diagnostic_export(payload: bytes, plan: ExportPlan) -> ExportWriteResult:
    """Write one new diagnostic file without overwrite or automatic retry."""
    status, target_dir, final_path = _validate_runtime_contract(payload, plan)
    if status != PASS:
        return _result(status, final_path)

    payload_digest = hashlib.sha256(payload).hexdigest()
    partial_path = target_dir / f".PROVOWARE-Diagnose.partial-{secrets.token_hex(12)}"
    directory_fd: int | None = None
    partial_fd: int | None = None
    partial_created = False
    bytes_written = 0

    try:
        directory_fd = os.open(
            target_dir,
            os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
        )
        partial_fd = os.open(
            partial_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
        )
        partial_created = True
        while bytes_written < len(payload):
            written = os.write(partial_fd, payload[bytes_written:])
            if written <= 0:
                raise OSError(errno.EIO, "os.write lieferte keinen Fortschritt")
            bytes_written += written
        os.fsync(partial_fd)
        os.close(partial_fd)
        partial_fd = None

        if not _verify_payload_file(partial_path, plan):
            if not _cleanup_owned_partial(partial_path):
                return _result(
                    WRITE_PARTIAL_REMAINS,
                    final_path,
                    partial_path=partial_path,
                    bytes_written=bytes_written,
                    payload_sha256=payload_digest,
                    error="Partial-Datei konnte nach fehlgeschlagener Verifikation nicht entfernt werden.",
                )
            return _result(
                WRITE_VERIFY_FAILED,
                final_path,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
                error="Hash oder Größe der Partial-Datei stimmt nicht mit dem ExportPlan überein.",
            )

        if final_path.exists() or final_path.is_symlink():
            _cleanup_owned_partial(partial_path)
            return _result(
                WRITE_COMMIT_RACE,
                final_path,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
                error="Finales Ziel entstand nach dem Preflight.",
            )

        try:
            os.link(partial_path, final_path, follow_symlinks=False)
        except FileExistsError:
            _cleanup_owned_partial(partial_path)
            return _result(
                WRITE_COMMIT_RACE,
                final_path,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
                error="Finales Ziel wurde von einem konkurrierenden Lauf belegt.",
            )

        os.fsync(directory_fd)
        try:
            os.unlink(partial_path)
        except OSError as exc:
            os.fsync(directory_fd)
            return _result(
                WRITE_PARTIAL_REMAINS,
                final_path,
                partial_path=partial_path,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
                error=f"Finale Datei ist veröffentlicht, Partial-Datei blieb zurück: {exc.__class__.__name__}",
            )
        os.fsync(directory_fd)
        return _result(
            PASS,
            final_path,
            bytes_written=bytes_written,
            payload_sha256=payload_digest,
        )

    except PermissionError as exc:
        if partial_created:
            _cleanup_owned_partial(partial_path)
        return _result(
            WRITE_PERMISSION_ERROR,
            final_path,
            partial_path=partial_path if partial_path.exists() else None,
            bytes_written=bytes_written,
            payload_sha256=payload_digest,
            error=exc.__class__.__name__,
        )
    except FileExistsError:
        return _result(
            WRITE_COMMIT_RACE,
            final_path,
            bytes_written=bytes_written,
            payload_sha256=payload_digest,
            error="Partial-Dateiname kollidierte; kein automatischer Retry.",
        )
    except OSError as exc:
        cleanup_ok = True
        if partial_created:
            cleanup_ok = _cleanup_owned_partial(partial_path)
        if not cleanup_ok:
            return _result(
                WRITE_PARTIAL_REMAINS,
                final_path,
                partial_path=partial_path,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
                error=f"Fehler und Partial-Cleanup fehlgeschlagen: {exc.__class__.__name__}",
            )
        mapped = WRITE_NO_SPACE if exc.errno == errno.ENOSPC else WRITE_IO_ERROR
        return _result(
            mapped,
            final_path,
            bytes_written=bytes_written,
            payload_sha256=payload_digest,
            error=exc.__class__.__name__,
        )
    finally:
        if partial_fd is not None:
            try:
                os.close(partial_fd)
            except OSError:
                pass
        if directory_fd is not None:
            try:
                os.close(directory_fd)
            except OSError:
                pass
