"""Data-only plugin boundary for B09/I34.

This module deliberately defines no loader, installer, entry-point discovery,
network access or persistence. It only validates future plugin metadata against
the existing PROVOWARE capability registry.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from .capability_registry import (
    SAFETY_READ_ONLY,
    STATUS_READY,
    get_use_case,
    list_use_cases,
)

PLUGIN_API_VERSION = "1"
PLUGIN_STATUS_DISABLED = "DISABLED"
VALID_PLUGIN_STATUSES = {PLUGIN_STATUS_DISABLED}
_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_VERSION_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}(?:[-+][A-Za-z0-9._-]+)?$")


@dataclass(frozen=True, slots=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    api_version: str
    requested_use_cases: tuple[str, ...]
    status: str = PLUGIN_STATUS_DISABLED
    auto_install: bool = False
    auto_enable: bool = False
    network_required: bool = False
    entrypoint: str | None = None


@dataclass(frozen=True, slots=True)
class PluginValidation:
    status: str
    errors: tuple[str, ...]
    approved_use_cases: tuple[str, ...]


def approved_plugin_use_cases() -> tuple[str, ...]:
    return tuple(
        sorted(
            entry.id
            for entry in list_use_cases()
            if entry.status == STATUS_READY and entry.safety_class == SAFETY_READ_ONLY
        )
    )


def validate_plugin_manifest(manifest: PluginManifest) -> PluginValidation:
    errors: list[str] = []
    approved: list[str] = []

    if not _ID_PATTERN.fullmatch(manifest.plugin_id):
        errors.append("Plugin-ID ist ungültig.")
    if not manifest.name.strip():
        errors.append("Plugin-Name fehlt.")
    if not _VERSION_PATTERN.fullmatch(manifest.version):
        errors.append("Plugin-Version ist ungültig.")
    if manifest.api_version != PLUGIN_API_VERSION:
        errors.append(f"Plugin-API-Version {manifest.api_version!r} ist nicht unterstützt.")
    if manifest.status not in VALID_PLUGIN_STATUSES:
        errors.append("Plugins dürfen in I34 nur DISABLED sein.")
    if manifest.auto_install:
        errors.append("Auto-Install ist verboten.")
    if manifest.auto_enable:
        errors.append("Auto-Aktivierung ist verboten.")
    if manifest.network_required:
        errors.append("Plugins dürfen in I34 keinen Netzwerkbedarf deklarieren.")
    if manifest.entrypoint is not None:
        errors.append("Ausführbare Plugin-Entry-Points sind in I34 gesperrt.")

    if len(manifest.requested_use_cases) != len(set(manifest.requested_use_cases)):
        errors.append("Doppelte Capability-Anforderung ist verboten.")

    for use_case_id in manifest.requested_use_cases:
        entry = get_use_case(use_case_id)
        if entry is None:
            errors.append(f"Unbekannter Use-Case: {use_case_id}")
            continue
        if entry.status != STATUS_READY:
            errors.append(f"Use-Case ist nicht READY: {use_case_id}")
            continue
        if entry.safety_class != SAFETY_READ_ONLY:
            errors.append(f"Use-Case ist nicht read-only: {use_case_id}")
            continue
        approved.append(use_case_id)

    return PluginValidation(
        status="PASS" if not errors else "BLOCKED",
        errors=tuple(errors),
        approved_use_cases=tuple(sorted(approved)),
    )
