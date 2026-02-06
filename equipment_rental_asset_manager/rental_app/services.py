from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Iterable

from .db import get_connection


def _now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def _to_iso(d: date) -> str:
    return d.isoformat()


def _parse_iso(s: str) -> date:
    return date.fromisoformat(s)


@dataclass(frozen=True)
class Kpis:
    total_assets: int
    available_assets: int
    rented_assets: int
    maintenance_assets: int
    active_rentals: int
    overdue_rentals: int


def compute_kpis() -> Kpis:
    today = date.today()
    with get_connection() as conn:
        total_assets = conn.execute("SELECT COUNT(*) AS c FROM assets").fetchone()["c"]
        available_assets = conn.execute("SELECT COUNT(*) AS c FROM assets WHERE status='available'").fetchone()["c"]
        rented_assets = conn.execute("SELECT COUNT(*) AS c FROM assets WHERE status='rented'").fetchone()["c"]
        maintenance_assets = conn.execute("SELECT COUNT(*) AS c FROM assets WHERE status='maintenance'").fetchone()["c"]
        active_rentals = conn.execute("SELECT COUNT(*) AS c FROM rentals WHERE return_date IS NULL").fetchone()["c"]
        overdue_rentals = conn.execute(
            "SELECT COUNT(*) AS c FROM rentals WHERE return_date IS NULL AND due_date < ?",
            (_to_iso(today),),
        ).fetchone()["c"]
        return Kpis(
            total_assets=total_assets,
            available_assets=available_assets,
            rented_assets=rented_assets,
            maintenance_assets=maintenance_assets,
            active_rentals=active_rentals,
            overdue_rentals=overdue_rentals,
        )


# -----------------------------
# Assets
# -----------------------------


def list_assets(search: str = "") -> list[sqlite3.Row]:
    q = """
    SELECT id, tag, name, category, daily_rate, status, condition, notes
    FROM assets
    WHERE (? = '' OR tag LIKE ? OR name LIKE ? OR category LIKE ?)
    ORDER BY tag ASC
    """
    s = search.strip()
    like = f"%{s}%"
    with get_connection() as conn:
        return list(conn.execute(q, (s, like, like, like)).fetchall())


def create_asset(*, tag: str, name: str, category: str, daily_rate: float, status: str, condition: str, notes: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO assets (tag, name, category, daily_rate, status, condition, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tag.strip(), name.strip(), category.strip(), float(daily_rate), status, condition, notes.strip(), _now_iso()),
        )


def update_asset(
    *,
    asset_id: int,
    tag: str,
    name: str,
    category: str,
    daily_rate: float,
    status: str,
    condition: str,
    notes: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE assets
            SET tag=?, name=?, category=?, daily_rate=?, status=?, condition=?, notes=?
            WHERE id=?
            """,
            (tag.strip(), name.strip(), category.strip(), float(daily_rate), status, condition, notes.strip(), int(asset_id)),
        )


def delete_asset(asset_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM assets WHERE id=?", (int(asset_id),))


def list_available_assets() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return list(
            conn.execute(
                "SELECT id, tag, name, category, daily_rate FROM assets WHERE status='available' ORDER BY tag ASC"
            ).fetchall()
        )


def get_asset(asset_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, tag, name, category, daily_rate, status, condition, notes FROM assets WHERE id=?",
            (int(asset_id),),
        ).fetchone()


# -----------------------------
# Customers
# -----------------------------


def list_customers(search: str = "") -> list[sqlite3.Row]:
    q = """
    SELECT id, name, company, email, phone
    FROM customers
    WHERE (? = '' OR name LIKE ? OR company LIKE ? OR email LIKE ? OR phone LIKE ?)
    ORDER BY name ASC
    """
    s = search.strip()
    like = f"%{s}%"
    with get_connection() as conn:
        return list(conn.execute(q, (s, like, like, like, like)).fetchall())


def create_customer(*, name: str, company: str, email: str, phone: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO customers (name, company, email, phone, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name.strip(), company.strip(), email.strip(), phone.strip(), _now_iso()),
        )


def update_customer(*, customer_id: int, name: str, company: str, email: str, phone: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE customers
            SET name=?, company=?, email=?, phone=?
            WHERE id=?
            """,
            (name.strip(), company.strip(), email.strip(), phone.strip(), int(customer_id)),
        )


