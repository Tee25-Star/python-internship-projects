from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QPushButton


class CardFrame(QFrame):
    def __init__(self, *, radius: int = 18, parent=None):
        super().__init__(parent)
        self.setObjectName("CardFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            f"""
            QFrame#CardFrame {{
              background: rgba(12, 18, 39, 0.58);
              border: 1px solid rgba(255,255,255,0.07);
              border-radius: {radius}px;
            }}
            """
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 170))
        self.setGraphicsEffect(shadow)


class PillLabel(QLabel):
    def __init__(self, text: str, *, kind: str = "neutral", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(24)
        self.setStyleSheet(_pill_qss(kind))

    def set_kind(self, kind: str) -> None:
        self.setStyleSheet(_pill_qss(kind))


def _pill_qss(kind: str) -> str:
    if kind == "good":
        bg, bd = "rgba(34,197,94,0.16)", "rgba(34,197,94,0.34)"
    elif kind == "warn":
        bg, bd = "rgba(251,191,36,0.16)", "rgba(251,191,36,0.32)"
    elif kind == "bad":
        bg, bd = "rgba(251,113,133,0.16)", "rgba(251,113,133,0.35)"
    else:
        bg, bd = "rgba(255,255,255,0.07)", "rgba(255,255,255,0.12)"

    return f"""
    QLabel {{
      padding: 3px 10px;
      border-radius: 12px;
      background: {bg};
      border: 1px solid {bd};
      font-weight: 800;
      color: rgba(231,234,243,0.92);
    }}
    """


class PrimaryButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("Primary")


class DangerButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("Danger")

