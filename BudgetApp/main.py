"""
BudgetWise � Personal Budget Management
A visually stunning mobile app built with Flet.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import flet as ft

# Data & Storage

DATA_FILE = Path(__file__).parent / "budget_data.json"

DEFAULT_CATEGORIES = [
    {"id": "food", "name": "Food & Dining", "icon": "restaurant", "color": "0xffe07c5e"},
    {"id": "transport", "name": "Transport", "icon": "directions_car", "color": "0xff4ecdc4"},
    {"id": "shopping", "name": "Shopping", "icon": "shopping_bag", "color": "0xff95e1d3"},
    {"id": "entertainment", "name": "Entertainment", "icon": "movie", "color": "0xfff38181"},
    {"id": "bills", "name": "Bills & Utilities", "icon": "receipt_long", "color": "0xffaa96da"},
    {"id": "health", "name": "Health", "icon": "favorite", "color": "0xfffcbad3"},
    {"id": "income", "name": "Salary & Income", "icon": "account_balance_wallet", "color": "0xffa8e6cf"},
]


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {
            "transactions": [],
            "categories": [c.copy() for c in DEFAULT_CATEGORIES],
            "budget_goals": {},
        }
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Theme & Colors

BG_GRADIENT = ft.LinearGradient(
    begin=ft.Alignment.TOP_LEFT,
    end=ft.Alignment.BOTTOM_RIGHT,
    colors=["0xff0f0c29", "0xff302b63", "0xff24243e"],
)

CARD_BG = "0x1affffff"
CARD_BORDER = "0x28ffffff"
INCOME_COLOR = "0xff00d9a5"
EXPENSE_COLOR = "0xffff6b6b"
ACCENT = "0xff7c3aed"
ACCENT_LIGHT = "0xffa78bfa"
TEXT_PRIMARY = "0xfff8fafc"
TEXT_SECONDARY = "0xff94a3b8"
TEXT_MUTED = "0xff64748b"


def this_month() -> str:
    return datetime.now().strftime("%Y-%m")


def format_currency(value: float) -> str:
    v = abs(float(value)) if value is not None else 0.0
    return f"${v:,.2f}"


def parse_amount(s: str) -> float:
    try:
        return max(0, float(str(s).replace(",", "").replace("$", "").strip()))
    except (ValueError, TypeError, AttributeError):
        return 0.0


def glass_card(
    content: ft.Control,
    padding: int = 16,
    border_radius: int = 20,
    on_click=None,
) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=border_radius,
        bgcolor=CARD_BG,
        border=ft.Border.all(1, CARD_BORDER),
        on_click=on_click,
    )


def section_title(title: str, icon: Optional[str] = None) -> ft.Control:
    parts = []
    if icon:
        parts.append(ft.Icon(icon, color=ACCENT_LIGHT, size=20))
    parts.append(ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY))
    return ft.Row(parts, spacing=8)


def stat_card(label: str, value: str, color: str, icon: str) -> ft.Control:
    return glass_card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color=color, size=20),
                            bgcolor=f"{color}28",
                            padding=8,
                            border_radius=12,
                        ),
                        ft.Text(label, size=12, color=TEXT_SECONDARY),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=color),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=16,
    )


def main(page: ft.Page) -> None:
    data = load_data()
    transactions: list[dict] = data["transactions"]
    categories: list[dict] = data["categories"]
    budget_goals: dict[str, float] = data.get("budget_goals", {})

    def persist() -> None:
        save_data({
            "transactions": transactions,
            "categories": categories,
            "budget_goals": budget_goals,
        })

    month_filter = [this_month()]

    def transactions_this_month() -> list[dict]:
        return [t for t in transactions if (t.get("date") or "")[:7] == month_filter[0]]

    def total_income() -> float:
        return sum(t["amount"] for t in transactions_this_month() if t.get("type") == "income")

    def total_expense() -> float:
        return sum(t["amount"] for t in transactions_this_month() if t.get("type") == "expense")

    def balance() -> float:
        return total_income() - total_expense()

    def expense_by_category() -> dict[str, float]:
        out: dict[str, float] = {}
        for t in transactions_this_month():
            if t.get("type") != "expense":
                continue
            cat = t.get("category", "other")
            out[cat] = out.get(cat, 0) + t["amount"]
        return out

    def category_name(cat_id: str) -> str:
        for c in categories:
            if c.get("id") == cat_id:
                return c.get("name", cat_id)
        return cat_id or ""

    def category_color(cat_id: str) -> str:
        for c in categories:
            if c.get("id") == cat_id:
                return c.get("color", TEXT_MUTED)
        return TEXT_MUTED

    # Views

    body_container = ft.Ref[ft.Container]()
    nav_bar = ft.Ref[ft.NavigationBar]()

    def build_dashboard() -> ft.Column:
        inc = total_income()
        exp = total_expense()
        bal = balance()
        by_cat = expense_by_category()
        total_exp_cat = sum(by_cat.values()) or 1

        header = ft.Column(
            [
                ft.Text("Your finances", size=14, color=TEXT_SECONDARY),
                ft.Text("at a glance", size=26, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ],
            spacing=4,
        )

        balance_card = glass_card(
            ft.Column(
                [
                    ft.Text("Current balance", size=14, color=TEXT_SECONDARY),
                    ft.Text(
                        format_currency(bal),
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=INCOME_COLOR if bal >= 0 else EXPENSE_COLOR,
                    ),
                    ft.Text(
                        datetime.now().strftime("%B %Y"),
                        size=12,
                        color=TEXT_MUTED,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=24,
        )

        stats = ft.Row(
            [
                stat_card("Income", format_currency(inc), INCOME_COLOR, "trending_up"),
                stat_card("Expenses", format_currency(exp), EXPENSE_COLOR, "trending_down"),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

        bar_items: list[ft.Control] = []
        for cat_id, amount in sorted(by_cat.items(), key=lambda x: -x[1])[:6]:
            pct = (amount / total_exp_cat) * 100
            bar_items.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(category_name(cat_id), size=13, color=TEXT_PRIMARY, expand=True),
                                ft.Text(format_currency(amount), size=13, color=TEXT_SECONDARY),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.ProgressBar(
                            value=pct / 100,
                            color=category_color(cat_id),
                            bgcolor=TEXT_MUTED + "44",
                            bar_height=8,
                            border_radius=4,
                        ),
                    ],
                    spacing=6,
                )
            )

        chart_card = glass_card(
            ft.Column(
                [section_title("Spending by category", "pie_chart")] + bar_items,
                spacing=16,
            ),
        ) if bar_items else glass_card(
            ft.Column(
                [
                    section_title("Spending by category", "pie_chart"),
                    ft.Text("No expenses this month yet.", size=14, color=TEXT_MUTED),
                ],
                spacing=12,
            ),
        )

        recent = list(transactions_this_month())[-5:][::-1]
        recent_list: list[ft.Control] = []
        for t in recent:
            is_inc = t.get("type") == "income"
            recent_list.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(
                                    "arrow_upward" if is_inc else "arrow_downward",
                                    color=INCOME_COLOR if is_inc else EXPENSE_COLOR,
                                    size=18,
                                ),
                                bgcolor=(INCOME_COLOR if is_inc else EXPENSE_COLOR) + "22",
                                padding=8,
                                border_radius=10,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        t.get("note") or category_name(t.get("category", "")),
                                        size=14,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ft.Text(t.get("date", ""), size=11, color=TEXT_MUTED),
                                ],
                                spacing=2,
                                expand=True,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                            ),
                            ft.Text(
                                ("+" if is_inc else "-") + format_currency(t["amount"]),
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=INCOME_COLOR if is_inc else EXPENSE_COLOR,
                            ),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    padding=ft.Padding.symmetric(vertical=8),
                )
            )

        recent_card = glass_card(
            ft.Column(
                [
                    section_title("Recent activity", "history"),
                    ft.Column(recent_list, spacing=0)
                    if recent_list
                    else ft.Text("No transactions yet.", size=14, color=TEXT_MUTED),
                ],
                spacing=16,
            ),
        )

        return ft.Column(
            [
                header,
                balance_card,
                stats,
                chart_card,
                recent_card,
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def build_history() -> ft.Column:
        month_start = datetime.now().replace(day=1)
        months = [(month_start - timedelta(days=31 * i)).strftime("%Y-%m") for i in range(12)]

        def on_month(e: ft.ControlEvent) -> None:
            val = e.control.value
            if val:
                month_filter[0] = val
                refresh_views()
                page.update()

        def month_label(ym: str) -> str:
            try:
                d = datetime.strptime(ym + "-01", "%Y-%m-%d")
                return d.strftime("%B %Y")
            except Exception:
                return ym

        dd = ft.Dropdown(
            label="Month",
            value=month_filter[0],
            options=[ft.dropdown.Option(m, month_label(m)) for m in months],
            border_color=ACCENT_LIGHT,
            focused_border_color=ACCENT,
            fill_color=CARD_BG,
            on_select=on_month,
        )

        filtered = [t for t in transactions if (t.get("date") or "")[:7] == month_filter[0]]
        rows: list[ft.Control] = []
        for t in sorted(filtered, key=lambda x: x.get("date", ""), reverse=True):
            is_inc = t.get("type") == "income"
            rows.append(
                glass_card(
                    ft.Row(
                        [
                            ft.Container(
                                ft.Icon(
                                    "arrow_upward" if is_inc else "arrow_downward",
                                    color=INCOME_COLOR if is_inc else EXPENSE_COLOR,
                                    size=20,
                                ),
                                bgcolor=(INCOME_COLOR if is_inc else EXPENSE_COLOR) + "22",
                                padding=10,
                                border_radius=12,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        t.get("note") or category_name(t.get("category", "")),
                                        size=14,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ft.Text(t.get("date", ""), size=12, color=TEXT_MUTED),
                                ],
                                spacing=2,
                                expand=True,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                            ),
                            ft.Text(
                                ("+" if is_inc else "-") + format_currency(t["amount"]),
                                size=15,
                                weight=ft.FontWeight.W_600,
                                color=INCOME_COLOR if is_inc else EXPENSE_COLOR,
                            ),
                        ],
                        spacing=12,
                    ),
                    padding=14,
                )
            )

        return ft.Column(
            [
                section_title("Transaction history", "list"),
                dd,
                ft.Column(rows, spacing=10)
                if rows
                else glass_card(ft.Text("No transactions for this month.", size=14, color=TEXT_MUTED)),
            ],
            spacing=16,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def build_goals() -> ft.Column:
        by_cat = expense_by_category()
        goal_rows: list[ft.Control] = []
        for c in categories:
            if c.get("id") == "income":
                continue
            cat_id = c["id"]
            spent = by_cat.get(cat_id, 0)
            limit = budget_goals.get(cat_id, 0)
            name = c.get("name", cat_id)
            color = c.get("color", ACCENT_LIGHT)
            if limit <= 0:
                pct = 0.0
                status = "No limit set"
            else:
                pct = min(1.0, (spent / limit))
                status = f"{format_currency(spent)} / {format_currency(limit)}"
            goal_rows.append(
                glass_card(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(name, size=14, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                                    ft.Text(status, size=12, color=TEXT_SECONDARY),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.ProgressBar(
                                value=pct,
                                color=color,
                                bgcolor=TEXT_MUTED + "44",
                                bar_height=8,
                                border_radius=4,
                            ),
                        ],
                        spacing=10,
                    ),
                )
            )

        return ft.Column(
            [
                section_title("Budget goals", "flag"),
                ft.Text(
                    "Track spending vs. monthly limits per category.",
                    size=14,
                    color=TEXT_SECONDARY,
                ),
                ft.Column(goal_rows, spacing=12)
                if goal_rows
                else glass_card(
                    ft.Text("Set limits in Goals to track progress.", size=14, color=TEXT_MUTED)
                ),
            ],
            spacing=16,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    nav_index = [0]

    def refresh_views() -> None:
        if not body_container.current:
            return
        idx = nav_index[0]
        if idx == 0:
            body_container.current.content = build_dashboard()
        elif idx == 1:
            body_container.current.content = build_history()
        else:
            body_container.current.content = build_goals()

    def go_back(_: ft.ControlEvent) -> None:
        if body_container.current:
            body_container.current.content = build_dashboard()
            nav_index[0] = 0
            if nav_bar.current is not None:
                nav_bar.current.selected_index = 0
        page.update()

    def open_add(_: ft.ControlEvent) -> None:
        amount_ref = ft.Ref[ft.TextField]()
        note_ref = ft.Ref[ft.TextField]()
        type_ref = ft.Ref[ft.Dropdown]()
        cat_ref = ft.Ref[ft.Dropdown]()
        expense_cats = [c for c in categories if c.get("id") != "income"]
        income_cats = [c for c in categories if c.get("id") == "income"] or [
            {"id": "income", "name": "Income"},
        ]

        def update_cats() -> None:
            td = type_ref.current
            cd = cat_ref.current
            if not td or not cd:
                return
            is_income = (td.value or "expense") == "income"
            opts = income_cats if is_income else expense_cats
            cd.options = [ft.dropdown.Option(c["id"], c["name"]) for c in opts]
            cd.value = opts[0]["id"] if opts else None
            page.update()

        def on_type_change(_: ft.ControlEvent) -> None:
            update_cats()

        type_dd = ft.Dropdown(
            ref=type_ref,
            label="Transaction type",
            value="expense",
            options=[
                ft.dropdown.Option("expense", "Expense"),
                ft.dropdown.Option("income", "Income"),
            ],
            border_color=ACCENT_LIGHT,
            focused_border_color=ACCENT,
            fill_color=CARD_BG,
            on_select=on_type_change,
        )
        cat_dd = ft.Dropdown(
            ref=cat_ref,
            label="Category",
            border_color=ACCENT_LIGHT,
            focused_border_color=ACCENT,
            fill_color=CARD_BG,
            options=[ft.dropdown.Option(c["id"], c["name"]) for c in expense_cats],
            value=expense_cats[0]["id"] if expense_cats else None,
        )
        amt_tf = ft.TextField(
            ref=amount_ref,
            label="Amount ($)",
            hint_text="0.00",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ACCENT_LIGHT,
            focused_border_color=ACCENT,
            fill_color=CARD_BG,
            autofocus=True,
        )
        note_tf = ft.TextField(
            ref=note_ref,
            label="Note (optional)",
            hint_text="e.g. Groceries",
            border_color=ACCENT_LIGHT,
            focused_border_color=ACCENT,
            fill_color=CARD_BG,
        )

        def submit(_: ft.ControlEvent) -> None:
            a = parse_amount(amount_ref.current.value or "0")
            if a <= 0:
                return
            t = type_ref.current.value or "expense"
            transactions.append({
                "id": str(len(transactions) + 1),
                "type": t,
                "amount": a,
                "category": cat_ref.current.value or "",
                "note": (note_ref.current.value or "").strip() or None,
                "date": datetime.now().strftime("%Y-%m-%d"),
            })
            persist()
            refresh_views()
            go_back(_)

        form = ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=TEXT_PRIMARY,
                            on_click=go_back,
                            tooltip="Back",
                        ),
                        ft.Text("Add transaction", size=20, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=12,
                ),
                glass_card(
                    ft.Column(
                        [type_dd, amt_tf, cat_dd, note_tf],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                    ),
                    padding=20,
                ),
                ft.Row(
                    [
                        ft.OutlinedButton("Cancel", on_click=go_back),
                        ft.Button(
                            "Save",
                            on_click=submit,
                            style=ft.ButtonStyle(bgcolor=ACCENT, color=TEXT_PRIMARY, padding=16),
                        ),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            spacing=24,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        if body_container.current:
            body_container.current.content = form
        page.update()

    def on_nav(e: ft.ControlEvent) -> None:
        idx = e.control.selected_index
        nav_index[0] = idx
        if not body_container.current:
            return
        if idx == 0:
            body_container.current.content = build_dashboard()
        elif idx == 1:
            body_container.current.content = build_history()
        else:
            body_container.current.content = build_goals()
        page.update()

    # Single body: dashboard only at startup (lazy-build History/Goals on first nav)
    body = ft.Container(
        ref=body_container,
        content=build_dashboard(),
        expand=True,
    )

    nav = ft.NavigationBar(
        ref=nav_bar,
        selected_index=0,
        on_change=on_nav,
        destinations=[
            ft.NavigationBarDestination(icon="dashboard_outlined", selected_icon="dashboard", label="Dashboard"),
            ft.NavigationBarDestination(icon="history_outlined", selected_icon="history", label="History"),
            ft.NavigationBarDestination(icon="flag_outlined", selected_icon="flag", label="Goals"),
        ],
        bgcolor=CARD_BG,
        elevation=0,
    )

    layout = ft.Container(
        gradient=BG_GRADIENT,
        expand=True,
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("BudgetWise", size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                    ft.IconButton(
                                        icon=ft.Icons.ADD_CIRCLE,
                                        icon_color=ACCENT,
                                        icon_size=32,
                                        on_click=open_add,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Container(content=body, expand=True),
                        ],
                        expand=True,
                    ),
                    padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                    expand=True,
                ),
                nav,
            ],
            expand=True,
        ),
    )
    page.add(layout)
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "0xff0f0c29"
    page.update()


if __name__ == "__main__":
    try:
        ft.run(main)
    except Exception:
        ft.app(target=main)  # fallback for older Flet
