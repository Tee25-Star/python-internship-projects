from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon


_ROOT = Path(__file__).resolve().parents[2]
_ICON_DIR = _ROOT / "assets" / "icons"


def icon(name: str) -> QIcon:
    """
    Load an icon from assets/icons.
    Example: icon("dashboard") loads assets/icons/dashboard.svg
    """
    path = _ICON_DIR / f"{name}.svg"
    return QIcon(str(path))

