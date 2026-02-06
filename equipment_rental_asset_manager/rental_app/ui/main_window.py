from __future__ import annotations

from datetime import date

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .. import services
from .icons import icon
from .dialogs import (
    AssetDialog,
    AssetFormData,
    CustomerDialog,
    CustomerFormData,
    RentalDialog,
    message_confirm,
    message_error,
)
from .widgets import CardFrame, DangerButton, PillLabel, PrimaryButton


def _item(text: str, *, align: Qt.AlignmentFlag | None = None) -> QTableWidgetItem:
    it = QTableWidgetItem(text)
    it.setFlags(it.flags() & ~Qt.ItemIsEditable)
    if align is not None:
        it.setTextAlignment(int(align))
    return it


def _money(x: float) -> str:
    return f"${x:,.2f}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aurum Rentals — Equipment Rental & Asset Management")
        self.setMinimumSize(1200, 720)

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        self.sidebar = self._build_sidebar()
        root_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        self.dashboard = DashboardPage()
        self.assets = AssetsPage()
        self.customers = CustomersPage()
        self.rentals = RentalsPage()
        self.pages = [self.dashboard, self.assets, self.customers, self.rentals]

        for p in self.pages:
            self.stack.addWidget(p)

        self._wire_nav()
        self._set_page(0)

        # Refresh in the background so overdue status stays lively.
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(15_000)
        self._refresh_timer.timeout.connect(self.refresh_all)
        self._refresh_timer.start()

        self.refresh_all()

    def refresh_all(self) -> None:
        for p in self.pages:
            if hasattr(p, "refresh"):
                p.refresh()

    def _build_sidebar(self) -> QFrame:
        sb = QFrame()
        sb.setObjectName("Sidebar")
        sb.setMinimumWidth(270)
        sb.setMaximumWidth(310)
        sb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(sb)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("Aurum Rentals")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Asset Management • Rentals • Returns")
        subtitle.setObjectName("AppSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        self.btn_dashboard = self._nav_button("Dashboard", "KPIs & due soon", icon_name="dashboard")
        self.btn_assets = self._nav_button("Assets", "Inventory, status, notes", icon_name="box")
        self.btn_customers = self._nav_button("Customers", "Contacts & companies", icon_name="users")
        self.btn_rentals = self._nav_button("Rentals", "Create + return rentals", icon_name="rentals")

        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_assets)
        layout.addWidget(self.btn_customers)
        layout.addWidget(self.btn_rentals)

        layout.addStretch(1)

        hint = QLabel("Tip: double-click rows to edit.")
        hint.setStyleSheet("color: rgba(231,234,243,0.65);")
        layout.addWidget(hint)

        return sb

    def _nav_button(self, title: str, subtitle: str, *, icon_name: str) -> QToolButton:
        b = QToolButton()
        b.setObjectName("NavButton")
        b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        b.setIcon(icon(icon_name))
        b.setIconSize(QSize(20, 20))
        b.setText(f"{title}\n{subtitle}")
        b.setProperty("active", False)
        b.setCursor(Qt.PointingHandCursor)
        b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return b

    def _wire_nav(self) -> None:
        self.btn_dashboard.clicked.connect(lambda: self._set_page(0))
        self.btn_assets.clicked.connect(lambda: self._set_page(1))
        self.btn_customers.clicked.connect(lambda: self._set_page(2))
        self.btn_rentals.clicked.connect(lambda: self._set_page(3))

    def _set_page(self, idx: int) -> None:
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate([self.btn_dashboard, self.btn_assets, self.btn_customers, self.btn_rentals]):
            btn.setProperty("active", i == idx)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()
        w = self.stack.currentWidget()
        if hasattr(w, "refresh"):
            w.refresh()


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = self._header("Dashboard", "Live overview of assets and rentals")
        layout.addWidget(header)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        layout.addLayout(kpi_row)

        self.card_total = self._kpi_card("Total Assets", "0", kind="neutral")
        self.card_available = self._kpi_card("Available", "0", kind="good")
        self.card_rented = self._kpi_card("Rented", "0", kind="warn")
        self.card_overdue = self._kpi_card("Overdue Rentals", "0", kind="bad")
        for c in [self.card_total, self.card_available, self.card_rented, self.card_overdue]:
            kpi_row.addWidget(c, 1)

        self.due_table = QTableWidget(0, 3)
        self.due_table.setHorizontalHeaderLabels(["Due", "Asset", "Customer"])
        self.due_table.verticalHeader().setVisible(False)
        self.due_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.due_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.due_table.setAlternatingRowColors(True)
        self.due_table.setShowGrid(False)
        self.due_table.setSortingEnabled(False)

        card = CardFrame()
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(10)

        title = QLabel("Due soon")
        title.setStyleSheet("font-weight: 900; font-size: 14px;")
        hint = QLabel("Active rentals sorted by due date (overdue float to the top).")
        hint.setStyleSheet("color: rgba(231,234,243,0.70);")

        c_layout.addWidget(title)
        c_layout.addWidget(hint)
        c_layout.addWidget(self.due_table)
        layout.addWidget(card, 1)

    def refresh(self) -> None:
        k = services.compute_kpis()
        self._set_kpi(self.card_total, str(k.total_assets))
        self._set_kpi(self.card_available, str(k.available_assets))
        self._set_kpi(self.card_rented, str(k.rented_assets))
        self._set_kpi(self.card_overdue, str(k.overdue_rentals))

        rows = services.due_soon(limit=10)
        self.due_table.setRowCount(0)
        for r in rows:
            row_idx = self.due_table.rowCount()
            self.due_table.insertRow(row_idx)
            due = r["due_date"]
            due_it = _item(due, align=Qt.AlignVCenter | Qt.AlignLeft)
            if date.fromisoformat(due) < date.today():
                due_it.setForeground(Qt.red)
            self.due_table.setItem(row_idx, 0, due_it)
            self.due_table.setItem(row_idx, 1, _item(f'{r["asset_tag"]} — {r["asset_name"]}'))
            cust = r["customer_name"]
            if r["customer_company"]:
                cust = f'{cust} ({r["customer_company"]})'
            self.due_table.setItem(row_idx, 2, _item(cust))

        self.due_table.resizeColumnsToContents()
        self.due_table.horizontalHeader().setStretchLastSection(True)

    def _header(self, title: str, hint: str) -> QWidget:
        bar = CardFrame(radius=18)
        bar.setObjectName("TopBar")
        l = QVBoxLayout(bar)
        l.setContentsMargins(18, 14, 18, 14)
        t = QLabel(title)
        t.setObjectName("PageTitle")
        h = QLabel(hint)
        h.setObjectName("PageHint")
        l.addWidget(t)
        l.addWidget(h)
        return bar

    def _kpi_card(self, title: str, value: str, *, kind: str) -> QWidget:
        card = CardFrame()
        l = QVBoxLayout(card)
        l.setContentsMargins(16, 14, 16, 14)
        l.setSpacing(6)
        t = QLabel(title)
        t.setStyleSheet("font-weight: 800; color: rgba(231,234,243,0.80);")
        v = QLabel(value)
        v.setProperty("kpi", "value")
        v.setStyleSheet("font-size: 28px; font-weight: 900;")
        pill = PillLabel(kind.upper(), kind=kind)
        pill.setMaximumWidth(120)
        l.addWidget(t)
        l.addWidget(v)
        l.addWidget(pill, alignment=Qt.AlignLeft)
        card._kpi_value = v  # type: ignore[attr-defined]
        return card

    def _set_kpi(self, card: QWidget, value: str) -> None:
        v = getattr(card, "_kpi_value", None)
        if v is not None:
            v.setText(value)


class AssetsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = self._header("Assets", "Track inventory, rates, condition, and availability")
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search tag, name, category…")
        self.search.textChanged.connect(self.refresh)

        self.btn_add = PrimaryButton("Add Asset")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = DangerButton("Delete")
        self.btn_add.clicked.connect(self.add_asset)
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_delete.clicked.connect(self.delete_selected)

        toolbar.addWidget(self.search, 1)
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Tag", "Name", "Category", "Rate", "Status", "Condition"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.itemDoubleClicked.connect(lambda _it: self.edit_selected())

        layout.addWidget(self.table, 1)

    def refresh(self) -> None:
        rows = services.list_assets(self.search.text())
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            tag = _item(r["tag"])
            tag.setData(Qt.UserRole, int(r["id"]))
            self.table.setItem(i, 0, tag)
            self.table.setItem(i, 1, _item(r["name"]))
            self.table.setItem(i, 2, _item(r["category"]))
            self.table.setItem(i, 3, _item(_money(float(r["daily_rate"])), align=Qt.AlignVCenter | Qt.AlignRight))
            self.table.setItem(i, 4, _item(r["status"]))
            self.table.setItem(i, 5, _item(r["condition"]))

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def _selected_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return int(self.table.item(items[0].row(), 0).data(Qt.UserRole))

    def add_asset(self) -> None:
        dlg = AssetDialog(title="Add Asset", parent=self)
        if dlg.exec() != dlg.Accepted:
            return
        data = dlg.data()
        if not data.tag or not data.name or not data.category:
            message_error(self, "Missing fields", "Please fill Tag, Name, and Category.")
            return
        try:
            services.create_asset(
                tag=data.tag,
                name=data.name,
                category=data.category,
                daily_rate=data.daily_rate,
                status=data.status,
                condition=data.condition,
                notes=data.notes,
            )
        except Exception as e:
            message_error(self, "Could not create asset", str(e))
        self.refresh()

    def edit_selected(self) -> None:
        asset_id = self._selected_id()
        if asset_id is None:
            return
        row = services.get_asset(asset_id)
        if not row:
            return
        initial = AssetFormData(
            tag=row["tag"],
            name=row["name"],
            category=row["category"],
            daily_rate=float(row["daily_rate"]),
            status=row["status"],
            condition=row["condition"],
            notes=row["notes"],
        )
        dlg = AssetDialog(title=f"Edit Asset — {row['tag']}", initial=initial, parent=self)
        if dlg.exec() != dlg.Accepted:
            return
        data = dlg.data()
        if not data.tag or not data.name or not data.category:
            message_error(self, "Missing fields", "Please fill Tag, Name, and Category.")
            return
        try:
            services.update_asset(
                asset_id=asset_id,
                tag=data.tag,
                name=data.name,
                category=data.category,
                daily_rate=data.daily_rate,
                status=data.status,
                condition=data.condition,
                notes=data.notes,
            )
        except Exception as e:
            message_error(self, "Could not update asset", str(e))
        self.refresh()

    def delete_selected(self) -> None:
        asset_id = self._selected_id()
        if asset_id is None:
            return
        if not message_confirm(self, "Delete asset?", "This will permanently remove the asset.\n\nContinue?"):
            return
        try:
            services.delete_asset(asset_id)
        except Exception as e:
            message_error(self, "Could not delete asset", str(e))
        self.refresh()

    def _header(self, title: str, hint: str) -> QWidget:
        bar = CardFrame(radius=18)
        bar.setObjectName("TopBar")
        l = QVBoxLayout(bar)
        l.setContentsMargins(18, 14, 18, 14)
        t = QLabel(title)
        t.setObjectName("PageTitle")
        h = QLabel(hint)
        h.setObjectName("PageHint")
        l.addWidget(t)
        l.addWidget(h)
        return bar


class CustomersPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        layout.addWidget(self._header("Customers", "Keep track of people and companies you rent to"))

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search name, company, email, phone…")
        self.search.textChanged.connect(self.refresh)

        self.btn_add = PrimaryButton("Add Customer")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = DangerButton("Delete")
        self.btn_add.clicked.connect(self.add_customer)
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_delete.clicked.connect(self.delete_selected)

        toolbar.addWidget(self.search, 1)
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Company", "Email", "Phone"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.itemDoubleClicked.connect(lambda _it: self.edit_selected())

        layout.addWidget(self.table, 1)

    def refresh(self) -> None:
        rows = services.list_customers(self.search.text())
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            name = _item(r["name"])
            name.setData(Qt.UserRole, int(r["id"]))
            self.table.setItem(i, 0, name)
            self.table.setItem(i, 1, _item(r["company"]))
            self.table.setItem(i, 2, _item(r["email"]))
            self.table.setItem(i, 3, _item(r["phone"]))

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def _selected_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return int(self.table.item(items[0].row(), 0).data(Qt.UserRole))

    def add_customer(self) -> None:
        dlg = CustomerDialog(title="Add Customer", parent=self)
        if dlg.exec() != dlg.Accepted:
            return
        data = dlg.data()
        if not data.name:
            message_error(self, "Missing fields", "Please fill the customer name.")
            return
        try:
            services.create_customer(name=data.name, company=data.company, email=data.email, phone=data.phone)
        except Exception as e:
            message_error(self, "Could not create customer", str(e))
        self.refresh()

    def edit_selected(self) -> None:
        cust_id = self._selected_id()
        if cust_id is None:
            return
        # Reuse list query to get current row
        rows = services.list_customers("")
        row = next((r for r in rows if int(r["id"]) == cust_id), None)
        if not row:
            return
        initial = CustomerFormData(
            name=row["name"],
            company=row["company"],
            email=row["email"],
            phone=row["phone"],
        )
        dlg = CustomerDialog(title=f"Edit Customer — {row['name']}", initial=initial, parent=self)
        if dlg.exec() != dlg.Accepted:
            return
        data = dlg.data()
        if not data.name:
            message_error(self, "Missing fields", "Please fill the customer name.")
            return
        try:
            services.update_customer(customer_id=cust_id, name=data.name, company=data.company, email=data.email, phone=data.phone)
        except Exception as e:
            message_error(self, "Could not update customer", str(e))
        self.refresh()

    def delete_selected(self) -> None:
        cust_id = self._selected_id()
        if cust_id is None:
            return
        if not message_confirm(self, "Delete customer?", "This will permanently remove the customer.\n\nContinue?"):
            return
        try:
            services.delete_customer(cust_id)
        except Exception as e:
            message_error(self, "Could not delete customer", str(e))
        self.refresh()

    def _header(self, title: str, hint: str) -> QWidget:
        bar = CardFrame(radius=18)
        bar.setObjectName("TopBar")
        l = QVBoxLayout(bar)
        l.setContentsMargins(18, 14, 18, 14)
        t = QLabel(title)
        t.setObjectName("PageTitle")
        h = QLabel(hint)
        h.setObjectName("PageHint")
        l.addWidget(t)
        l.addWidget(h)
        return bar


class RentalsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        layout.addWidget(self._header("Rentals", "Create rentals, track due dates, and process returns"))

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.filter = QComboBox()
        self.filter.addItem("Active", "active")
        self.filter.addItem("Returned", "returned")
        self.filter.addItem("All", "all")
        self.filter.currentIndexChanged.connect(self.refresh)

        self.btn_new = PrimaryButton("New Rental")
        self.btn_return = QPushButton("Return Selected")
        self.btn_new.clicked.connect(self.new_rental)
        self.btn_return.clicked.connect(self.return_selected)

        toolbar.addWidget(QLabel("Filter"))
        toolbar.addWidget(self.filter)
        toolbar.addStretch(1)
        toolbar.addWidget(self.btn_new)
        toolbar.addWidget(self.btn_return)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Status", "Asset", "Customer", "Start", "Due", "Returned", "Rate", "Deposit"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        layout.addWidget(self.table, 1)

    def refresh(self) -> None:
        mode = str(self.filter.currentData())
        rows = services.list_rentals(mode)
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)

            status = "Returned" if r["return_date"] is not None else "Active"
            if services.rental_is_overdue(r):
                status = "Overdue"

            st = _item(status)
            st.setData(Qt.UserRole, int(r["id"]))
            if status == "Overdue":
                st.setForeground(Qt.red)
            self.table.setItem(i, 0, st)

            self.table.setItem(i, 1, _item(f'{r["asset_tag"]} — {r["asset_name"]}'))
            cust = r["customer_name"]
            if r["customer_company"]:
                cust = f'{cust} ({r["customer_company"]})'
            self.table.setItem(i, 2, _item(cust))

            self.table.setItem(i, 3, _item(r["start_date"]))
            self.table.setItem(i, 4, _item(r["due_date"]))
            self.table.setItem(i, 5, _item(r["return_date"] or "—"))
            self.table.setItem(i, 6, _item(_money(float(r["daily_rate"])), align=Qt.AlignVCenter | Qt.AlignRight))
            self.table.setItem(i, 7, _item(_money(float(r["deposit"])), align=Qt.AlignVCenter | Qt.AlignRight))

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def _selected_rental_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return int(self.table.item(items[0].row(), 0).data(Qt.UserRole))

    def new_rental(self) -> None:
        assets = services.list_available_assets()
        customers = services.list_customer_choices()
        if not assets:
            message_error(self, "No available assets", "All assets are currently rented or in maintenance.")
            return
        if not customers:
            message_error(self, "No customers", "Please add a customer first.")
            return

        asset_choices: list[tuple[int, str, float]] = []
        for a in assets:
            label = f'{a["tag"]} — {a["name"]}  ({_money(float(a["daily_rate"]))}/day)'
            asset_choices.append((int(a["id"]), label, float(a["daily_rate"])))

        cust_choices: list[tuple[int, str]] = []
        for c in customers:
            label = c["name"]
            if c["company"]:
                label = f'{label} ({c["company"]})'
            cust_choices.append((int(c["id"]), label))

        dlg = RentalDialog(
            title="New Rental",
            asset_choices=asset_choices,
            customer_choices=cust_choices,
            parent=self,
        )
        if dlg.exec() != dlg.Accepted:
            return

        data = dlg.data()
        try:
            services.create_rental(
                asset_id=data.asset_id,
                customer_id=data.customer_id,
                start_date=data.start_date,
                due_date=data.due_date,
                daily_rate=data.daily_rate,
                deposit=data.deposit,
                notes=data.notes,
            )
        except Exception as e:
            message_error(self, "Could not create rental", str(e))
        self.refresh()

    def return_selected(self) -> None:
        rid = self._selected_rental_id()
        if rid is None:
            return
        if not message_confirm(self, "Return rental?", "Mark the selected rental as returned today?"):
            return
        try:
            services.return_rental(rental_id=rid)
        except Exception as e:
            message_error(self, "Could not return rental", str(e))
        self.refresh()

    def _header(self, title: str, hint: str) -> QWidget:
        bar = CardFrame(radius=18)
        bar.setObjectName("TopBar")
        l = QVBoxLayout(bar)
        l.setContentsMargins(18, 14, 18, 14)
        t = QLabel(title)
        t.setObjectName("PageTitle")
        h = QLabel(hint)
        h.setObjectName("PageHint")
        l.addWidget(t)
        l.addWidget(h)
        return bar

