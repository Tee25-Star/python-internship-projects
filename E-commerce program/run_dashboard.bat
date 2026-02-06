@echo off
echo Starting E-Commerce Analytics Dashboard...
echo.
cd /d "%~dp0"
streamlit run app.py
pause
