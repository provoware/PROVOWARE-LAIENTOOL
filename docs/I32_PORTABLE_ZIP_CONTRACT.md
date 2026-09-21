# I32 – Portable ZIP / Fremdpfad / Offline-Paketvertrag

**Status:** Portable-Source-ZIP implementiert; vollständig frische Offline-GUI noch nicht behauptet.

I32 erzeugt ein deterministisches ZIP mit `start.sh` als kanonischem Einstieg, Manifest mit SHA-256/Größe und einer `PROVOWARE.desktop`-Klickoberfläche, die ausschließlich `start.sh --gui` delegiert.

Automatisch geprüft werden: zwei byte-identische Builds, Manifest/Hashes, Ausschluss von `.venv`/Git/Buildresten, ausführbarer Starter, Entpacken in einen Fremdpfad mit Leerzeichen/Unicode, Offline-`--help` und fail-closed Offline-`--check` ohne Mutation.

Das ZIP enthält bewusst kein eingebettetes Venv und keine PySide6-Wheels. Hilfe und Check funktionieren offline; eine erstmalige GUI-Einrichtung ohne bereits verfügbare Abhängigkeiten ist Gegenstand eines späteren Entscheids.

Nicht-Ziele: DEB/AppImage/Snap/Flatpak, Systeminstallation, eingebettetes Python, automatische Desktop-Installation, Änderungen an I25/I31 Human-Gates.
