# How to Run the E-Commerce Dashboard

## Quick Start

### Method 1: Using the Batch File (Windows - Easiest)
1. Double-click `run_dashboard.bat`
2. The dashboard will open automatically in your browser

### Method 2: Using PowerShell Script
1. Right-click `run_dashboard.ps1`
2. Select "Run with PowerShell"
3. The dashboard will open automatically in your browser

### Method 3: Using Command Line
1. Open Command Prompt or PowerShell
2. Navigate to the dashboard folder:
   ```bash
   cd "C:\Users\TREASURE.DESKTOP-L3QJAEP\PycharmProjects\E-commerce program"
   ```
3. Run the command:
   ```bash
   streamlit run app.py
   ```

## About the Warnings

The warnings you see are **normal and harmless**:

1. **"Warning: to view this Streamlit app on a browser..."**
   - This is just informational
   - The app will still work perfectly
   - It's telling you the correct way to run it

2. **"No runtime found, using MemoryCacheStorageManager"**
   - This is a normal Streamlit behavior
   - It means Streamlit is using in-memory caching
   - Your app will work exactly the same

## Troubleshooting

### If the dashboard doesn't open automatically:
- Check the terminal/command prompt for the URL (usually `http://localhost:8501`)
- Copy and paste that URL into your browser

### If you get import errors:
- Make sure `data_generator.py` is in the same folder as `app.py`
- Make sure all dependencies are installed:
  ```bash
  pip install -r requirements.txt
  ```

### If port 8501 is already in use:
- Streamlit will automatically try the next available port (8502, 8503, etc.)
- Check the terminal for the actual URL

## Requirements

Make sure you have installed all dependencies:
```bash
pip install streamlit pandas plotly numpy
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Notes

- The dashboard generates synthetic data automatically
- All visualizations are interactive
- You can filter data using the sidebar
- Data can be exported as CSV

Enjoy your analytics dashboard! ??
