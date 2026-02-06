# Weather Application (AI‑Enhanced Forecast)

A visually rich desktop weather app built with **PySide6 (Qt)**.

- Real forecasts via **Open‑Meteo** (no API key required)
- **AI‑enhanced temperature forecast**: a tiny local Ridge-style regression trained on recent history and blended with the model forecast
- Modern UI: gradients, glassy cards, animated loading state, and a forecast chart overlay

## Setup (Windows / PowerShell)

```powershell
cd "C:\Users\TREASURE.DESKTOP-L3QJAEP\weather_ai_app"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Notes

- If your PowerShell blocks venv activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

- Data source: Open‑Meteo forecast + geocoding + archive endpoints.
