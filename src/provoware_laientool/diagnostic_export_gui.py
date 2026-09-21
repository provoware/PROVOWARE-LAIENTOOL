"""PySide6 GUI adapter used only by the gated I31 evidence mode."""

from __future__ import annotations

from pathlib import Path

from .diagnostic_export_adapter import (
    DiagnosticExportAdapterSession,
    FORMAT_JSON,
    FORMAT_TEXT,
    PASS,
)
from .diagnostics import DiagnosticReport
from .ui_themes import get_theme, stylesheet


def create_export_evidence_window(report: DiagnosticReport, *, target_dir: Path):
    try:
        from PySide6.QtWidgets import (
            QApplication,
            QComboBox,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QPushButton,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:
        raise RuntimeError(f"PySide6/QtWidgets konnte nicht geladen werden: {exc}") from exc

    class ExportEvidenceWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("PROVOWARE – Diagnoseexport · Prüfmodus")
            self.resize(1120, 780)
            self._report = report
            self._target_dir = target_dir
            self._session: DiagnosticExportAdapterSession | None = None
            self.last_status = "OPEN"

            root = QWidget()
            layout = QVBoxLayout(root)
            layout.setContentsMargins(24, 24, 24, 24)
            layout.setSpacing(14)

            title = QLabel("Diagnose lokal speichern · Prüfmodus")
            title.setObjectName("title")
            layout.addWidget(title)

            self.safety = QLabel(
                "🧪 Synthetischer Testbereich – keine Nutzerdateien werden als Testdaten verwendet."
            )
            self.safety.setWordWrap(True)
            layout.addWidget(self.safety)

            controls = QHBoxLayout()
            self.scale_box = QComboBox()
            self.scale_box.setAccessibleName("Schrift- und Oberflächengröße")
            for value in (100, 150, 200):
                self.scale_box.addItem(f"{value} %", value)
            self.scale_box.currentIndexChanged.connect(self.apply_scale)
            controls.addWidget(self.scale_box)

            self.format_box = QComboBox()
            self.format_box.setAccessibleName("Exportformat")
            self.format_box.addItem("Klartext", FORMAT_TEXT)
            self.format_box.addItem("JSON", FORMAT_JSON)
            self.format_box.currentIndexChanged.connect(self.reset_preview)
            controls.addWidget(self.format_box)
            controls.addStretch()
            layout.addLayout(controls)

            self.target_label = QLabel(f"Test-Zielordner: {target_dir}")
            self.target_label.setWordWrap(True)
            layout.addWidget(self.target_label)

            self.output = QTextEdit()
            self.output.setReadOnly(True)
            self.output.setAccessibleName("Diagnoseexport Status und Zusammenfassung")
            layout.addWidget(self.output, 1)

            buttons = QHBoxLayout()
            self.preview_button = QPushButton("Vorschau vorbereiten")
            self.preview_button.clicked.connect(self.prepare_preview)
            buttons.addWidget(self.preview_button)

            self.stage1_button = QPushButton("Weiter zur finalen Bestätigung")
            self.stage1_button.setEnabled(False)
            self.stage1_button.clicked.connect(self.confirm_stage1)
            buttons.addWidget(self.stage1_button)

            self.commit_button = QPushButton("Diagnosedatei jetzt neu erstellen")
            self.commit_button.setEnabled(False)
            self.commit_button.setAutoDefault(False)
            self.commit_button.setDefault(False)
            self.commit_button.clicked.connect(self.commit_stage2)
            buttons.addWidget(self.commit_button)

            self.cancel_button = QPushButton("Abbrechen")
            self.cancel_button.setAutoDefault(True)
            self.cancel_button.setDefault(True)
            self.cancel_button.clicked.connect(self.cancel_flow)
            buttons.addWidget(self.cancel_button)
            layout.addLayout(buttons)

            self.setCentralWidget(root)
            self.apply_scale()
            self.reset_preview()

        def set_scale_percent(self, percent: int) -> None:
            index = self.scale_box.findData(percent)
            if index >= 0:
                self.scale_box.setCurrentIndex(index)
            self.apply_scale()

        def apply_scale(self) -> None:
            percent = int(self.scale_box.currentData() or 100)
            self.setStyleSheet(stylesheet(get_theme("graphite-electric"), percent))

        def core_widgets(self):
            return (
                self.scale_box,
                self.format_box,
                self.output,
                self.preview_button,
                self.stage1_button,
                self.commit_button,
                self.cancel_button,
            )

        def reset_preview(self) -> None:
            self._session = None
            self.last_status = "OPEN"
            self.stage1_button.setEnabled(False)
            self.commit_button.setEnabled(False)
            self.format_box.setEnabled(True)
            self.preview_button.setEnabled(True)
            self.output.setPlainText(
                "Noch kein Export vorbereitet.\n"
                "Es wurde nichts geschrieben.\n"
                "Wähle das Format und bereite anschließend die Vorschau vor."
            )

        def prepare_preview(self) -> None:
            export_format = str(self.format_box.currentData())
            self._session = DiagnosticExportAdapterSession(
                self._report,
                target_dir=self._target_dir,
                export_format=export_format,
            )
            result = self._session.preview()
            self.last_status = result.status
            self.output.setPlainText(result.body)
            ready = result.status == PASS
            self.stage1_button.setEnabled(ready)
            self.commit_button.setEnabled(False)

        def confirm_stage1(self) -> None:
            if self._session is None:
                return
            result = self._session.confirm_stage1()
            self.last_status = result.status
            self.output.setPlainText(
                result.body
                + "\n\nFinale Zusammenfassung:\n"
                + self._session.preview().body
            )
            if result.status == "CONFIRMED_STAGE_1":
                self.format_box.setEnabled(False)
                self.preview_button.setEnabled(False)
                self.stage1_button.setEnabled(False)
                self.commit_button.setEnabled(True)
                self.cancel_button.setFocus()

        def commit_stage2(self) -> None:
            if self._session is None:
                return
            result = self._session.confirm_and_execute()
            self.last_status = result.status
            self.output.setPlainText(result.body)
            self.commit_button.setEnabled(False)
            self.stage1_button.setEnabled(False)
            self.preview_button.setEnabled(False)
            self.cancel_button.setFocus()

        def cancel_flow(self) -> None:
            if self._session is not None:
                result = self._session.cancel()
                self.last_status = result.status
                self.output.setPlainText(result.body)
            else:
                self.last_status = "CANCELLED"
                self.output.setPlainText("Abgebrochen. Es wurde keine Diagnosedatei erstellt.")
            self.stage1_button.setEnabled(False)
            self.commit_button.setEnabled(False)
            self.cancel_button.setFocus()

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("PROVOWARE I31 Evidence")
    return app, ExportEvidenceWindow()
