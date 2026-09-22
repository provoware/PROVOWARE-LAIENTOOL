"""Machine-readable regression manifest checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

Fail = Callable[[str], None]


def check_regression_manifest(root: Path, fail: Fail) -> None:
    regression_manifest = root / "docs" / "REGRESSIONSMANIFEST.json"
    if not regression_manifest.is_file():
        return
    try:
        manifest_data = json.loads(regression_manifest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        fail(f"Regressionsmanifest ist nicht gültig: {exc}")
        return

    families = manifest_data.get("familien", [])
    identifiers = [family.get("kennung") for family in families if isinstance(family, dict)]
    if manifest_data.get("schema_version") != 1 or not families:
        fail("Regressionsmanifest braucht Schema 1 und mindestens eine Fehlerfamilie")
    if len(identifiers) != len(set(identifiers)) or any(not item for item in identifiers):
        fail("Regressionsmanifest enthält leere oder doppelte Kennungen")
    for family in families:
        if not isinstance(family, dict):
            fail("Regressionsmanifest enthält eine ungültige Fehlerfamilie")
            continue
        tests = family.get("pruefungen", [])
        keywords = family.get("suchwoerter", [])
        if not family.get("anzeige") or not keywords or not tests:
            fail(f"Regressionsfamilie {family.get('kennung')!r} ist unvollständig")
            continue
        for test_path in tests:
            if not isinstance(test_path, str) or not (root / test_path).is_file():
                fail(f"Regressionsfamilie {family.get('kennung')!r}: Prüfung fehlt: {test_path}")
