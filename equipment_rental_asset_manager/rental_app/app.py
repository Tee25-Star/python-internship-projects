from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from .db import init_db
from .ui.main_window import MainWindow
from .ui.theme import apply_theme


def run_app() -> None:
    init_db(seed=True)

    app = QApplication(sys.argv)
    app.setApplicationName("Aurum Rentals")
    app.setOrganizationName("Aurum Labs")
    app.setApplicationDisplayName("Aurum Rentals")
    app.setStyle("Fusion")
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    apply_theme(app)

    win = MainWindow()
    win.show()
    raise SystemExit(app.exec())

