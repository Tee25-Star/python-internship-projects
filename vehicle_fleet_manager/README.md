# Vehicle Fleet Management Application

This is a **Python-based vehicle fleet management web application** built with **Flask** and **SQLite (via SQLAlchemy)**. It provides a clean, modern dashboard interface for tracking your vehicles.

## Features

- **Dashboard overview**
  - Total vehicles
  - Vehicles by status (Active, In Maintenance, Retired)
- **Vehicle management**
  - Add new vehicles
  - Edit existing vehicles
  - View vehicle details
  - Soft-delete / retire vehicles
- **Filtering & search**
  - Filter by status
  - Quick search by make, model, plate number, or driver

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite (via Flask-SQLAlchemy)
- **Frontend**: HTML5, modern CSS (cards, glassmorphism accents, responsive layout)

## Setup & Installation

1. **Navigate to the project directory**

   ```bash
   cd vehicle_fleet_manager
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python app.py
   ```

5. **Open the app in your browser**

   Go to `http://127.0.0.1:5000` and you’ll see the fleet management dashboard.

## Usage

- Use the **“Add Vehicle”** button on the top right of the dashboard to register a new vehicle.
- Use the **status chips** and **search bar** at the top to quickly filter and find vehicles.
- Click the **three-dot menu** on each vehicle row to **view details, edit, or retire** a vehicle.

## Customization

- You can tweak the color palette and layout in `static/css/styles.css`.
- If you want to change the database schema (add fields like insurance expiry, GPS ID, etc.), update the `Vehicle` model in `app.py` and run once to let SQLAlchemy create/update the SQLite database.

## License

This project is provided as a learning/demo application. Feel free to modify and adapt it for your own needs.

