"""I28 diagnostic export writer testlab.

This is the only product module allowed to perform a filesystem write.
It is intentionally not registered in GUI/CLI and accepts only an explicitly
write-enabled I26 ExportPlan plus already-validated payload bytes.
"""

from __future__ import annotations

import errno
import hashlib
import os
import secrets
import stat
from dataclasses import dataclass
from pathlib import Path

from .diagnostic_export_plan import FORMAT_JSON, FORMAT_TEXT, ExportPlan

VALID_FORMATS = {FORMAT_JSON, FORMAT_TEXT}
PARTIAL_PREFIX = ".PROVOWARE-Diagnose.partial-"


@dataclass(frozen=True, slots=True)
class ExportWriteResult:
    status: str
    errors: tuple[str, ...]
    committed: bool
    final_path: str | None
    partial_path: str | None
    bytes_written: int
    payload_sha256: str | None


def _result(
    status: str,
    *errors: str,
    committed: bool = False,
    final_path: Path | None = None,
    partial_path: Path | None = None,
    bytes_written: int = 0,
    payload_sha256: str | None = None,
) -> ExportWriteResult:
    return ExportWriteResult(
        status=status,
        errors=tuple(errors),
        committed=committed,
        final_path=str(final_path) if final_path is not None else None,
        partial_path=str(partial_path) if partial_path is not None else None,
        bytes_written=bytes_written,
        payload_sha256=payload_sha256,
    )


def _same_inode(left: os.stat_result, right: os.stat_result) -> bool:
    return left.st_dev == right.st_dev and left.st_ino == right.st_ino


def _validate_contract(payload: bytes, plan: ExportPlan) -> tuple[str, ...]:
    errors: list[str] = []

    if not isinstance(payload, bytes):
        errors.append("Writer akzeptiert ausschließlich bytes-Payload.")
        return tuple(errors)

    if not plan.write_enabled:
        errors.append("ExportPlan besitzt keine explizite Schreibfreigabe.")

    if plan.overwrite_allowed:
        errors.append("Overwrite-Freigabe ist im Diagnose-Writer verboten.")

    if plan.export_format not in VALID_FORMATS:
        errors.append("Exportformat ist für den Writer nicht freigegeben.")

    filename = plan.filename
    if not filename or Path(filename).name != filename or "/" in filename or "\\" in filename:
        errors.append("Export-Dateiname darf keinen Pfad enthalten.")

    expected_suffix = ".json" if plan.export_format == FORMAT_JSON else ".txt"
    if plan.export_format in VALID_FORMATS and not filename.lower().endswith(expected_suffix):
        errors.append(f"Export-Dateiname muss auf {expected_suffix} enden.")

    if len(payload) != plan.payload_size_bytes:
        errors.append("Payload-Größe stimmt nicht mit ExportPlan überein.")

    digest = hashlib.sha256(payload).hexdigest()
    if digest != plan.payload_sha256:
        errors.append("Payload-Hash stimmt nicht mit ExportPlan überein.")

    target_dir = Path(plan.target_dir)
    if target_dir.is_symlink():
        errors.append("Zielordner ist ein Symlink.")
    elif not target_dir.exists():
        errors.append("Zielordner existiert nicht.")
    elif not target_dir.is_dir():
        errors.append("Zielpfad ist kein Ordner.")
    else:
        try:
            resolved_dir = target_dir.resolve(strict=True)
        except OSError as exc:
            errors.append(f"Zielordner konnte nicht sicher aufgelöst werden: {exc}")
        else:
            expected_final = resolved_dir / filename
            if Path(plan.final_path) != expected_final:
                errors.append("Finalpfad stimmt nicht exakt mit Zielordner und Dateiname überein.")

    return tuple(errors)


