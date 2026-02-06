"""Application entry point."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from warehouse_app.ui.views import create_main_window


def _load_theme(app: QApplication) -> None:
    theme_path = Path(__file__).resolve().parent / "ui" / "theme.qss"
    if theme_path.exists():
        with theme_path.open("r", encoding="utf-8") as stylesheet:
            app.setStyleSheet(stylesheet.read())


def main() -> None:
    """Launch the warehouse management experience."""
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Aurora Warehouse Studio")
    app.setOrganizationName("Aurora Labs")

    _load_theme(app)

    window = create_main_window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

