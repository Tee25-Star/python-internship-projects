# PulseWatch - Service / Website Availability Monitor

PulseWatch is a small Python + Flask web app that lets you quickly check whether one or more websites are up, along with their HTTP status codes and response times.

## Features

- **Multi?URL checks**: Paste multiple URLs (one per line or comma?separated) and run a single scan.
- **Live results**: Checks are executed on demand; nothing is stored.
- **Visual status dashboard**: Modern, dark, glassmorphism?style UI that clearly shows up/down state and latency.
- **Helpful defaults**: Automatically adds `http://` if you forget the scheme.

## Requirements

- Python 3.9+ recommended
- `pip` available on your system

## Setup & Run

1. **Navigate into the project folder**

   ```bash
   cd "C:\Users\TREASURE.DESKTOP-L3QJAEP\service_monitor_app"
   ```

2. **Create and activate a virtual environment (optional but recommended)**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the web app**

   ```bash
   python app.py
   ```

5. **Open the UI**

   Visit `http://127.0.0.1:5000` in your browser.

## Usage

1. Enter one or more URLs in the text area (you can omit `http://` / `https://` if you like).
2. Click **Run check**.
3. The table will show:
   - **Status** (`Up` / `Down` / `Invalid`)
   - **HTTP Code** (if available)
   - **Response time (ms)**
   - **Details** for any errors

You can use the **Try example URLs** button to quickly test the app.

