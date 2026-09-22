# I37 – Repository-Hygiene und Quality-Gate-Refactor

## Ziel

Altbranches gegen `main` fachlich klassifizieren und den gewachsenen Repository-Gate ohne Regelverlust in kleine Verantwortungen zerlegen.

## Branch-Forensik

| Branch | Befund | Entscheidung |
| --- | --- | --- |
| `design/i24-diagnostic-export-writer` | 0 Unique-Commits, vollständig hinter `main` | entbehrlich |
| `security/i34-precommitted-wheel-lock` | 0 Unique-Commits, vollständig hinter `main` | entbehrlich |
| `domain/i12-preview-contract` | alter Preview-Modell-Pfad; aktuelle `preview_model.py` + Tests auf `main` vorhanden | superseded |
| `application/i21-transfer-preview` | alter reiner Transfer-Preview-Builder; aktueller `transfer_application.py` + I21-Tests auf `main` vorhanden | superseded |
| `security/i27-diagnostic-writer-guard` | alter Guard-Stand; gehärteter I27-Stand auf `main` vorhanden | superseded |
| `security/i28-diagnostic-writer-testlab` | alter Testlab-PR; I28 bereits auf `main` vorhanden, PR #43 geschlossen | superseded |
| `packaging/i32-portable-zip` | parallele ZIP-Architektur; aktueller I32-Paketpfad auf `main` vorhanden, PR #49 bereits superseded | superseded |
| `security/i33-offline-wheelhouse-lock` | enthält **zusätzliche** vorab festgeschriebene Wheel-Dateinamen, Größen und SHA-256 | **KEEP bis Security-Salvage** |

## Sicherheitsfund I33

Der aktuelle I33-Stand auf `main` prüft Wheel-Namen, Versionen, Plattform, Manifest, Größen und SHA-256 innerhalb des erzeugten Pakets. Der alte Branch enthält zusätzlich eine **vor dem Paketbau fest eingecheckte Hash-Baseline** (`wheelhouse-lock-linux-x86_64.json`).

Diese Invariante ist nicht gleichwertig auf `main` vorhanden und darf deshalb beim Aufräumen nicht verloren gehen. Sie wird als eigener P0-Folgeblock auf aktuellem `main` neu umgesetzt; der alte Branch wird bis dahin nicht als entbehrlich behandelt.

## Quality-Gate-Refactor

`scripts/repo_quality.py` bleibt der stabile Einstiegspunkt und ruft nun getrennte Prüffamilien auf:

- `repo_quality_checks/structure.py` – Pflichtstruktur, Starter, Baseline und TODO;
- `repo_quality_checks/regression.py` – Regressionsmanifest;
- `repo_quality_checks/source.py` – Python-Syntax und Tkinter-Grenze;
- `repo_quality_checks/workflows.py` – GitHub-Actions-Verträge;
- `repo_quality_checks/documentation.py` – Register, Iterationsindex, Links, Status und Text-Hygiene.

Die bisherigen PASS-Ausgaben und Exit-Semantik des Orchestrators bleiben unverändert.

## Nicht-Ziele

- keine Produktlogik;
- keine Schreibfreigabe;
- keine Änderung an I25/I31 Human-Gates;
- kein blindes Mergen alter Branches;
- kein Löschen des I33-Branches vor Übernahme der einzigartigen Sicherheitsinvariante.
