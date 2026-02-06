"""UI views for the warehouse app."""

from __future__ import annotations

import math
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from warehouse_app.data.repository import RepositoryError
from warehouse_app.services.inventory_service import (
    InventoryCreate,
    InventoryDTO,
    InventoryService,
    InventorySummary,
    InventoryUpdate,
)


class InventoryTableModel(QAbstractTableModel):
    """Backs the table view with inventory data."""

    headers = ["SKU", "Name", "Category", "Qty", "Reorder", "Location", "Unit Cost"]

    def __init__(self, items: Optional[list[InventoryDTO]] = None) -> None:
        super().__init__()
        self._items: list[InventoryDTO] = items or []
        self._sort_column = 1

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self._items)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # type: ignore[override]
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return None
        item = self._items[index.row()]

        if role == Qt.DisplayRole:
            column_handlers = {
                0: lambda: item.sku,
                1: lambda: item.name,
                2: lambda: item.category,
                3: lambda: f"{item.quantity}",
                4: lambda: f"{item.reorder_level}",
                5: lambda: item.location,
                6: lambda: f"${item.unit_cost:,.2f}",
            }
            handler = column_handlers.get(index.column())
            return handler() if handler else None

        if role == Qt.TextAlignmentRole and index.column() in (3, 4, 6):
            return Qt.AlignCenter

        if role == Qt.ForegroundRole and index.column() == 3:
            if item.quantity <= item.reorder_level:
                return QColor("#f25f4c")

        if role == Qt.ToolTipRole:
            return (
                f"{item.name}\n"
                f"SKU: {item.sku}\n"
                f"Category: {item.category}\n"
                f"Location: {item.location}\n"
                f"Quantity: {item.quantity}"
            )

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # type: ignore[override]
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.headers[section]
        return str(section + 1)

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:  # type: ignore[override]
        reverse = order == Qt.DescendingOrder
        key_map = {
            0: lambda item: item.sku.lower(),
            1: lambda item: item.name.lower(),
            2: lambda item: item.category.lower(),
            3: lambda item: item.quantity,
            4: lambda item: item.reorder_level,
            5: lambda item: item.location.lower(),
            6: lambda item: item.unit_cost,
        }
        key_fn = key_map.get(column, lambda item: item.name.lower())
        self.layoutAboutToBeChanged.emit()
        self._items.sort(key=key_fn, reverse=reverse)
        self.layoutChanged.emit()

    def update_items(self, items: list[InventoryDTO]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def item_at(self, row: int) -> InventoryDTO | None:
        if 0 <= row < len(self._items):
            return self._items[row]
        return None


class InventoryFilterProxyModel(QSortFilterProxyModel):
    """Allows fuzzy filtering across visible columns."""

    def __init__(self) -> None:
        super().__init__()
        self._search_term: str = ""
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def set_search_term(self, term: str) -> None:
        self._search_term = term.strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # type: ignore[override]
        if not self._search_term:
            return True
        model = self.sourceModel()
        if model is None:
            return True
        column_count = model.columnCount()
        for column in range(column_count):
            index = model.index(source_row, column, source_parent)
            value = model.data(index, Qt.DisplayRole)
            if value and self._search_term in str(value).lower():
                return True
        return False


class SummaryCard(QFrame):
    """Glowing dashboard card."""

    def __init__(self, title: str, variant: str, prefix: str = "", suffix: str = "") -> None:
        super().__init__()
        self.setProperty("role", "summaryCard")
        self.setProperty("variant", variant)
        self._prefix = prefix
        self._suffix = suffix
        self._build_ui(title)

    def _build_ui(self, title: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        self.title_label = QLabel(title.upper())
        self.title_label.setProperty("class", "cardTitle")
        self.value_label = QLabel("--")
        self.value_label.setProperty("class", "cardValue")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

    def update_value(self, value: float | int) -> None:
        if isinstance(value, float) and not value.is_integer():
            text = f"{self._prefix}{value:,.2f}{self._suffix}"
        else:
            text = f"{self._prefix}{int(value):,}{self._suffix}"
        self.value_label.setText(text)


class DetailPanel(QFrame):
    """Shows rich context for the selection."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DetailPanel")
        self.setProperty("role", "detailPanel")
        self._labels: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.hero_label = QLabel("Select an item")
        self.hero_label.setObjectName("HeroLabel")
        self.hero_label.setWordWrap(True)

        layout.addWidget(self.hero_label)

        info_frame = QFrame()
        info_layout = QFormLayout(info_frame)
        info_layout.setLabelAlignment(Qt.AlignLeft)
        info_layout.setFormAlignment(Qt.AlignTop)
        info_layout.setHorizontalSpacing(12)
        info_layout.setVerticalSpacing(10)

        for field in ("SKU", "Category", "Location", "Quantity", "Reorder Level", "Unit Cost"):
            label = QLabel("--")
            label.setObjectName(f"Detail{field.replace(' ', '')}")
            self._labels[field] = label
            info_layout.addRow(f"{field}:", label)

        layout.addWidget(info_frame)

        self.description_title = QLabel("Description")
        self.description_title.setProperty("class", "sectionTitle")
        self.description_label = QLabel("—")
        self.description_label.setWordWrap(True)
        self.description_label.setObjectName("DetailDescription")

        layout.addWidget(self.description_title)
        layout.addWidget(self.description_label)
        layout.addStretch(1)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 18)
        shadow.setColor(QColor(0, 0, 0, 35))
        self.setGraphicsEffect(shadow)

    def display_item(self, item: InventoryDTO | None) -> None:
        if item is None:
            self.hero_label.setText("Select an item to reveal its story.")
            for label in self._labels.values():
                label.setText("--")
            self.description_label.setText("—")
            return

        self.hero_label.setText(f"{item.name}\n<small>{item.category}</small>")
        self._labels["SKU"].setText(item.sku)
        self._labels["Category"].setText(item.category)
        self._labels["Location"].setText(item.location)
        self._labels["Quantity"].setText(f"{item.quantity:,}")
        self._labels["Reorder Level"].setText(f"{item.reorder_level:,}")
        self._labels["Unit Cost"].setText(f"${item.unit_cost:,.2f}")
        self.description_label.setText(item.description or "No description provided.")


class AddEditItemDialog(QDialog):
    """Collects details for new or existing items."""

    def __init__(self, parent: QWidget | None = None, item: InventoryDTO | None = None) -> None:
        super().__init__(parent)
        self._item = item
        self._payload: InventoryCreate | InventoryUpdate | None = None
        self.setWindowTitle("New Inventory Item" if item is None else f"Edit {item.name}")
        self.setModal(True)
        self._build_ui()
        if item:
            self._populate(item)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setVerticalSpacing(12)

        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("SKU-0001-A")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(
            ["Electronics", "Apparel", "Home & Living", "Sports", "Automotive", "Beauty", "Industrial"]
        )

        self.location_input = QComboBox()
        self.location_input.setEditable(True)
        self.location_input.addItems(
            ["Aisle A1", "Aisle B4", "Cold Storage", "Showroom", "Receiving Dock", "Packaging Zone", "Overflow"]
        )

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 1_000_000)
        self.quantity_input.setValue(25)

        self.reorder_input = QSpinBox()
        self.reorder_input.setRange(0, 1_000_000)
        self.reorder_input.setValue(10)

        self.unit_cost_input = QDoubleSpinBox()
        self.unit_cost_input.setRange(0.0, 10_000_000.0)
        self.unit_cost_input.setDecimals(2)
        self.unit_cost_input.setPrefix("$")
        self.unit_cost_input.setValue(25.0)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Curate a vivid, compelling description.")
        self.description_input.setFixedHeight(120)

        self.image_url_input = QLineEdit()
        self.image_url_input.setPlaceholderText("Image URL (optional)")

        form.addRow("SKU", self.sku_input)
        form.addRow("Name", self.name_input)
        form.addRow("Category", self.category_input)
        form.addRow("Location", self.location_input)
        form.addRow("Quantity", self.quantity_input)
        form.addRow("Reorder Level", self.reorder_input)
        form.addRow("Unit Cost", self.unit_cost_input)
        form.addRow("Image URL", self.image_url_input)
        form.addRow("Description", self.description_input)

        layout.addLayout(form)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")
        self.save_button.setProperty("accent", "primary")
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.save_button)
        layout.addLayout(button_row)

        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._on_submit)

        if self._item:
            self.sku_input.setDisabled(True)

    def _populate(self, item: InventoryDTO) -> None:
        self.sku_input.setText(item.sku)
        self.name_input.setText(item.name)
        self.category_input.setCurrentText(item.category)
        self.location_input.setCurrentText(item.location)
        self.quantity_input.setValue(item.quantity)
        self.reorder_input.setValue(item.reorder_level)
        self.unit_cost_input.setValue(item.unit_cost)
        self.description_input.setText(item.description)
        self.image_url_input.setText(item.image_url)

    def _on_submit(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing field", "Name is required.")
            return

        description = self.description_input.toPlainText().strip()
        payload_dict = {
            "name": name,
            "category": self.category_input.currentText().strip(),
            "quantity": self.quantity_input.value(),
            "reorder_level": self.reorder_input.value(),
            "location": self.location_input.currentText().strip(),
            "unit_cost": float(self.unit_cost_input.value()),
            "description": description,
            "image_url": self.image_url_input.text().strip(),
        }

        if self._item is None:
            sku = self.sku_input.text().strip()
            if not sku:
                QMessageBox.warning(self, "Missing field", "SKU is required.")
                return
            payload = InventoryCreate(sku=sku.upper(), **payload_dict)
        else:
            changes = {}
            for field, value in payload_dict.items():
                existing_value = getattr(self._item, field)
                if isinstance(value, str):
                    if value != existing_value:
                        changes[field] = value
                elif isinstance(value, float):
                    if not math.isclose(value, float(existing_value), rel_tol=1e-9):
                        changes[field] = value
                else:
                    if value != existing_value:
                        changes[field] = value

            if not changes:
                QMessageBox.information(self, "No changes", "Nothing to update.")
                return
            payload = InventoryUpdate(**changes)

        self._payload = payload
        self.accept()

    @property
    def payload(self) -> InventoryCreate | InventoryUpdate | None:
        return self._payload


class StockAdjustDialog(QDialog):
    """Prompt for stock adjustments."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Adjust Stock")
        self._value: Optional[int] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        self.spin = QSpinBox()
        self.spin.setRange(-10_000, 10_000)
        self.spin.setValue(5)
        self.spin.setSingleStep(1)
        layout.addWidget(QLabel("Increase (+) or decrease (-) the stock quantity:"))
        layout.addWidget(self.spin)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_btn = QPushButton("Cancel")
        apply_btn = QPushButton("Apply")
        apply_btn.setProperty("accent", "primary")
        button_row.addWidget(cancel_btn)
        button_row.addWidget(apply_btn)
        layout.addLayout(button_row)

        cancel_btn.clicked.connect(self.reject)
        apply_btn.clicked.connect(self._on_accept)

    def _on_accept(self) -> None:
        value = self.spin.value()
        if value == 0:
            QMessageBox.information(self, "No change", "Adjust value cannot be zero.")
            return
        self._value = value
        self.accept()

    @property
    def value(self) -> Optional[int]:
        return self._value


class MainWindow(QMainWindow):
    """Luxuriously styled main window."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AppWindow")
        self.service = InventoryService()
        self.model = InventoryTableModel()
        self.proxy_model = InventoryFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        self.summary_cards: dict[str, SummaryCard] = {}

        self.setWindowTitle("Aurora Warehouse Studio")
        self.resize(1280, 780)
        self.setMinimumSize(QSize(1120, 680))

        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        central = QWidget(self)
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(22)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        title_block = QVBoxLayout()
        title_label = QLabel("Aurora Warehouse")
        title_label.setObjectName("AppTitle")
        subtitle_label = QLabel("Orchestrate stock with flair and precision.")
        subtitle_label.setObjectName("AppSubtitle")
        title_block.addWidget(title_label)
        title_block.addWidget(subtitle_label)

        header_layout.addLayout(title_block)
        header_layout.addStretch(1)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search SKU, name, category, or location")
        self.search_field.setClearButtonEnabled(True)
        header_layout.addWidget(self.search_field, stretch=2)

        main_layout.addLayout(header_layout)

        cards_container = QHBoxLayout()
        cards_container.setSpacing(16)

        self.summary_cards["total_sku"] = SummaryCard("Active SKUs", "plum")
        self.summary_cards["total_quantity"] = SummaryCard("Units On Hand", "azure")
        self.summary_cards["inventory_value"] = SummaryCard("Inventory Value", "sun", prefix="$")
        self.summary_cards["low_stock"] = SummaryCard("Low Stock Alerts", "ember")

        for card in self.summary_cards.values():
            cards_container.addWidget(card)

        main_layout.addLayout(cards_container)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.add_button = QPushButton("Add Item")
        self.add_button.setProperty("accent", "primary")
        self.edit_button = QPushButton("Edit")
        self.edit_button.setProperty("accent", "secondary")
        self.adjust_button = QPushButton("Adjust Stock")
        self.bulk_seed_button = QPushButton("Populate Demo")
        self.delete_button = QPushButton("Delete")
        self.delete_button.setProperty("accent", "danger")
        self.refresh_button = QPushButton("Refresh")

        for widget in (
            self.add_button,
            self.edit_button,
            self.adjust_button,
            self.bulk_seed_button,
            self.delete_button,
            self.refresh_button,
        ):
            action_row.addWidget(widget)

        action_row.addStretch(1)
        main_layout.addLayout(action_row)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)

        table_frame = QFrame()
        table_frame.setObjectName("TableFrame")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSortingEnabled(True)
        self.table_view.setObjectName("InventoryTable")

        table_layout.addWidget(self.table_view)
        self.splitter.addWidget(table_frame)

        self.detail_panel = DetailPanel()
        self.detail_panel.setMinimumWidth(320)
        self.splitter.addWidget(self.detail_panel)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)

        main_layout.addWidget(self.splitter, stretch=1)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.search_field.textChanged.connect(self.proxy_model.set_search_term)
        self.add_button.clicked.connect(self.on_add_item)
        self.edit_button.clicked.connect(self.on_edit_item)
        self.delete_button.clicked.connect(self.on_delete_item)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.bulk_seed_button.clicked.connect(self.on_populate_demo)
        self.adjust_button.clicked.connect(self.on_adjust_stock)
        self.table_view.doubleClicked.connect(lambda _: self.on_edit_item())
        self.table_view.selectionModel().currentChanged.connect(lambda *_: self._update_detail_panel())

    def refresh_data(self) -> None:
        try:
            items = self.service.list_items()
            self.model.update_items(items)
            self.proxy_model.invalidate()
            summary = self.service.summary()
            self._update_summary(summary)
            self._update_detail_panel()
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Load failed", f"Unable to fetch inventory data.\n{exc}")

    def _update_summary(self, summary: InventorySummary) -> None:
        self.summary_cards["total_sku"].update_value(summary.total_sku)
        self.summary_cards["total_quantity"].update_value(summary.total_quantity)
        self.summary_cards["inventory_value"].update_value(summary.inventory_value)
        self.summary_cards["low_stock"].update_value(summary.low_stock_count)

    def _update_detail_panel(self) -> None:
        item = self.current_item()
        self.detail_panel.display_item(item)

    def current_item(self) -> InventoryDTO | None:
        selection = self.table_view.selectionModel()
        if not selection:
            return None
        indexes = selection.selectedRows()
        if not indexes:
            return None
        source_index = self.proxy_model.mapToSource(indexes[0])
        return self.model.item_at(source_index.row())

    def on_add_item(self) -> None:
        dialog = AddEditItemDialog(self)
        if dialog.exec() == QDialog.Accepted and dialog.payload:
            payload = dialog.payload
            if isinstance(payload, InventoryCreate):
                try:
                    self.service.create_item(payload)
                except RepositoryError as exc:
                    QMessageBox.critical(self, "Create failed", str(exc))
                    return
                self.refresh_data()

    def on_edit_item(self) -> None:
        item = self.current_item()
        if item is None:
            QMessageBox.information(self, "No selection", "Choose an item to edit.")
            return
        dialog = AddEditItemDialog(self, item=item)
        if dialog.exec() == QDialog.Accepted and dialog.payload:
            payload = dialog.payload
            if isinstance(payload, InventoryUpdate):
                try:
                    self.service.update_item(item.id, payload)
                except RepositoryError as exc:
                    QMessageBox.critical(self, "Update failed", str(exc))
                    return
                self.refresh_data()

    def on_adjust_stock(self) -> None:
        item = self.current_item()
        if item is None:
            QMessageBox.information(self, "No selection", "Choose an item to adjust.")
            return
        dialog = StockAdjustDialog(self)
        if dialog.exec() == QDialog.Accepted and dialog.value:
            try:
                self.service.adjust_stock(item.id, dialog.value)
            except RepositoryError as exc:
                QMessageBox.warning(self, "Adjustment failed", str(exc))
                return
            self.refresh_data()

    def on_delete_item(self) -> None:
        item = self.current_item()
        if item is None:
            QMessageBox.information(self, "No selection", "Choose an item to delete.")
            return
        response = QMessageBox.question(
            self,
            "Confirm delete",
            f"Remove {item.name} ({item.sku}) from inventory?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if response == QMessageBox.Yes:
            try:
                self.service.delete_item(item.id)
            except RepositoryError as exc:
                QMessageBox.warning(self, "Delete failed", str(exc))
                return
            self.refresh_data()

    def on_populate_demo(self) -> None:
        try:
            from faker import Faker
        except ImportError:  # pragma: no cover - dependency managed via requirements
            QMessageBox.critical(self, "Missing dependency", "Install Faker to generate demo data.")
            return

        answer = QMessageBox.question(
            self,
            "Generate demo data",
            "Populate the warehouse with curated sample items?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        fake = Faker()
        demo_records = []
        for _ in range(32):
            payload = InventoryCreate(
                sku=fake.unique.bothify("SKU-####-??").upper(),
                name=fake.catch_phrase(),
                category=fake.random_element(
                    elements=["Electronics", "Apparel", "Sports", "Lifestyle", "Industrial", "Beauty"]
                ),
                quantity=fake.random_int(min=5, max=250),
                reorder_level=fake.random_int(min=10, max=60),
                location=fake.random_element(
                    elements=["Aisle A1", "Aisle B4", "Cold Storage", "Showroom", "Packaging Zone", "Overflow"]
                ),
                unit_cost=round(fake.random_number(digits=4) / 4.5, 2),
                description=fake.sentence(nb_words=18),
                image_url=f"https://source.unsplash.com/random/400x300?sig={fake.uuid4()}",
            )
            demo_records.append(payload)
        try:
            self.service.bulk_upsert(demo_records)
        except RepositoryError as exc:
            QMessageBox.warning(self, "Populate failed", str(exc))
            return
        fake.unique.clear()
        self.refresh_data()
        QMessageBox.information(self, "Success", "Demo inventory crafted successfully.")


def create_main_window() -> MainWindow:
    """Factory for the main window."""
    return MainWindow()


