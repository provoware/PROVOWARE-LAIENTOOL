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
        "purple-neon", "Purple Neon",
        "#10121a", "#171a24", "#202536", "#f6f2ff", "#b8b4c8",
        "#9d5cff", "#4f7cff", "#2ee6d6", "#62f59b", "#c07cff",
    ),
    Theme(
        "turquoise-neon", "Turquoise Neon",
        "#07191a", "#0c2325", "#123033", "#efffff", "#a9c8c8",
        "#24d7c8", "#24a7ff", "#9a6cff", "#ffb347", "#55f5e8",
    ),
    Theme(
        "graphite-electric", "Graphite Electric",
        "#111316", "#191c20", "#24282e", "#f4f7fb", "#b2bac5",
        "#3f8cff", "#a8b6c8", "#6dff9b", "#ffb454", "#7db7ff",
    ),
    Theme(
        "crimson-copper", "Crimson / Copper",
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
    title = round(28 * scale)
    button = round(16 * scale)
    radius = round(12 * scale)
    padding = round(12 * scale)

    return f"""
QWidget {{
    background: {theme.canvas};
    color: {theme.text};
    font-size: {body}px;
}}
QFrame#sidebar, QFrame#contentCard, QFrame#statusCard {{
    background: {theme.surface};
    border: 1px solid {theme.raised};
    border-radius: {radius}px;
}}
QLabel#title {{
    font-size: {title}px;
    font-weight: 700;
}}
QLabel#muted {{
    color: {theme.muted};
}}
QPushButton {{
    background: {theme.raised};
    border: 1px solid {theme.accent_secondary};
    border-radius: {radius}px;
    padding: {padding}px;
    text-align: left;
    font-size: {button}px;
}}
QPushButton:hover {{
    border: 1px solid {theme.accent};
}}
QPushButton:focus {{
    border: 2px solid {theme.focus};
}}
QComboBox {{
    background: {theme.raised};
    border: 1px solid {theme.accent_secondary};
    border-radius: {radius}px;
    padding: {padding}px;
}}
QComboBox:focus {{
    border: 2px solid {theme.focus};
}}
QTextEdit {{
    background: {theme.surface};
    border: 1px solid {theme.raised};
    border-radius: {radius}px;
    padding: {padding}px;
}}
QTextEdit:focus {{
    border: 2px solid {theme.focus};
}}
"""
