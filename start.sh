#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
REQUIREMENTS="$ROOT_DIR/requirements-gui.txt"
WHEELHOUSE="$ROOT_DIR/wheelhouse"
EXPECTED_PYSIDE6="6.11.2"
ACTION="${1:---gui}"
ASSUME_YES=0

if [[ "$ACTION" == "--yes" ]]; then
  ASSUME_YES=1
  ACTION="${2:---gui}"
elif [[ "${2:-}" == "--yes" ]]; then
  ASSUME_YES=1
fi

status() {
  printf '%s\n' "$1"
}

die() {
  printf '🔴 %s\n' "$1" >&2
  exit "${2:-1}"
}

confirm() {
  local message="$1"
  if [[ "$ASSUME_YES" -eq 1 ]]; then
    return 0
  fi

  if command -v kdialog >/dev/null 2>&1 && [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    kdialog --yesno "$message" --title "PROVOWARE Einrichtung"
    return $?
  fi

  printf '%s [j/N]: ' "$message"
  local answer=""
  IFS= read -r answer || return 1
  [[ "$answer" =~ ^([jJ]|[jJ][aA]|[yY]|[yY][eE][sS])$ ]]
}

show_help() {
  cat <<'EOF'
PROVOWARE Venv-Starter

Aufruf:
  ./start.sh --setup       .venv anlegen/prüfen, PySide6 installieren falls bestätigt
  ./start.sh --check       nur prüfen, nichts verändern
  ./start.sh --i17         I17-D automatisch + Chromium-Abnahme starten
  ./start.sh --i17-auto    Alias für --i17
  ./start.sh --i17-offscreen  technische Pipeline ohne Human-Abnahme
  ./start.sh --gui         GUI starten
  ./start.sh --i25-evidence I25 automatisch prüfen + eine finale Chromium-Abnahme
  ./start.sh --i25-offscreen I25 technische Evidence ohne Human-Abnahme
  ./start.sh --i31-evidence I31 GUI+CLI automatisch prüfen + eine finale Human-Abnahme
  ./start.sh --i31-offscreen I31 technische GUI+CLI-Evidence ohne Human-Abnahme
  ./start.sh --i31-cli-evidence I31 Konsolen-Prüfmodus mit synthetischen Daten
  ./start.sh --menu        Konsolenmenü starten
  ./start.sh --preflight   read-only Preflight starten
  ./start.sh --json        read-only Preflight als JSON
  ./start.sh --diagnostics redigierten Diagnose-Snapshot anzeigen
  ./start.sh --diagnostics-json  Diagnose-Snapshot als JSON anzeigen
  ./start.sh --second-device-evidence  Zweitgeräte-Evidence anzeigen
  ./start.sh --second-device-evidence-json  Zweitgeräte-Evidence als JSON anzeigen
  ./start.sh --yes --i17   explizit ohne Rückfrage einrichten und I17 starten

Ohne Option wird --gui verwendet.

Sicherheitsregeln:
- keine sudo-/apt-Aufrufe;
- keine Installation außerhalb von .venv;
- keine stillen Downloads: Installation nur nach Bestätigung oder --yes;
- bestehende .venv wird validiert statt blind überschrieben.
EOF
}

case "$ACTION" in
  --help|-h)
    show_help
    exit 0
    ;;
  --setup|--check|--i17|--i17-auto|--i17-offscreen|--gui|--i25-evidence|--i25-offscreen|--i31-evidence|--i31-offscreen|--i31-cli-evidence|--menu|--preflight|--json|--diagnostics|--diagnostics-json|--second-device-evidence|--second-device-evidence-json)
    ;;
  *)
    show_help
    die "Unbekannte Option: $ACTION" 2
    ;;
esac

cd "$ROOT_DIR"

[[ -f "$REQUIREMENTS" ]] || die "requirements-gui.txt fehlt. Repository ist unvollständig."

BASE_PYTHON="$(command -v python3 || true)"
[[ -n "$BASE_PYTHON" ]] || die "python3 wurde nicht gefunden."

if ! "$BASE_PYTHON" - <<'PY'
import sys
ok = (3, 10) <= sys.version_info[:2] < (3, 15)
print(f"Python: {sys.version.split()[0]} ({sys.executable})")
raise SystemExit(0 if ok else 1)
PY
then
  die "Python muss >= 3.10 und < 3.15 sein."
fi

validate_venv() {
  [[ -x "$VENV_PYTHON" ]] || return 1
  "$VENV_PYTHON" - <<'PY'
import sys
raise SystemExit(0 if sys.prefix != sys.base_prefix else 1)
PY
}

pyside_version() {
  "$VENV_PYTHON" - <<'PY' 2>/dev/null || true
from importlib.metadata import PackageNotFoundError, version
try:
    print(version("PySide6"))
except PackageNotFoundError:
    pass
PY
}

validate_gui_runtime() {
  "$VENV_PYTHON" - <<PY
from importlib.metadata import version
expected = "$EXPECTED_PYSIDE6"
actual = version("PySide6")
if actual != expected:
    raise SystemExit(f"PySide6-Version falsch: {actual}; erwartet: {expected}")
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication
print(f"PySide6: {actual}")
print(f"Qt: {QtCore.qVersion()}")
print("QtWidgets-Import: PASS")
PY
}

