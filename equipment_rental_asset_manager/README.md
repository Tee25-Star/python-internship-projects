# Equipment Rental / Asset Management System (Python)

A modern **desktop** equipment rental + asset management app built with **Python + PySide6 (Qt)** and a local **SQLite** database.

## Features

- **Dashboard** with KPI cards (Total assets, Available, Rented, Overdue)
- **Assets**: add/edit/delete, search, status tracking (Available / Rented / Maintenance)
- **Customers**: add/edit/delete, quick search
- **Rentals**: create rental, return rental, automatic overdue detection, "due soon" list
- **Stunning UI**: dark glassy theme, gradient accents, soft shadows, rounded cards

## Requirements

- Python 3.10+ recommended

## Install

From this folder:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Data storage

The app stores data in:

- `data/app.sqlite3`

On first run, it seeds a small set of sample assets/customers so you can explore the UI immediately.

