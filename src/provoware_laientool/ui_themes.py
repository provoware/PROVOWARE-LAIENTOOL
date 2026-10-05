"""Pure theme definitions for the optional PySide6 shell."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Theme:
    id: str
    label: str
    canvas: str
    surface: str
    raised: str
    text: str
    muted: str
    accent: str
    accent_secondary: str
    contrast_one: str
    contrast_two: str
    focus: str


THEMES: tuple[Theme, ...] = (
    Theme(
        "purple-neon", "Violett Neon",
        "#10121a", "#171a24", "#202536", "#f6f2ff", "#b8b4c8",
        "#9d5cff", "#4f7cff", "#2ee6d6", "#62f59b", "#c07cff",
    ),
    Theme(
        "turquoise-neon", "Türkis Neon",
        "#07191a", "#0c2325", "#123033", "#efffff", "#a9c8c8",
        "#24d7c8", "#24a7ff", "#9a6cff", "#ffb347", "#55f5e8",
    ),
    Theme(
        "graphite-electric", "Graphit Elektrisch",
        "#111316", "#191c20", "#24282e", "#f4f7fb", "#b2bac5",
        "#3f8cff", "#a8b6c8", "#6dff9b", "#ffb454", "#7db7ff",
    ),
    Theme(
        "crimson-copper", "Karmin / Kupfer",
        "#1a0d11", "#271419", "#351d22", "#fff7f1", "#d4b9b0",
        "#e84b72", "#d98345", "#55dff0", "#ffe4c4", "#ff7d9f",
    ),
)


def get_theme(theme_id: str) -> Theme:
    for theme in THEMES:
        if theme.id == theme_id:
            return theme
    return THEMES[0]


def stylesheet(theme: Theme, scale_percent: int = 100) -> str:
    scale = max(100, min(scale_percent, 200)) / 100
    body = round(16 * scale)
    small = round(14 * scale)
    title = round(28 * scale)
    section = round(20 * scale)
    button = round(16 * scale)
    radius = round(12 * scale)
    padding = round(12 * scale)
    compact_padding = round(8 * scale)
    control_height = round(24 * scale)

    return f"""
QWidget {{
    background: {theme.canvas};
    color: {theme.text};
    font-size: {body}px;
}}
QMainWindow, QDialog {{
    background: {theme.canvas};
}}
QFrame#sidebar, QFrame#contentCard, QFrame#statusCard, QFrame#safetyCard {{
    background: {theme.surface};
    border: 1px solid {theme.raised};
    border-radius: {radius}px;
}}
QFrame#safetyCard {{
    border: 2px solid {theme.accent_secondary};
}}
QLabel#title {{
    font-size: {title}px;
    font-weight: 700;
}}
QLabel#subtitle, QLabel#muted, QLabel#stepHint {{
    color: {theme.muted};
}}
QLabel#subtitle {{
    font-size: {small}px;
}}
QLabel#controlLabel {{
    color: {theme.muted};
    font-size: {small}px;
    font-weight: 600;
}}
QLabel#navTitle, QLabel#dialogStep {{
    font-size: {section}px;
    font-weight: 700;
}}
QLabel#stepHint {{
    font-size: {small}px;
}}
QLabel#statusPill {{
    background: {theme.raised};
    border: 2px solid {theme.accent_secondary};
    border-radius: {radius}px;
    padding: {compact_padding}px;
    font-weight: 700;
}}
QLabel#statusPill[status="pass"] {{
    border-color: {theme.contrast_two};
}}
QLabel#statusPill[status="open"] {{
    border-color: {theme.accent_secondary};
}}
QLabel#statusPill[status="blocked"] {{
    border-color: {theme.accent};
}}
QPushButton {{
    background: {theme.raised};
    border: 1px solid {theme.accent_secondary};
    border-radius: {radius}px;
    padding: {padding}px;
    min-height: {control_height}px;
    text-align: left;
    font-size: {button}px;
}}
QPushButton:hover {{
    border: 2px solid {theme.accent};
}}
QPushButton[active="true"] {{
    background: {theme.surface};
    border: 2px solid {theme.accent};
    font-weight: 700;
}}
QPushButton:focus {{
    border: 3px solid {theme.focus};
}}
QComboBox {{
    background: {theme.raised};
    border: 1px solid {theme.accent_secondary};
    border-radius: {radius}px;
    padding: {compact_padding}px {padding}px;
    min-height: {control_height}px;
}}
QComboBox:focus {{
    border: 3px solid {theme.focus};
}}
QTextEdit, QListWidget {{
    background: {theme.surface};
    border: 1px solid {theme.raised};
    border-radius: {radius}px;
    padding: {padding}px;
}}
QTextEdit:focus, QListWidget:focus {{
    border: 3px solid {theme.focus};
}}
QListWidget::item {{
    padding: {compact_padding}px;
}}
QListWidget::item:selected {{
    background: {theme.raised};
    color: {theme.text};
    border-left: 4px solid {theme.accent};
}}
QToolTip {{
    background: {theme.raised};
    color: {theme.text};
    border: 1px solid {theme.focus};
    padding: {compact_padding}px;
}}
"""
