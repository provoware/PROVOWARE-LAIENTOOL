"""GitHub Actions safety and reproducibility checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

Fail = Callable[[str], None]


def check_workflows(root: Path, fail: Fail) -> None:
    for workflow in (root / ".github" / "workflows").glob("*.y*ml"):
        text = workflow.read_text(encoding="utf-8")
        if re.search(r"(?m)^permissions:\s*$", text) is None:
            fail(f"Workflow ohne explizite permissions: {workflow.relative_to(root)}")
        if re.search(r"(?m)^\s{2,}timeout-minutes:\s*[1-9][0-9]*\s*$", text) is None:
            fail(f"Workflow ohne Job-Timeout: {workflow.relative_to(root)}")
        if re.search(r"(?mi)^\s*continue-on-error:\s*true\s*$", text):
            fail(f"Workflow darf Fehler nicht pauschal ignorieren: {workflow.relative_to(root)}")
        if re.search(r"(?m)^concurrency:\s*$", text) is None:
            fail(f"Workflow ohne Concurrency-Schutz: {workflow.relative_to(root)}")
        if re.search(r"(?mi)^\s{2}cancel-in-progress:\s*true\s*$", text) is None:
            fail(f"Workflow ohne Abbruch veralteter Runs: {workflow.relative_to(root)}")
        if workflow.name in {"i25-gui-evidence.yml", "i31-export-evidence.yml", "portable-package.yml"}:
            if re.search(r"(?m)^\s{2}push:\s*$", text) is None or "- main" not in text:
                fail(f"{workflow.name} muss relevante Änderungen auch nach Merge auf main prüfen")
        for action in re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", text):
            if action.startswith("./"):
                continue
            ref = action.rsplit("@", 1)[-1] if "@" in action else ""
            if not re.fullmatch(r"[0-9a-fA-F]{40}", ref):
                fail(f"Action nicht auf Commit-SHA gepinnt: {action}")
