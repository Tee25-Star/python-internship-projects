# Simple CRM for Small Businesses

A lightweight Customer Relationship Management system built with Python and Flask. Manage **contacts**, **companies**, and **deals** with a distinctive dark-themed interface.

## Features

- **Dashboard** — Overview with contact/company/deal counts and won pipeline value
- **Contacts** — Add, edit, delete, and search contacts; link to companies
- **Companies** — Manage organizations with industry, contact info, and address
- **Deals** — Track opportunities with stages: Lead → Qualified → Proposal → Negotiation → Won/Lost

Data is stored in a local SQLite database (`crm.db`), created automatically on first run.

## Setup and run

1. **Create a virtual environment (recommended):**
   ```bash
   cd simple_crm
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the app:**
   ```bash
   python app.py
   ```

4. Open **http://127.0.0.1:5000** in your browser.

## Project structure

```
simple_crm/
├── app.py              # Flask app and routes
├── requirements.txt
├── crm.db              # SQLite DB (created on first run)
├── static/
│   └── style.css       # Standout UI styles
├── templates/          # Jinja2 HTML templates
└── README.md
```

## Tech stack

- **Backend:** Flask 3, SQLite
- **Frontend:** HTML, CSS (Outfit + JetBrains Mono), no JavaScript framework