def delete_customer(customer_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM customers WHERE id=?", (int(customer_id),))


def list_customer_choices() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return list(conn.execute("SELECT id, name, company FROM customers ORDER BY name ASC").fetchall())


# -----------------------------
# Rentals
# -----------------------------


def list_rentals(filter_mode: str = "active") -> list[sqlite3.Row]:
    """
    filter_mode: 'active' | 'returned' | 'all'
    """
    where = ""
    params: list[Any] = []
    if filter_mode == "active":
        where = "WHERE r.return_date IS NULL"
    elif filter_mode == "returned":
        where = "WHERE r.return_date IS NOT NULL"
    else:
        where = ""

    q = f"""
    SELECT
      r.id,
      r.start_date,
      r.due_date,
      r.return_date,
      r.daily_rate,
      r.deposit,
      r.notes,
      a.id AS asset_id,
      a.tag AS asset_tag,
      a.name AS asset_name,
      c.id AS customer_id,
      c.name AS customer_name,
      c.company AS customer_company
    FROM rentals r
    JOIN assets a ON a.id = r.asset_id
    JOIN customers c ON c.id = r.customer_id
    {where}
    ORDER BY r.id DESC
    """

    with get_connection() as conn:
        return list(conn.execute(q, params).fetchall())


def create_rental(
    *,
    asset_id: int,
    customer_id: int,
    start_date: date,
    due_date: date,
    daily_rate: float,
    deposit: float,
    notes: str,
) -> None:
    if due_date < start_date:
        raise ValueError("Due date cannot be before start date.")

    with get_connection() as conn:
        asset = conn.execute("SELECT status FROM assets WHERE id=?", (int(asset_id),)).fetchone()
        if not asset:
            raise ValueError("Asset not found.")
        if asset["status"] != "available":
            raise ValueError("Asset is not available.")

        conn.execute(
            """
            INSERT INTO rentals (asset_id, customer_id, start_date, due_date, return_date, daily_rate, deposit, notes, created_at)
            VALUES (?, ?, ?, ?, NULL, ?, ?, ?, ?)
            """,
            (
                int(asset_id),
                int(customer_id),
                _to_iso(start_date),
                _to_iso(due_date),
                float(daily_rate),
                float(deposit),
                notes.strip(),
                _now_iso(),
            ),
        )
        conn.execute("UPDATE assets SET status='rented' WHERE id=?", (int(asset_id),))


def return_rental(*, rental_id: int, return_date: date | None = None) -> None:
    rd = return_date or date.today()

    with get_connection() as conn:
        rental = conn.execute("SELECT asset_id, return_date FROM rentals WHERE id=?", (int(rental_id),)).fetchone()
        if not rental:
            raise ValueError("Rental not found.")
        if rental["return_date"] is not None:
            return

        conn.execute("UPDATE rentals SET return_date=? WHERE id=?", (_to_iso(rd), int(rental_id)))
        conn.execute("UPDATE assets SET status='available' WHERE id=?", (int(rental["asset_id"]),))


def due_soon(limit: int = 8) -> list[sqlite3.Row]:
    today = date.today()
    q = """
    SELECT
      r.id,
      r.due_date,
      a.tag AS asset_tag,
      a.name AS asset_name,
      c.name AS customer_name,
      c.company AS customer_company
    FROM rentals r
    JOIN assets a ON a.id = r.asset_id
    JOIN customers c ON c.id = r.customer_id
    WHERE r.return_date IS NULL
    ORDER BY r.due_date ASC
    LIMIT ?
    """
    with get_connection() as conn:
        rows = list(conn.execute(q, (int(limit),)).fetchall())
    # Move overdue to top (still ordered overall nicely)
    rows.sort(key=lambda r: (_parse_iso(r["due_date"]) >= today, r["due_date"]))
    return rows


def rental_is_overdue(row: sqlite3.Row) -> bool:
    if row["return_date"] is not None:
        return False
    return _parse_iso(row["due_date"]) < date.today()

