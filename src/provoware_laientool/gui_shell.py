"""Optional PySide6 GUI adapter for the read-only shell."""

from __future__ import annotations

from pathlib import Path

from .application_core import (
    TRANSFER_PREVIEW_IDS,
    action_requires_root,
    execute,
    prepare_inventory_view,
    prepare_target_directories,
)
from .inventory_view import InventoryViewSpec, SORT_NAME_ASC
from .capability_registry import list_use_cases
from .ui_themes import THEMES, get_theme, stylesheet


def create_main_window(*, evidence_mode: bool = False):
    """Create the real GUI window without entering the Qt event loop."""
    try:
        from PySide6.QtWidgets import (
            QApplication,
            QComboBox,
            QFrame,
            QFileDialog,
            QDialog,
            QDialogButtonBox,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QPushButton,
            QListWidget,
            QAbstractItemView,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:
        raise RuntimeError(f"PySide6/QtWidgets konnte nicht geladen werden: {exc}") from exc

    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("PROVOWARE LAIENTOOL")
            self.resize(1240, 800)
            self.action_buttons: dict[str, QPushButton] = {}

            root = QWidget()
            root.setObjectName("root")
            outer = QVBoxLayout(root)
            outer.setContentsMargins(18, 18, 18, 18)
            outer.setSpacing(14)

            top = QHBoxLayout()
            brand = QVBoxLayout()
            title = QLabel("PROVOWARE")
            title.setObjectName("title")
            brand.addWidget(title)
            self.header_subtitle = QLabel("Dateien sicher prüfen – Schritt für Schritt.")
            self.header_subtitle.setObjectName("subtitle")
            self.header_subtitle.setWordWrap(True)
            brand.addWidget(self.header_subtitle)
            top.addLayout(brand, 1)
            top.addStretch()

            scale_controls = QVBoxLayout()
            self.scale_label = QLabel("Größe")
            self.scale_label.setObjectName("controlLabel")
            scale_controls.addWidget(self.scale_label)
            self.scale_box = QComboBox()
            self.scale_box.setObjectName("scaleBox")
            self.scale_box.setAccessibleName("Schrift- und Oberflächengröße")
            self.scale_box.setToolTip("Vergrößert Schrift und Bedienelemente.")
            for value in (100, 125, 150, 175, 200):
                self.scale_box.addItem(f"{value} %", value)
            self.scale_box.currentIndexChanged.connect(self.apply_theme)
            scale_controls.addWidget(self.scale_box)
            top.addLayout(scale_controls)

            theme_controls = QVBoxLayout()
            self.theme_label = QLabel("Darstellung")
            self.theme_label.setObjectName("controlLabel")
            theme_controls.addWidget(self.theme_label)
            self.theme_box = QComboBox()
            self.theme_box.setObjectName("themeBox")
            self.theme_box.setAccessibleName("Farbthema")
            self.theme_box.setToolTip("Ändert nur die Farben, nicht die Bedienung.")
            for theme in THEMES:
                self.theme_box.addItem(theme.label, theme.id)
            self.theme_box.currentIndexChanged.connect(self.apply_theme)
            theme_controls.addWidget(self.theme_box)
            top.addLayout(theme_controls)
            outer.addLayout(top)

            safety_card = QFrame()
            safety_card.setObjectName("safetyCard")
            safety_layout = QVBoxLayout(safety_card)
            safety_layout.setContentsMargins(14, 10, 14, 10)
            safety_layout.setSpacing(4)
            self.safety_label = QLabel("🔒 Sicherer Lese-Modus")
            self.safety_label.setObjectName("navTitle")
            self.safety_label.setAccessibleName("Sicherheitsstatus: Sicherer Lese-Modus")
            safety_layout.addWidget(self.safety_label)
            self.safety_detail = QLabel(
                "Es werden keine Dateien verändert. Vorschauen zeigen nur, was später möglich wäre."
            )
            self.safety_detail.setObjectName("subtitle")
            self.safety_detail.setWordWrap(True)
            safety_layout.addWidget(self.safety_detail)
            outer.addWidget(safety_card)

            body = QHBoxLayout()
            body.setSpacing(14)

            sidebar = QFrame()
            sidebar.setObjectName("sidebar")
            side_layout = QVBoxLayout(sidebar)
            side_layout.setContentsMargins(12, 12, 12, 12)
            side_layout.setSpacing(8)

            self.nav_title = QLabel("Was möchtest du tun?")
            self.nav_title.setObjectName("navTitle")
            self.nav_title.setWordWrap(True)
            side_layout.addWidget(self.nav_title)
            self.nav_hint = QLabel(
                "Wähle eine Aufgabe. Die Übersicht bringt dich jederzeit zurück zum Start."
            )
            self.nav_hint.setObjectName("subtitle")
            self.nav_hint.setWordWrap(True)
            side_layout.addWidget(self.nav_hint)

            friendly_labels = {
                "app.overview": "🏠 Start",
                "system.preflight": "🩺 System prüfen",
                "files.preview_trash": "📄 Dateien ansehen",
                "files.preview_copy": "📋 Kopieren prüfen",
                "files.preview_move": "↪ Verschieben prüfen",
                "app.help": "❓ Hilfe",
            }

            for entry in list_use_cases():
                is_ready = entry.gui_available and entry.status == "READY"
                is_i25_evidence = (
                    evidence_mode
                    and entry.gui_available
                    and entry.id in TRANSFER_PREVIEW_IDS
                )
                if not (is_ready or is_i25_evidence):
                    continue
                label = friendly_labels.get(entry.id, entry.label)
                if entry.id in TRANSFER_PREVIEW_IDS and entry.status != "READY":
                    label = f"{label} · Prüfmodus"
                button = QPushButton(label)
                button.setObjectName(f"action-{entry.id}")
                button.setAccessibleName(entry.label)
                button.setToolTip(f"{entry.label} öffnen")
                button.setProperty("active", False)
                button.clicked.connect(
                    lambda checked=False, use_case_id=entry.id: self.show_action(use_case_id)
                )
                self.action_buttons[entry.id] = button
                side_layout.addWidget(button)
            side_layout.addStretch()
            body.addWidget(sidebar, 2)

            content = QFrame()
            content.setObjectName("contentCard")
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(18, 18, 18, 18)
            content_layout.setSpacing(10)

            result_head = QHBoxLayout()
            self.section_title = QLabel("Übersicht")
            self.section_title.setObjectName("title")
            self.section_title.setWordWrap(True)
            result_head.addWidget(self.section_title, 1)

            self.status_label = QLabel("🟢 Bereit")
            self.status_label.setObjectName("statusPill")
            self.status_label.setProperty("status", "pass")
            self.status_label.setAccessibleName("Status: Bereit")
            result_head.addWidget(self.status_label)
            content_layout.addLayout(result_head)

            self.step_hint = QLabel("💡 Tipp: Beginne mit der Übersicht oder prüfe zuerst das System.")
            self.step_hint.setObjectName("stepHint")
            self.step_hint.setWordWrap(True)
            content_layout.addWidget(self.step_hint)

            self.output = QTextEdit()
            self.output.setObjectName("resultOutput")
            self.output.setReadOnly(True)
            self.output.setAccessibleName("Ergebnis und Hilfe")
            content_layout.addWidget(self.output, 1)

            body.addWidget(content, 5)
            outer.addLayout(body, 1)

            self.setCentralWidget(root)
            self._set_stable_tab_order()
            self.show_action_for_root("app.overview", None)
            self.apply_theme()

        def _set_stable_tab_order(self) -> None:
            chain = list(self.keyboard_focus_widgets())
            for first, second in zip(chain, chain[1:]):
                QWidget.setTabOrder(first, second)

        def keyboard_focus_widgets(self):
            return (
                self.scale_box,
                self.theme_box,
                *self.action_buttons.values(),
                self.output,
            )

        def core_widgets(self):
            return (
                self.header_subtitle,
                self.scale_label,
                self.scale_box,
                self.theme_label,
                self.theme_box,
                self.safety_label,
                self.safety_detail,
                self.nav_title,
                self.nav_hint,
                *self.action_buttons.values(),
                self.section_title,
                self.status_label,
                self.step_hint,
                self.output,
            )

        def _set_active_action(self, use_case_id: str) -> None:
            for action_id, button in self.action_buttons.items():
                is_active = action_id == use_case_id
                if button.property("active") != is_active:
                    button.setProperty("active", is_active)
                    button.style().unpolish(button)
                    button.style().polish(button)

        def _set_status(self, status: str) -> None:
            status_text = {
                "PASS": "🟢 Bereit",
                "OPEN": "🟡 Noch offen",
                "BLOCKED": "🔴 Blockiert",
            }.get(status, f"🔵 {status}")
            status_key = {
                "PASS": "pass",
                "OPEN": "open",
                "BLOCKED": "blocked",
            }.get(status, "open")
            self.status_label.setText(status_text)
            self.status_label.setAccessibleName(f"Status: {status_text}")
            self.status_label.setProperty("status", status_key)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)

        def _hint_for_action(self, use_case_id: str, status: str) -> str:
            if status == "BLOCKED":
                return "💡 Nächster Schritt: Lies den Grund vollständig und ändere nichts, bevor er geklärt ist."
            hints = {
                "app.overview": "💡 Tipp: Prüfe zuerst das System. Danach kannst du Dateien sicher ansehen.",
                "system.preflight": "💡 Tipp: Grün bedeutet startklar. Gelbe oder rote Hinweise zuerst lesen.",
                "files.preview_trash": "💡 Tipp: Du siehst nur eine Vorschau. Es wird nichts gelöscht oder verschoben.",
                "files.preview_copy": "💡 Prüfmodus: Quelle, Dateien und Ziel werden nur als Vorschau zusammengestellt.",
                "files.preview_move": "💡 Prüfmodus: Quelle, Dateien und Ziel werden nur als Vorschau zusammengestellt.",
                "app.help": "💡 Tipp: Arbeite die Hilfe von oben nach unten ab. Fachwissen ist nicht nötig.",
            }
            if status == "OPEN":
                return hints.get(
                    use_case_id,
                    "💡 Noch offen: Lies den Hinweis und folge dem dort genannten nächsten Schritt.",
                )
            return hints.get(use_case_id, "💡 Wähle links den nächsten gewünschten Schritt.")

        def _present(self, use_case_id: str, title: str, status: str, body: str) -> None:
            self._set_active_action(use_case_id)
            self.section_title.setText(title)
            self._set_status(status)
            self.step_hint.setText(self._hint_for_action(use_case_id, status))
            self.output.setPlainText(body)
            self.output.verticalScrollBar().setValue(0)

        def set_scale_percent(self, scale_percent: int) -> None:
            index = self.scale_box.findData(scale_percent)
            if index < 0:
                raise ValueError(f"Nicht unterstützte Skalierung: {scale_percent}")
            self.scale_box.setCurrentIndex(index)
            self.apply_theme()

        def apply_theme(self) -> None:
            theme_id = self.theme_box.currentData() or THEMES[0].id
            scale = self.scale_box.currentData() or 100
            QApplication.instance().setStyleSheet(
                stylesheet(get_theme(theme_id), int(scale))
            )

        def _render_result(self, use_case_id: str, root: str | None) -> None:
            result = execute(use_case_id, root=root)
            self._present(use_case_id, result.title, result.status, result.body)

        def show_action_for_root(self, use_case_id: str, root: str | None) -> None:
            self._render_result(use_case_id, root)

        def build_file_selection_dialog(self, preparation):
            dialog = QDialog(self)
            dialog.setWindowTitle("Schritt 2 von 3 · Dateien auswählen")
            dialog.resize(760, 560)
            dialog_layout = QVBoxLayout(dialog)
            step = QLabel("Schritt 2 von 3 · Dateien auswählen")
            step.setObjectName("dialogStep")
            step.setAccessibleName("Schritt 2 von 3: Dateien auswählen")
            dialog_layout.addWidget(step)
            hint = QLabel(
                "Wähle mindestens eine Datei. Mit Strg oder Umschalt kannst du mehrere markieren."
            )
            hint.setObjectName("subtitle")
            hint.setWordWrap(True)
            dialog_layout.addWidget(hint)

            file_list = QListWidget()
            file_list.setObjectName("i25FileSelection")
            file_list.setAccessibleName("Dateien für Transfer-Vorschau")
            file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            for item in preparation.view.items:
                file_list.addItem(f"{item.relative_path}  ·  {item.size_bytes} Byte")
            dialog_layout.addWidget(file_list)

            selection_status = QLabel("0 Dateien ausgewählt")
            selection_status.setObjectName("stepHint")
            selection_status.setAccessibleName("Auswahl: 0 Dateien")
            dialog_layout.addWidget(selection_status)

            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            ok_button = buttons.button(QDialogButtonBox.Ok)
            cancel_button = buttons.button(QDialogButtonBox.Cancel)
            ok_button.setText("Weiter")
            ok_button.setAccessibleName("Weiter zur Zielauswahl")
            cancel_button.setText("Abbrechen")
            cancel_button.setAccessibleName("Auswahl abbrechen")
            ok_button.setEnabled(False)

            def update_selection_status() -> None:
                count = len(file_list.selectedItems())
                ok_button.setEnabled(count > 0)
                label = f"{count} Datei ausgewählt" if count == 1 else f"{count} Dateien ausgewählt"
                selection_status.setText(label)
                selection_status.setAccessibleName(f"Auswahl: {label}")

            file_list.itemSelectionChanged.connect(update_selection_status)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            dialog_layout.addWidget(buttons)
            return dialog, file_list

        def build_target_selection_dialog(self, root: Path):
            preparation = prepare_target_directories(root)
            if preparation.status != "PASS":
                return None, None, preparation

            dialog = QDialog(self)
            dialog.setWindowTitle("Schritt 3 von 3 · Zielordner auswählen")
            dialog.resize(760, 560)
            dialog_layout = QVBoxLayout(dialog)
            step = QLabel("Schritt 3 von 3 · Zielordner auswählen")
            step.setObjectName("dialogStep")
            step.setAccessibleName("Schritt 3 von 3: Zielordner auswählen")
            dialog_layout.addWidget(step)
            hint = QLabel(
                "Wähle den Zielordner. Angeboten werden nur sichere Ordner innerhalb des zuerst gewählten Bereichs."
            )
            hint.setObjectName("subtitle")
            hint.setWordWrap(True)
            dialog_layout.addWidget(hint)

            target_list = QListWidget()
            target_list.setObjectName("i25TargetSelection")
            target_list.setAccessibleName("Gültiger Zielordner innerhalb der Wurzel")
            target_list.setSelectionMode(QAbstractItemView.SingleSelection)
            for relative in preparation.directories:
                target_list.addItem(
                    "/ (gewählte Wurzel)" if relative == "." else relative
                )
            dialog_layout.addWidget(target_list)

            target_status = QLabel("Noch kein Zielordner ausgewählt")
            target_status.setObjectName("stepHint")
            target_status.setAccessibleName("Zielauswahl: noch kein Zielordner")
            target_status.setWordWrap(True)
            target_status.setMaximumWidth(620)
            dialog_layout.addWidget(target_status)

            def compact_target_label(value: str, limit: int = 42) -> str:
                if len(value) <= limit:
                    return value
                keep = (limit - 1) // 2
                return f"{value[:keep]}…{value[-keep:]}"

            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            ok_button = buttons.button(QDialogButtonBox.Ok)
            cancel_button = buttons.button(QDialogButtonBox.Cancel)
            ok_button.setText("Vorschau anzeigen")
            ok_button.setAccessibleName("Transfer-Vorschau anzeigen")
            cancel_button.setText("Abbrechen")
            cancel_button.setAccessibleName("Zielauswahl abbrechen")
            ok_button.setEnabled(False)

            def update_target_status() -> None:
                selected = target_list.selectedItems()
                ok_button.setEnabled(bool(selected))
                if selected:
                    full_target = selected[0].text()
                    label = f"Ziel: {compact_target_label(full_target)}"
                    target_status.setText(label)
                    target_status.setToolTip(full_target)
                    target_status.setAccessibleName(f"Zielauswahl: Ziel: {full_target}")
                else:
                    target_status.setText("Noch kein Zielordner ausgewählt")
                    target_status.setAccessibleName("Zielauswahl: noch kein Zielordner")

            target_list.itemSelectionChanged.connect(update_target_status)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            dialog_layout.addWidget(buttons)
            return dialog, target_list, preparation

        def show_transfer_preview_for_paths(
            self,
            use_case_id: str,
            root: str,
            selected: tuple[str, ...],
            target: str,
        ) -> str:
            result = execute(
                use_case_id,
                root=root,
                selected_relative_paths=selected,
                target_dir=target,
            )
            self._present(use_case_id, result.title, result.status, result.body)
            return result.status

        def show_transfer_action(self, use_case_id: str) -> None:
            self._set_active_action(use_case_id)
            root = QFileDialog.getExistingDirectory(
                self,
                "Schritt 1 von 3 · Ausgangsordner auswählen",
            )
            if not root:
                self._render_result(use_case_id, None)
                return

            preparation = prepare_inventory_view(
                Path(root),
                InventoryViewSpec(sort=SORT_NAME_ASC, limit=100),
            )
            if preparation.status != "PASS" or preparation.view is None:
                self._present(
                    use_case_id,
                    "Transfer-Vorschau",
                    preparation.status,
                    "Der gewählte Ordner konnte nicht vollständig und sicher vorbereitet werden.\n\n"
                    "🔒 Es wurden keine Dateien verändert.",
                )
                return

            dialog, file_list = self.build_file_selection_dialog(preparation)

            if dialog.exec() != QDialog.Accepted:
                self._present(
                    use_case_id,
                    "Transfer-Vorschau",
                    "OPEN",
                    "Du hast die Dateiauswahl abgebrochen.\n\n🔒 Es wurden keine Dateien verändert.",
                )
                return

            selected_rows = sorted(index.row() for index in file_list.selectedIndexes())
            selected = tuple(
                preparation.view.items[row].relative_path for row in selected_rows
            )

            target_dialog, target_list, targets = self.build_target_selection_dialog(
                Path(root)
            )
            if target_dialog is None or target_list is None:
                self._present(
                    use_case_id,
                    "Transfer-Vorschau",
                    targets.status,
                    "Die Zielordner konnten nicht vollständig und sicher vorbereitet werden.\n\n"
                    "🔒 Es wurden keine Dateien verändert.",
                )
                return
            if target_dialog.exec() != QDialog.Accepted:
                self._present(
                    use_case_id,
                    "Transfer-Vorschau",
                    "OPEN",
                    "Du hast die Zielauswahl abgebrochen.\n\n🔒 Es wurden keine Dateien verändert.",
                )
                return

            row = target_list.currentRow()
            if row < 0:
                self._present(
                    use_case_id,
                    "Transfer-Vorschau",
                    "OPEN",
                    "Es wurde kein Zielordner gewählt.\n\n🔒 Es wurden keine Dateien verändert.",
                )
                return
            relative_target = targets.directories[row]
            target = (
                Path(targets.root)
                if relative_target == "."
                else Path(targets.root) / relative_target
            )
            self.show_transfer_preview_for_paths(
                use_case_id,
                root,
                selected,
                str(target),
            )

        def show_action(self, use_case_id: str) -> None:
            if use_case_id in TRANSFER_PREVIEW_IDS:
                self.show_transfer_action(use_case_id)
                return
            root = None
            if action_requires_root(use_case_id):
                root = QFileDialog.getExistingDirectory(
                    self,
                    "Ordner für sichere Vorschau auswählen",
                )
            self._render_result(use_case_id, root)

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("PROVOWARE LAIENTOOL")
    return app, MainWindow()


def run_gui() -> int:
    try:
        app, window = create_main_window()
    except RuntimeError:
        print(
            "GUI nicht verfügbar: PySide6 ist lokal nicht installiert. "
            "Es wird nichts nachinstalliert. Nutze stattdessen: ./start.sh --menu"
        )
        return 3
    window.show()
    return app.exec()


def main() -> int:
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
