"""
Simple CRM for Small Businesses
Flask + SQLite — contacts, companies, and deals.
"""
import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "crm-dev-secret-change-in-production")
DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                industry TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                role TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                title TEXT NOT NULL,
                value REAL DEFAULT 0,
                stage TEXT DEFAULT 'lead',
                expected_close DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts(id)
            );
        """)


# ---------- Companies ----------
@app.route("/")
def index():
    with get_db() as conn:
        stats = conn.execute(
            "SELECT (SELECT COUNT(*) FROM contacts) AS contacts, "
            "(SELECT COUNT(*) FROM companies) AS companies, "
            "(SELECT COUNT(*) FROM deals) AS deals, "
            "(SELECT COALESCE(SUM(value), 0) FROM deals WHERE stage = 'won') AS pipeline"
        ).fetchone()
        recent = conn.execute(
            "SELECT c.id, c.name, c.email, c.phone, co.name AS company_name "
            "FROM contacts c LEFT JOIN companies co ON c.company_id = co.id "
            "ORDER BY c.created_at DESC LIMIT 8"
        ).fetchall()
    return render_template("index.html", stats=stats, recent=recent)


@app.route("/companies")
def companies_list():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT c.*, (SELECT COUNT(*) FROM contacts WHERE company_id = c.id) AS contact_count "
            "FROM companies c ORDER BY c.name"
        ).fetchall()
    return render_template("companies.html", companies=rows)


@app.route("/companies/add", methods=["GET", "POST"])
def company_add():
    if request.method == "POST":
        with get_db() as conn:
            conn.execute(
                "INSERT INTO companies (name, industry, phone, email, address) VALUES (?, ?, ?, ?, ?)",
                (
                    request.form.get("name", "").strip(),
                    request.form.get("industry", "").strip(),
                    request.form.get("phone", "").strip(),
                    request.form.get("email", "").strip(),
                    request.form.get("address", "").strip(),
                ),
            )
        flash("Company added successfully.", "success")
        return redirect(url_for("companies_list"))
    return render_template("company_form.html", company=None)


@app.route("/companies/<int:id>/edit", methods=["GET", "POST"])
def company_edit(id):
    with get_db() as conn:
        company = conn.execute("SELECT * FROM companies WHERE id = ?", (id,)).fetchone()
    if not company:
        flash("Company not found.", "error")
        return redirect(url_for("companies_list"))
    if request.method == "POST":
        with get_db() as conn:
            conn.execute(
                "UPDATE companies SET name=?, industry=?, phone=?, email=?, address=? WHERE id=?",
                (
                    request.form.get("name", "").strip(),
                    request.form.get("industry", "").strip(),
                    request.form.get("phone", "").strip(),
                    request.form.get("email", "").strip(),
                    request.form.get("address", "").strip(),
                    id,
                ),
            )
        flash("Company updated.", "success")
        return redirect(url_for("companies_list"))
    return render_template("company_form.html", company=company)


@app.route("/companies/<int:id>/delete", methods=["POST"])
def company_delete(id):
    with get_db() as conn:
        conn.execute("DELETE FROM companies WHERE id = ?", (id,))
    flash("Company deleted.", "success")
    return redirect(url_for("companies_list"))


# ---------- Contacts ----------
@app.route("/contacts")
def contacts_list():
    q = request.args.get("q", "").strip()
    with get_db() as conn:
        if q:
            rows = conn.execute(
                "SELECT c.*, co.name AS company_name FROM contacts c "
                "LEFT JOIN companies co ON c.company_id = co.id "
                "WHERE c.name LIKE ? OR c.email LIKE ? OR co.name LIKE ? "
                "ORDER BY c.name",
                (f"%{q}%", f"%{q}%", f"%{q}%"),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT c.*, co.name AS company_name FROM contacts c "
                "LEFT JOIN companies co ON c.company_id = co.id ORDER BY c.name"
            ).fetchall()
    return render_template("contacts.html", contacts=rows, search=q)


@app.route("/contacts/add", methods=["GET", "POST"])
def contact_add():
    with get_db() as conn:
        companies = conn.execute("SELECT id, name FROM companies ORDER BY name").fetchall()
    if request.method == "POST":
        company_id = request.form.get("company_id") or None
        if company_id:
            company_id = int(company_id)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO contacts (company_id, name, email, phone, role, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    company_id,
                    request.form.get("name", "").strip(),
                    request.form.get("email", "").strip(),
                    request.form.get("phone", "").strip(),
                    request.form.get("role", "").strip(),
                    request.form.get("notes", "").strip(),
                ),
            )
        flash("Contact added.", "success")
        return redirect(url_for("contacts_list"))
    return render_template("contact_form.html", contact=None, companies=companies)


@app.route("/contacts/<int:id>/edit", methods=["GET", "POST"])
def contact_edit(id):
    with get_db() as conn:
        contact = conn.execute(
            "SELECT c.*, co.name AS company_name FROM contacts c "
            "LEFT JOIN companies co ON c.company_id = co.id WHERE c.id = ?",
            (id,),
        ).fetchone()
        companies = conn.execute("SELECT id, name FROM companies ORDER BY name").fetchall()
    if not contact:
        flash("Contact not found.", "error")
        return redirect(url_for("contacts_list"))
    if request.method == "POST":
        company_id = request.form.get("company_id") or None
        if company_id:
            company_id = int(company_id)
        with get_db() as conn:
            conn.execute(
                "UPDATE contacts SET company_id=?, name=?, email=?, phone=?, role=?, notes=? WHERE id=?",
                (
                    company_id,
                    request.form.get("name", "").strip(),
                    request.form.get("email", "").strip(),
                    request.form.get("phone", "").strip(),
                    request.form.get("role", "").strip(),
                    request.form.get("notes", "").strip(),
                    id,
                ),
            )
        flash("Contact updated.", "success")
        return redirect(url_for("contacts_list"))
    return render_template("contact_form.html", contact=contact, companies=companies)


@app.route("/contacts/<int:id>/delete", methods=["POST"])
def contact_delete(id):
    with get_db() as conn:
        conn.execute("DELETE FROM contacts WHERE id = ?", (id,))
    flash("Contact deleted.", "success")
    return redirect(url_for("contacts_list"))


# ---------- Deals ----------
@app.route("/deals")
def deals_list():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT d.*, c.name AS contact_name, co.name AS company_name "
            "FROM deals d LEFT JOIN contacts c ON d.contact_id = c.id "
            "LEFT JOIN companies co ON c.company_id = co.id ORDER BY d.created_at DESC"
        ).fetchall()
    return render_template("deals.html", deals=rows)


@app.route("/deals/add", methods=["GET", "POST"])
def deal_add():
    with get_db() as conn:
        contacts = conn.execute(
            "SELECT c.id, c.name, co.name AS company_name FROM contacts c "
            "LEFT JOIN companies co ON c.company_id = co.id ORDER BY c.name"
        ).fetchall()
    if request.method == "POST":
        contact_id = request.form.get("contact_id") or None
        if contact_id:
            contact_id = int(contact_id)
        value = request.form.get("value") or 0
        try:
            value = float(value)
        except ValueError:
            value = 0
        expected = request.form.get("expected_close") or None
        with get_db() as conn:
            conn.execute(
                "INSERT INTO deals (contact_id, title, value, stage, expected_close, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    contact_id,
                    request.form.get("title", "").strip(),
                    value,
                    request.form.get("stage", "lead"),
                    expected,
                    request.form.get("notes", "").strip(),
                ),
            )
        flash("Deal added.", "success")
        return redirect(url_for("deals_list"))
    return render_template("deal_form.html", deal=None, contacts=contacts)


@app.route("/deals/<int:id>/edit", methods=["GET", "POST"])
def deal_edit(id):
    with get_db() as conn:
        deal = conn.execute(
            "SELECT d.*, c.name AS contact_name FROM deals d "
            "LEFT JOIN contacts c ON d.contact_id = c.id WHERE d.id = ?",
            (id,),
        ).fetchone()
        contacts = conn.execute(
            "SELECT c.id, c.name, co.name AS company_name FROM contacts c "
            "LEFT JOIN companies co ON c.company_id = co.id ORDER BY c.name"
        ).fetchall()
    if not deal:
        flash("Deal not found.", "error")
        return redirect(url_for("deals_list"))
    if request.method == "POST":
        contact_id = request.form.get("contact_id") or None
        if contact_id:
            contact_id = int(contact_id)
        value = request.form.get("value") or 0
        try:
            value = float(value)
        except ValueError:
            value = 0
        expected = request.form.get("expected_close") or None
        with get_db() as conn:
            conn.execute(
                "UPDATE deals SET contact_id=?, title=?, value=?, stage=?, expected_close=?, notes=? WHERE id=?",
                (
                    contact_id,
                    request.form.get("title", "").strip(),
                    value,
                    request.form.get("stage", "lead"),
                    expected,
                    request.form.get("notes", "").strip(),
                    id,
                ),
            )
        flash("Deal updated.", "success")
        return redirect(url_for("deals_list"))
    return render_template("deal_form.html", deal=deal, contacts=contacts)


@app.route("/deals/<int:id>/delete", methods=["POST"])
def deal_delete(id):
    with get_db() as conn:
        conn.execute("DELETE FROM deals WHERE id = ?", (id,))
    flash("Deal deleted.", "success")
    return redirect(url_for("deals_list"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