def _cleanup_owned_partial(
    partial_name: str,
    target_dir_fd: int,
) -> str | None:
    try:
        os.unlink(partial_name, dir_fd=target_dir_fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        return f"Eigene Partial-Datei konnte nicht entfernt werden: {exc}"
    return None


def write_diagnostic_export(
    payload: bytes,
    plan: ExportPlan,
) -> ExportWriteResult:
    """Write one validated diagnostic export without overwrite or retry."""
    errors = _validate_contract(payload, plan)
    final_path = Path(plan.final_path)
    if errors:
        return _result("BLOCKED", *errors, final_path=final_path)

    target_dir = Path(plan.target_dir)
    final_name = plan.filename
    payload_digest = hashlib.sha256(payload).hexdigest()
    partial_name = f"{PARTIAL_PREFIX}{secrets.token_hex(12)}"
    partial_path = target_dir / partial_name

    target_dir_fd: int | None = None
    partial_fd: int | None = None
    partial_created = False
    committed = False
    bytes_written = 0

    try:
        before_stat = os.stat(target_dir, follow_symlinks=False)
        target_dir_fd = os.open(
            target_dir,
            os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
        )
        opened_stat = os.fstat(target_dir_fd)
        if not stat.S_ISDIR(opened_stat.st_mode) or not _same_inode(before_stat, opened_stat):
            return _result(
                "BLOCKED",
                "Zielordner hat sich zwischen Prüfung und Öffnen verändert.",
                final_path=final_path,
            )

        try:
            os.stat(final_name, dir_fd=target_dir_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            return _result(
                "BLOCKED",
                "Finale Zieldatei existiert bereits; Overwrite ist verboten.",
                final_path=final_path,
            )

        partial_fd = os.open(
            partial_name,
            os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW,
            0o600,
            dir_fd=target_dir_fd,
        )
        partial_created = True

        view = memoryview(payload)
        while bytes_written < len(view):
            written = os.write(partial_fd, view[bytes_written:])
            if written <= 0:
                raise OSError(errno.EIO, "os.write lieferte keinen Fortschritt")
            bytes_written += written

        os.fsync(partial_fd)

        partial_stat = os.fstat(partial_fd)
        if partial_stat.st_size != plan.payload_size_bytes:
            cleanup_error = _cleanup_owned_partial(partial_name, target_dir_fd)
            partial_created = False if cleanup_error is None else True
            messages = ["Partial-Größe stimmt nach Write nicht mit ExportPlan überein."]
            if cleanup_error:
                messages.append(cleanup_error)
            return _result(
                "FAILED",
                *messages,
                final_path=final_path,
                partial_path=partial_path if partial_created else None,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
            )

        os.lseek(partial_fd, 0, os.SEEK_SET)
        hasher = hashlib.sha256()
        verified_size = 0
        while True:
            chunk = os.read(partial_fd, 65536)
            if not chunk:
                break
            verified_size += len(chunk)
            hasher.update(chunk)

        if verified_size != plan.payload_size_bytes or hasher.hexdigest() != plan.payload_sha256:
            cleanup_error = _cleanup_owned_partial(partial_name, target_dir_fd)
            partial_created = False if cleanup_error is None else True
            messages = ["Partial-Payload stimmt nach Write nicht mit ExportPlan überein."]
            if cleanup_error:
                messages.append(cleanup_error)
            return _result(
                "FAILED",
                *messages,
                final_path=final_path,
                partial_path=partial_path if partial_created else None,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
            )

        os.close(partial_fd)
        partial_fd = None

        current_stat = os.stat(target_dir, follow_symlinks=False)
        if not _same_inode(opened_stat, current_stat):
            cleanup_error = _cleanup_owned_partial(partial_name, target_dir_fd)
            partial_created = False if cleanup_error is None else True
            messages = ["Zielordner hat sich vor dem Publish verändert."]
            if cleanup_error:
                messages.append(cleanup_error)
            return _result(
                "BLOCKED",
                *messages,
                final_path=final_path,
                partial_path=partial_path if partial_created else None,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
            )

        try:
            os.link(
                partial_name,
                final_name,
                src_dir_fd=target_dir_fd,
                dst_dir_fd=target_dir_fd,
                follow_symlinks=False,
            )
        except FileExistsError:
            cleanup_error = _cleanup_owned_partial(partial_name, target_dir_fd)
            partial_created = False if cleanup_error is None else True
            messages = ["Finales Ziel entstand vor dem Publish; No-clobber hat blockiert."]
            if cleanup_error:
                messages.append(cleanup_error)
            return _result(
                "BLOCKED",
                *messages,
                final_path=final_path,
                partial_path=partial_path if partial_created else None,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
            )

        committed = True
        os.fsync(target_dir_fd)

        cleanup_error = _cleanup_owned_partial(partial_name, target_dir_fd)
        if cleanup_error is not None:
            return _result(
                "OPEN",
                "Finaler Export ist veröffentlicht, aber Partial-Cleanup ist unvollständig.",
                cleanup_error,
                committed=True,
                final_path=final_path,
                partial_path=partial_path,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
            )
        partial_created = False

        os.fsync(target_dir_fd)

        after_stat = os.stat(target_dir, follow_symlinks=False)
        if not _same_inode(opened_stat, after_stat):
            return _result(
                "OPEN",
                "Finaler Export wurde veröffentlicht, Zielordnerpfad hat sich danach verändert.",
                committed=True,
                final_path=final_path,
                bytes_written=bytes_written,
                payload_sha256=payload_digest,
            )

        return _result(
            "PASS",
            committed=True,
            final_path=final_path,
            bytes_written=bytes_written,
            payload_sha256=payload_digest,
        )

    except PermissionError as exc:
        if partial_created and target_dir_fd is not None:
            cleanup_error = _cleanup_owned_partial(partial_name, target_dir_fd)
            partial_created = cleanup_error is not None
        else:
            cleanup_error = None
        messages = [f"Dateisystem-Berechtigung blockiert den Export: {exc}"]
        if cleanup_error:
            messages.append(cleanup_error)
        return _result(
            "FAILED" if partial_created or bytes_written else "BLOCKED",
            *messages,
            committed=committed,
            final_path=final_path,
            partial_path=partial_path if partial_created else None,
            bytes_written=bytes_written,
            payload_sha256=payload_digest if bytes_written else None,
        )
    except OSError as exc:
        if partial_created and target_dir_fd is not None and not committed:
            cleanup_error = _cleanup_owned_partial(partial_name, target_dir_fd)
            partial_created = cleanup_error is not None
        else:
            cleanup_error = None

        status = "OPEN" if committed else "FAILED"
        messages = [f"Dateisystemfehler beim Diagnose-Export: {exc}"]
        if cleanup_error:
            messages.append(cleanup_error)
        return _result(
            status,
            *messages,
            committed=committed,
            final_path=final_path,
            partial_path=partial_path if partial_created else None,
            bytes_written=bytes_written,
            payload_sha256=payload_digest if bytes_written else None,
        )
    finally:
        if partial_fd is not None:
            try:
                os.close(partial_fd)
            except OSError:
                pass
        if target_dir_fd is not None:
            try:
                os.close(target_dir_fd)
            except OSError:
                pass
