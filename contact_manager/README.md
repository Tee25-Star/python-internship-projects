# Contact Management Application (Address Book / CRM Lite)

This is a **desktop contact management application** built with Python and `customtkinter`.  
It provides a **modern, visually polished UI** with support for:

- **Add / Edit / Delete** contacts
- **Search and filter** contacts by name, company, or tags
- **Persistent storage** using a local SQLite database
- Clean dark theme and responsive layout

---

## 1. Requirements

Make sure you have **Python 3.9+** installed.

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 2. Running the Application

From the project directory:

```bash
python main.py
```

This will open the Contact Manager window.

---

## 3. Features Overview

- **Contact Fields**
  - Full Name
  - Company
  - Email
  - Phone
  - Address (multi-line)
  - Tags (comma-separated)
  - Notes (multi-line)

- **Contact List Panel**
  - Scrollable list of contacts
  - Each row shows name, company, and primary phone
  - Click a contact to load it into the detail form

- **Actions**
  - **New**: Clear the form to create a new contact
  - **Save**: Create or update the currently selected contact
  - **Delete**: Remove the selected contact (with confirmation)
  - **Search**: Live filter by name, company, or tags

---

## 4. Data Storage

- All contacts are stored in a local **SQLite** database file named `contacts.db` (created automatically on first run).
- The database file is kept in the same directory as `main.py`.

---

## 5. Notes

- The UI uses **customtkinter** for a modern, dark-mode friendly look and feel.
- You can adjust global appearance (light/dark/system) or scaling directly in the code if desired.

