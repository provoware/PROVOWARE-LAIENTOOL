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
        raise RuntimeError("PySide6 ist lokal nicht installiert.") from exc

    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("PROVOWARE LAIENTOOL")
            self.resize(1180, 760)
            self.action_buttons: dict[str, QPushButton] = {}

            root = QWidget()
            root.setObjectName("root")
            outer = QVBoxLayout(root)
            outer.setContentsMargins(18, 18, 18, 18)
            outer.setSpacing(14)

            top = QHBoxLayout()
            title = QLabel("PROVOWARE")
            title.setObjectName("title")
            top.addWidget(title)
            top.addStretch()

            self.scale_box = QComboBox()
            self.scale_box.setObjectName("scaleBox")
            self.scale_box.setAccessibleName("Schrift- und Oberflächengröße")
            for value in (100, 125, 150, 175, 200):
                self.scale_box.addItem(f"{value} %", value)
            self.scale_box.currentIndexChanged.connect(self.apply_theme)
            top.addWidget(self.scale_box)

            self.theme_box = QComboBox()
            self.theme_box.setObjectName("themeBox")
            self.theme_box.setAccessibleName("Farbthema")
            for theme in THEMES:
                self.theme_box.addItem(theme.label, theme.id)
            self.theme_box.currentIndexChanged.connect(self.apply_theme)
            top.addWidget(self.theme_box)
            outer.addLayout(top)

            self.safety_label = QLabel(
                "🔒 Sicherer Lese-Modus – Es werden keine Dateien verändert."
            )
            self.safety_label.setObjectName("muted")
            self.safety_label.setWordWrap(True)
            outer.addWidget(self.safety_label)

            body = QHBoxLayout()
            body.setSpacing(14)

            sidebar = QFrame()
            sidebar.setObjectName("sidebar")
            side_layout = QVBoxLayout(sidebar)
            side_layout.setContentsMargins(12, 12, 12, 12)
            side_layout.setSpacing(8)

            for entry in list_use_cases():
                is_ready = entry.gui_available and entry.status == "READY"
                is_i25_evidence = (
                    evidence_mode
                    and entry.gui_available
                    and entry.id in TRANSFER_PREVIEW_IDS
                )
                if not (is_ready or is_i25_evidence):
                    continue
                label = (
                    f"{entry.label} · Prüfmodus"
                    if entry.id in TRANSFER_PREVIEW_IDS and entry.status != "READY"
                    else entry.label
                )
                button = QPushButton(label)
                button.setObjectName(f"action-{entry.id}")
                button.setAccessibleName(entry.label)
                button.clicked.connect(
                    lambda checked=False, use_case_id=entry.id: self.show_action(use_case_id)
                )
                self.action_buttons[entry.id] = button
                side_layout.addWidget(button)
            side_layout.addStretch()
            body.addWidget(sidebar, 1)

            content = QFrame()
            content.setObjectName("contentCard")
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(18, 18, 18, 18)
            content_layout.setSpacing(10)

            self.section_title = QLabel("Übersicht")
            self.section_title.setObjectName("title")
            content_layout.addWidget(self.section_title)

            self.output = QTextEdit()
            self.output.setObjectName("resultOutput")
            self.output.setReadOnly(True)
            self.output.setAccessibleName("Ergebnis und Hilfe")
            content_layout.addWidget(self.output, 1)

            body.addWidget(content, 3)
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
                self.scale_box,
                self.theme_box,
                self.safety_label,
                *self.action_buttons.values(),
                self.section_title,
                self.output,
            )

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
            self.section_title.setText(f"{result.title} · {result.status}")
            self.output.setPlainText(result.body)

        def show_action_for_root(self, use_case_id: str, root: str | None) -> None:
            self._render_result(use_case_id, root)

        def build_file_selection_dialog(self, preparation):
            dialog = QDialog(self)
            dialog.setWindowTitle("2/3 Dateien auswählen")
            dialog_layout = QVBoxLayout(dialog)
            hint = QLabel(
                "Wähle eine oder mehrere Dateien. Strg/Shift erlaubt Mehrfachauswahl."
            )
            hint.setWordWrap(True)
            dialog_layout.addWidget(hint)

            file_list = QListWidget()
            file_list.setObjectName("i25FileSelection")
            file_list.setAccessibleName("Dateien für Transfer-Vorschau")
            file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
            for item in preparation.view.items:
                file_list.addItem(f"{item.relative_path}  ·  {item.size_bytes} Byte")
            dialog_layout.addWidget(file_list)

            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            ok_button = buttons.button(QDialogButtonBox.Ok)
            ok_button.setEnabled(False)
            file_list.itemSelectionChanged.connect(
                lambda: ok_button.setEnabled(bool(file_list.selectedItems()))
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            dialog_layout.addWidget(buttons)
            return dialog, file_list

        def build_target_selection_dialog(self, root: Path):
            preparation = prepare_target_directories(root)
            if preparation.status != "PASS":
                return None, None, preparation

            dialog = QDialog(self)
            dialog.setWindowTitle("3/3 Zielordner innerhalb der Wurzel auswählen")
            dialog_layout = QVBoxLayout(dialog)
            hint = QLabel(
                "Es werden nur vorhandene Ordner innerhalb der gewählten Wurzel angeboten."
            )
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

            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            ok_button = buttons.button(QDialogButtonBox.Ok)
            ok_button.setEnabled(False)
            target_list.itemSelectionChanged.connect(
                lambda: ok_button.setEnabled(bool(target_list.selectedItems()))
            )
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
            self.section_title.setText(f"{result.title} · {result.status}")
            self.output.setPlainText(result.body)
            return result.status

        def show_transfer_action(self, use_case_id: str) -> None:
            root = QFileDialog.getExistingDirectory(
                self,
                "1/3 Wurzel für Transfer-Vorschau auswählen",
            )
            if not root:
                self._render_result(use_case_id, None)
                return

            preparation = prepare_inventory_view(
                Path(root),
                InventoryViewSpec(sort=SORT_NAME_ASC, limit=100),
            )
            if preparation.status != "PASS" or preparation.view is None:
                self.section_title.setText(f"Transfer-Vorschau · {preparation.status}")
                self.output.setPlainText(
                    "Der gewählte Ordner konnte nicht vollständig und sicher vorbereitet werden.\n\n"
                    "🔒 Es wurden keine Dateien verändert."
                )
                return

            dialog, file_list = self.build_file_selection_dialog(preparation)

            if dialog.exec() != QDialog.Accepted:
                self.section_title.setText("Transfer-Vorschau · OPEN")
                self.output.setPlainText(
                    "Auswahl abgebrochen.\n\n🔒 Es wurden keine Dateien verändert."
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
                self.section_title.setText(f"Transfer-Vorschau · {targets.status}")
                self.output.setPlainText(
                    "Die Zielordner konnten nicht vollständig und sicher vorbereitet werden.\n\n"
                    "🔒 Es wurden keine Dateien verändert."
                )
                return
            if target_dialog.exec() != QDialog.Accepted:
                self.section_title.setText("Transfer-Vorschau · OPEN")
                self.output.setPlainText(
                    "Zielauswahl abgebrochen.\n\n🔒 Es wurden keine Dateien verändert."
                )
                return

            row = target_list.currentRow()
            if row < 0:
                self.section_title.setText("Transfer-Vorschau · OPEN")
                self.output.setPlainText(
                    "Es wurde kein Zielordner gewählt.\n\n🔒 Es wurden keine Dateien verändert."
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
                    "Ordner für reine Vorschau auswählen",
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
