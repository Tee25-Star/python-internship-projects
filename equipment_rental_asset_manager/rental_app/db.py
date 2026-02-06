from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "app.sqlite3"


@dataclass(frozen=True)
class DbPaths:
    root_dir: Path
    data_dir: Path
    db_path: Path


def get_paths() -> DbPaths:
    return DbPaths(root_dir=ROOT_DIR, data_dir=DATA_DIR, db_path=DB_PATH)


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def init_db(seed: bool = True) -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS assets (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              tag TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL,
              category TEXT NOT NULL,
              daily_rate REAL NOT NULL DEFAULT 0,
              status TEXT NOT NULL DEFAULT 'available',
              condition TEXT NOT NULL DEFAULT 'good',
              notes TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS customers (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              company TEXT NOT NULL DEFAULT '',
              email TEXT NOT NULL DEFAULT '',
              phone TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rentals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              asset_id INTEGER NOT NULL,
              customer_id INTEGER NOT NULL,
              start_date TEXT NOT NULL,
              due_date TEXT NOT NULL,
              return_date TEXT,
              daily_rate REAL NOT NULL,
              deposit REAL NOT NULL DEFAULT 0,
              notes TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL,
              FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE RESTRICT,
              FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE RESTRICT
            );

            CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
            CREATE INDEX IF NOT EXISTS idx_rentals_asset ON rentals(asset_id);
            CREATE INDEX IF NOT EXISTS idx_rentals_customer ON rentals(customer_id);
            CREATE INDEX IF NOT EXISTS idx_rentals_due ON rentals(due_date);
            """
        )

        if seed:
            _seed_if_empty(conn)


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    asset_count = conn.execute("SELECT COUNT(*) AS c FROM assets").fetchone()["c"]
    customer_count = conn.execute("SELECT COUNT(*) AS c FROM customers").fetchone()["c"]

    today = date.today().isoformat()

    if asset_count == 0:
        assets: Iterable[tuple[str, str, str, float, str, str, str, str]] = [
            ("CAM-001", "Sony FX3 Cinema Camera", "Cameras", 120.0, "available", "excellent", "Full-frame; includes cage + batteries", today),
            ("LGT-014", "Aputure 300D II Key Light", "Lighting", 45.0, "available", "good", "Bowens mount; includes softbox", today),
            ("AUD-003", "RØDE Wireless GO II", "Audio", 25.0, "available", "excellent", "2 TX + 1 RX kit", today),
            ("DRN-020", "DJI Air 3 Drone", "Drones", 160.0, "maintenance", "fair", "Propellers replaced; calibration due", today),
            ("TRI-009", "Manfrotto Tripod 190X", "Support", 12.0, "available", "good", "Quick-release plate included", today),
        ]
        conn.executemany(
            """
            INSERT INTO assets (tag, name, category, daily_rate, status, condition, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            list(assets),
        )

    if customer_count == 0:
        customers: Iterable[tuple[str, str, str, str, str]] = [
            ("Nina Patel", "Northwind Studio", "nina@northwind.studio", "+1 555 0101", today),
            ("Oluwaseun Adeyemi", "Apex Media", "seun@apexmedia.com", "+1 555 0137", today),
            ("Jamie Chen", "", "jamie.chen@email.com", "+1 555 0199", today),
        ]
        conn.executemany(
            """
            INSERT INTO customers (name, company, email, phone, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            list(customers),
        )


def get_connection() -> sqlite3.Connection:
    """
    Public connection factory. Keep connections short-lived and use context managers.
    """
    return _connect()

