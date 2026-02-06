from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication


ACCENT = "#6D5DFc"
ACCENT_2 = "#22c55e"
DANGER = "#fb7185"
WARNING = "#fbbf24"


def apply_theme(app: QApplication) -> None:
    app.setFont(QFont("Segoe UI", 10))

    pal = QPalette()
    pal.setColor(QPalette.Window, QColor("#0b1020"))
    pal.setColor(QPalette.WindowText, QColor("#e7eaf3"))
    pal.setColor(QPalette.Base, QColor("#0f1630"))
    pal.setColor(QPalette.AlternateBase, QColor("#0c1227"))
    pal.setColor(QPalette.ToolTipBase, QColor("#0f1630"))
    pal.setColor(QPalette.ToolTipText, QColor("#e7eaf3"))
    pal.setColor(QPalette.Text, QColor("#e7eaf3"))
    pal.setColor(QPalette.Button, QColor("#131b38"))
    pal.setColor(QPalette.ButtonText, QColor("#e7eaf3"))
    pal.setColor(QPalette.BrightText, QColor("#ffffff"))
    pal.setColor(QPalette.Highlight, QColor(ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)

    # A "glassy" dark theme with gradient accents + soft borders.
    qss = f"""
    * {{
      font-family: "Segoe UI";
    }}

    QWidget {{
      color: #e7eaf3;
      selection-background-color: {ACCENT};
    }}

    QMainWindow {{
      background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0b1020, stop:0.55 #0c1330, stop:1 #070b18);
    }}

    QFrame#Sidebar {{
      background: rgba(10, 14, 30, 0.82);
      border-right: 1px solid rgba(255, 255, 255, 0.06);
    }}

    QLabel#AppTitle {{
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0.6px;
    }}

    QLabel#AppSubtitle {{
      color: rgba(231, 234, 243, 0.65);
      font-size: 11px;
    }}

    QToolButton#NavButton {{
      text-align: left;
      padding: 10px 12px;
      border-radius: 12px;
      background: transparent;
      border: 1px solid transparent;
      font-weight: 600;
    }}
    QToolButton#NavButton:hover {{
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.06);
    }}
    QToolButton#NavButton[active="true"] {{
      background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(109, 93, 252, 0.26),
        stop:1 rgba(34, 197, 94, 0.10));
      border: 1px solid rgba(109, 93, 252, 0.35);
    }}

    QFrame#TopBar {{
      background: rgba(10, 14, 30, 0.40);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 16px;
    }}

    QLabel#PageTitle {{
      font-size: 18px;
      font-weight: 800;
    }}
    QLabel#PageHint {{
      color: rgba(231, 234, 243, 0.70);
    }}

    QLineEdit {{
      background: rgba(15, 22, 48, 0.90);
      border: 1px solid rgba(255,255,255,0.08);
      padding: 9px 10px;
      border-radius: 12px;
    }}
    QLineEdit:focus {{
      border: 1px solid rgba(109,93,252,0.55);
      background: rgba(15, 22, 48, 1.0);
    }}

    QComboBox {{
      background: rgba(15, 22, 48, 0.90);
      border: 1px solid rgba(255,255,255,0.08);
      padding: 7px 10px;
      border-radius: 12px;
    }}
    QComboBox:focus {{
      border: 1px solid rgba(109,93,252,0.55);
    }}
    QComboBox QAbstractItemView {{
      background: #0f1630;
      border: 1px solid rgba(255,255,255,0.10);
      selection-background-color: rgba(109,93,252,0.40);
      outline: 0;
    }}

    QDateEdit {{
      background: rgba(15, 22, 48, 0.90);
      border: 1px solid rgba(255,255,255,0.08);
      padding: 7px 10px;
      border-radius: 12px;
    }}

    QPushButton {{
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      padding: 9px 12px;
      border-radius: 12px;
      font-weight: 700;
    }}
    QPushButton:hover {{
      background: rgba(255,255,255,0.09);
    }}
    QPushButton:pressed {{
      background: rgba(255,255,255,0.05);
    }}

    QPushButton#Primary {{
      background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(109,93,252,0.95),
        stop:1 rgba(34,197,94,0.85));
      border: 1px solid rgba(255,255,255,0.12);
    }}
    QPushButton#Primary:hover {{
      border: 1px solid rgba(255,255,255,0.20);
    }}

    QPushButton#Danger {{
      background: rgba(251, 113, 133, 0.18);
      border: 1px solid rgba(251, 113, 133, 0.35);
    }}

    QTableWidget {{
      background: rgba(9, 13, 27, 0.35);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 14px;
      gridline-color: rgba(255,255,255,0.06);
      selection-background-color: rgba(109,93,252,0.35);
      selection-color: #ffffff;
    }}
    QHeaderView::section {{
      background: rgba(19, 27, 56, 0.85);
      color: rgba(231,234,243,0.90);
      padding: 10px 10px;
      border: 0px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      font-weight: 800;
    }}

    QScrollBar:vertical {{
      background: transparent;
      width: 10px;
      margin: 4px 2px 4px 2px;
    }}
    QScrollBar::handle:vertical {{
      background: rgba(255,255,255,0.12);
      border-radius: 5px;
      min-height: 32px;
    }}
    QScrollBar::handle:vertical:hover {{
      background: rgba(255,255,255,0.18);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
      height: 0px;
    }}
    """
    app.setStyleSheet(qss)