if ! validate_venv; then
  if [[ "$ACTION" == "--check" ]]; then
    die ".venv fehlt oder ist ungültig. Nichts verändert." 3
  fi

  status "🟨 Lokale virtuelle Umgebung .venv fehlt."
  confirm "Jetzt .venv ausschließlich im Projektordner anlegen?" || die "Einrichtung abgebrochen. Nichts installiert." 4

  rm -rf -- "$VENV_DIR.tmp"
  if ! "$BASE_PYTHON" -m venv "$VENV_DIR.tmp"; then
    rm -rf -- "$VENV_DIR.tmp"
    die "Venv-Erstellung fehlgeschlagen. Prüfe, ob das venv-Modul für dein Python installiert ist. Es wurde kein sudo/apt ausgeführt." 5
  fi

  [[ -x "$VENV_DIR.tmp/bin/python" ]] || {
    rm -rf -- "$VENV_DIR.tmp"
    die "Venv-Erstellung unvollständig; temporäre Umgebung entfernt." 5
  }

  mv -- "$VENV_DIR.tmp" "$VENV_DIR"
  status "🟢 .venv wurde lokal angelegt."
fi

CURRENT_PYSIDE6="$(pyside_version)"
if [[ "$CURRENT_PYSIDE6" != "$EXPECTED_PYSIDE6" ]]; then
  if [[ "$ACTION" == "--check" ]]; then
    if [[ -z "$CURRENT_PYSIDE6" ]]; then
      die "PySide6 fehlt in .venv. Nichts verändert." 6
    fi
    die "PySide6 ist $CURRENT_PYSIDE6; erwartet wird $EXPECTED_PYSIDE6. Nichts verändert." 6
  fi

  if [[ -z "$CURRENT_PYSIDE6" ]]; then
    status "🟨 PySide6 fehlt in .venv."
  else
    status "🟨 PySide6-Version ist $CURRENT_PYSIDE6; erwartet wird $EXPECTED_PYSIDE6."
  fi

  if [[ -d "$WHEELHOUSE" ]] && compgen -G "$WHEELHOUSE/*.whl" >/dev/null; then
    status "📦 Lokales Offline-Wheelhouse erkannt. Integrität wird geprüft ..."
    "$BASE_PYTHON" "$ROOT_DIR/scripts/verify_wheelhouse_integrity.py" "$ROOT_DIR" || die "Lokales Wheelhouse ist unvollständig, beschädigt oder unerwartet. Nichts installiert." 8
    status "🟢 Wheelhouse-Integrität PASS. Es wird kein Paketindex verwendet."
    confirm "PySide6 $EXPECTED_PYSIDE6 jetzt ausschließlich aus dem lokalen wheelhouse/ in .venv installieren?" || die "Abgebrochen. Keine Paketinstallation durchgeführt." 7
    "$VENV_PYTHON" -m pip install       --disable-pip-version-check       --no-index       --find-links "$WHEELHOUSE"       --requirement "$REQUIREMENTS"
  else
    status "🌐 Kein lokales Wheelhouse vorhanden. PyPI wäre für die bestätigte Installation erforderlich."
    confirm "PySide6 $EXPECTED_PYSIDE6 jetzt nur in .venv aus requirements-gui.txt installieren?" || die "Abgebrochen. Keine Paketinstallation durchgeführt." 7
    "$VENV_PYTHON" -m pip install       --disable-pip-version-check       --requirement "$REQUIREMENTS"
  fi
fi

status "🔎 Validierung der virtuellen Umgebung ..."
validate_venv || die ".venv ist nach Einrichtung nicht als virtuelle Umgebung erkennbar."
validate_gui_runtime || die "PySide6-/Qt-Validierung fehlgeschlagen."

status "🟢 Virtuelle Umgebung bereit: $VENV_DIR"

if [[ "$ACTION" == "--check" || "$ACTION" == "--setup" ]]; then
  status "✅ Einrichtung/Prüfung abgeschlossen."
  exit 0
fi

case "$ACTION" in
  --i17|--i17-auto)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i17_auto_evidence.py"
    ;;
  --i17-offscreen)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i17_auto_evidence.py" --offscreen --auto-only
    ;;
  --gui)
    exec "$VENV_PYTHON" "$ROOT_DIR/start.py" --gui
    ;;
  --i25-evidence)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i25_auto_evidence.py"
    ;;
  --i25-offscreen)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i25_auto_evidence.py" --offscreen --auto-only
    ;;
  --i31-evidence)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i31_auto_evidence.py"
    ;;
  --i31-offscreen)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i31_auto_evidence.py" --offscreen --auto-only
    ;;
  --i31-cli-evidence)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/i31_auto_evidence.py" --cli-demo
    ;;
  --menu)
    exec "$VENV_PYTHON" "$ROOT_DIR/start.py" --menu
    ;;
  --preflight)
    exec "$VENV_PYTHON" "$ROOT_DIR/start.py"
    ;;
  --json)
    exec "$VENV_PYTHON" "$ROOT_DIR/start.py" --json
    ;;
  --diagnostics)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/diagnostic_snapshot.py"
    ;;
  --diagnostics-json)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/diagnostic_snapshot.py" --json
    ;;
  --second-device-evidence)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/second_device_evidence.py"
    ;;
  --second-device-evidence-json)
    exec "$VENV_PYTHON" "$ROOT_DIR/scripts/second_device_evidence.py" --json
    ;;
esac
