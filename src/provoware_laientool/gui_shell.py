"""Optional PySide6 GUI adapter for the read-only I11 shell."""

from __future__ import annotations

from .application_core import execute
from .capability_registry import list_use_cases
from .ui_themes import THEMES, get_theme, stylesheet


def run_gui() -> int:
    try:
        from PySide6.QtWidgets import (
            QApplication,
            QComboBox,
            QFrame,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QPushButton,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )
    except ImportError:
        print(
            "GUI nicht verfügbar: PySide6 ist lokal nicht installiert. "
            "Es wird nichts nachinstalliert. Nutze stattdessen: python3 start.py --menu"
        )
        return 3

    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("PROVOWARE LAIENTOOL")
            self.resize(1180, 760)

            root = QWidget()
            outer = QVBoxLayout(root)
            outer.setContentsMargins(18, 18, 18, 18)
            outer.setSpacing(14)

            top = QHBoxLayout()
            title = QLabel("PROVOWARE")
            title.setObjectName("title")
            top.addWidget(title)
            top.addStretch()

            self.scale_box = QComboBox()
            self.scale_box.setAccessibleName("Schrift- und Oberflächengröße")
            for value in (100, 125, 150, 175, 200):
                self.scale_box.addItem(f"{value} %", value)
            self.scale_box.currentIndexChanged.connect(self.apply_theme)
            top.addWidget(self.scale_box)

            self.theme_box = QComboBox()
            self.theme_box.setAccessibleName("Farbthema")
            for theme in THEMES:
                self.theme_box.addItem(theme.label, theme.id)
            self.theme_box.currentIndexChanged.connect(self.apply_theme)
            top.addWidget(self.theme_box)
            outer.addLayout(top)

            safety = QLabel("🔒 Sicherer Lese-Modus – Es werden keine Dateien verändert.")
            safety.setObjectName("muted")
            safety.setWordWrap(True)
            outer.addWidget(safety)

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
                button.setAccessibleName(entry.label)
                button.clicked.connect(
                    lambda checked=False, use_case_id=entry.id: self.show_action(use_case_id)
                )
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
            self.output.setReadOnly(True)
            self.output.setAccessibleName("Ergebnis und Hilfe")
            content_layout.addWidget(self.output, 1)

            body.addWidget(content, 3)
            outer.addLayout(body, 1)

            self.setCentralWidget(root)
            self.show_action("app.overview")
            self.apply_theme()

        def apply_theme(self) -> None:
            theme_id = self.theme_box.currentData() or THEMES[0].id
            scale = self.scale_box.currentData() or 100
            QApplication.instance().setStyleSheet(
                stylesheet(get_theme(theme_id), int(scale))
            )

        def show_action(self, use_case_id: str) -> None:
            result = execute(use_case_id)
            self.section_title.setText(f"{result.title} · {result.status}")
            self.output.setPlainText(result.body)

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("PROVOWARE LAIENTOOL")
    window = MainWindow()
    window.show()
    return app.exec()


def main() -> int:
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
