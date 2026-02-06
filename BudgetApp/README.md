# BudgetWise - Personal Budget Management

A visually stunning, mobile-first Python application for personal budget management. Built with **Flet** for cross-platform deployment (iOS, Android, Windows, Web).

## Features

- **Dashboard** ù Overview of income, expenses, and balance with category breakdown
- **Transactions** ù Add income & expenses with categories and notes
- **Categories** ù Predefined spending categories (Food, Transport, Shopping, etc.)
- **Budget Goals** ù Track spending vs. monthly limits per category
- **History** ù Filterable transaction list by month
- **Persistent Storage** ù Data saved locally (JSON)

## Design

- Gradient backgrounds and glassmorphism-style cards
- Dark theme with teal (income) / coral (expense) accents
- Mobile-optimized layout with bottom navigation
- Progress bars for spending by category and budget goals

## Run the App

```bash
cd PycharmProjects/BudgetApp
pip install -r requirements.txt
python main.py
```

If `flet` is on your PATH, you can also use:

```bash
flet run main.py
```

### Test on Your Phone

1. Install **Flet** app from [App Store](https://apps.apple.com/app/flet/id6475885963) or [Google Play](https://play.google.com/store/apps/details?id=dev.flet.flet)
2. Run `python main.py` or `flet run main.py` on your computer
3. Scan the QR code with the Flet app

### Build for Mobile

```bash
flet build apk     # Android
flet build ios     # iOS (macOS only)
```

## Documentation

`BudgetWise_Documentation.docx` contains requirements analysis, system architecture, MVP implementation, testing, documentation, and final presentation. To regenerate:

```bash
pip install python-docx
python create_documentation.py
```

## Requirements

- Python 3.10+
- Flet 0.25+
