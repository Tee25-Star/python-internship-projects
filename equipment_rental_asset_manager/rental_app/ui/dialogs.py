from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def _qdate(d: date) -> QDate:
    return QDate(d.year, d.month, d.day)


def _pydate(d: QDate) -> date:
    return date(d.year(), d.month(), d.day())


def message_error(parent: QWidget, title: str, text: str) -> None:
    m = QMessageBox(parent)
    m.setIcon(QMessageBox.Critical)
    m.setWindowTitle(title)
    m.setText(text)
    m.exec()


def message_confirm(parent: QWidget, title: str, text: str) -> bool:
    m = QMessageBox(parent)
    m.setIcon(QMessageBox.Question)
    m.setWindowTitle(title)
    m.setText(text)
    m.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return m.exec() == QMessageBox.Yes


@dataclass(frozen=True)
class AssetFormData:
    tag: str
    name: str
    category: str
    daily_rate: float
    status: str
    condition: str
    notes: str


class AssetDialog(QDialog):
    def __init__(self, *, title: str, initial: AssetFormData | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(520)

        self.tag = QLineEdit()
        self.name = QLineEdit()
        self.category = QLineEdit()

        self.daily_rate = QDoubleSpinBox()
        self.daily_rate.setRange(0.0, 1000000.0)
        self.daily_rate.setDecimals(2)
        self.daily_rate.setSingleStep(5.0)
        self.daily_rate.setPrefix("$ ")

        self.status = QComboBox()
        self.status.addItems(["available", "rented", "maintenance"])

        self.condition = QComboBox()
        self.condition.addItems(["excellent", "good", "fair", "poor"])

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes (included accessories, issues, serial details, etc.)")
        self.notes.setMinimumHeight(90)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.addRow("Asset Tag", self.tag)
        form.addRow("Name", self.name)
        form.addRow("Category", self.category)
        form.addRow("Daily Rate", self.daily_rate)
        form.addRow("Status", self.status)
        form.addRow("Condition", self.condition)
        form.addRow("Notes", self.notes)

        tip = QLabel("Tip: use unique tags like CAM-001, LGT-014, etc.")
        tip.setStyleSheet("color: rgba(231,234,243,0.70);")

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(tip)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if initial:
            self.tag.setText(initial.tag)
            self.name.setText(initial.name)
            self.category.setText(initial.category)
            self.daily_rate.setValue(float(initial.daily_rate))
            self.status.setCurrentText(initial.status)
            self.condition.setCurrentText(initial.condition)
            self.notes.setPlainText(initial.notes)

    def data(self) -> AssetFormData:
        return AssetFormData(
            tag=self.tag.text().strip(),
            name=self.name.text().strip(),
            category=self.category.text().strip(),
            daily_rate=float(self.daily_rate.value()),
            status=self.status.currentText(),
            condition=self.condition.currentText(),
            notes=self.notes.toPlainText().strip(),
        )


@dataclass(frozen=True)
class CustomerFormData:
    name: str
    company: str
    email: str
    phone: str


class CustomerDialog(QDialog):
    def __init__(self, *, title: str, initial: CustomerFormData | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(520)

        self.name = QLineEdit()
        self.company = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()

        form = QFormLayout()
        form.addRow("Name", self.name)
        form.addRow("Company", self.company)
        form.addRow("Email", self.email)
        form.addRow("Phone", self.phone)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if initial:
            self.name.setText(initial.name)
            self.company.setText(initial.company)
            self.email.setText(initial.email)
            self.phone.setText(initial.phone)

    def data(self) -> CustomerFormData:
        return CustomerFormData(
            name=self.name.text().strip(),
            company=self.company.text().strip(),
            email=self.email.text().strip(),
            phone=self.phone.text().strip(),
        )


@dataclass(frozen=True)
class RentalFormData:
    asset_id: int
    customer_id: int
    start_date: date
    due_date: date
    daily_rate: float
    deposit: float
    notes: str


class RentalDialog(QDialog):
    def __init__(
        self,
        *,
        title: str,
        asset_choices: list[tuple[int, str, float]],
        customer_choices: list[tuple[int, str]],
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(560)

        self.asset = QComboBox()
        self.customer = QComboBox()

        for asset_id, label, rate in asset_choices:
            self.asset.addItem(label, (int(asset_id), float(rate)))
        for cust_id, label in customer_choices:
            self.customer.addItem(label, int(cust_id))

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(_qdate(date.today()))

        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(_qdate(date.today()))
        self.due_date.setDate(self.due_date.date().addDays(3))

        self.daily_rate = QDoubleSpinBox()
        self.daily_rate.setRange(0.0, 1000000.0)
        self.daily_rate.setDecimals(2)
        self.daily_rate.setSingleStep(5.0)
        self.daily_rate.setPrefix("$ ")

        self.deposit = QDoubleSpinBox()
        self.deposit.setRange(0.0, 1000000.0)
        self.deposit.setDecimals(2)
        self.deposit.setSingleStep(25.0)
        self.deposit.setPrefix("$ ")

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Rental notes (pickup/return instructions, damage notes, etc.)")
        self.notes.setMinimumHeight(90)

        self.asset.currentIndexChanged.connect(self._sync_rate_from_asset)
        self._sync_rate_from_asset()

        form = QFormLayout()
        form.addRow("Asset", self.asset)
        form.addRow("Customer", self.customer)
        form.addRow("Start Date", self.start_date)
        form.addRow("Due Date", self.due_date)
        form.addRow("Daily Rate", self.daily_rate)
        form.addRow("Deposit", self.deposit)
        form.addRow("Notes", self.notes)

        hint = QLabel("Only available assets are shown here.")
        hint.setStyleSheet("color: rgba(231,234,243,0.70);")

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(hint)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _sync_rate_from_asset(self) -> None:
        data = self.asset.currentData()
        if not data:
            return
        _asset_id, rate = data
        self.daily_rate.setValue(float(rate))

    def data(self) -> RentalFormData:
        asset_id, _rate = self.asset.currentData()
        return RentalFormData(
            asset_id=int(asset_id),
            customer_id=int(self.customer.currentData()),
            start_date=_pydate(self.start_date.date()),
            due_date=_pydate(self.due_date.date()),
            daily_rate=float(self.daily_rate.value()),
            deposit=float(self.deposit.value()),
            notes=self.notes.toPlainText().strip(),
        )

