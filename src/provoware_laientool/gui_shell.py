"""Optional PySide6 GUI adapter for the read-only shell."""

from __future__ import annotations

from .application_core import action_requires_root, execute
from .capability_registry import list_use_cases
from .ui_themes import THEMES, get_theme, stylesheet


def create_main_window():
    """Create the real GUI window without entering the Qt event loop."""
    try:
        from PySide6.QtWidgets import (
            QApplication,
            QComboBox,
            QFrame,
            QFileDialog,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QPushButton,
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
                if not (entry.gui_available and entry.status == "READY"):
                    continue
                button = QPushButton(entry.label)
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

        def show_action(self, use_case_id: str) -> None:
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
