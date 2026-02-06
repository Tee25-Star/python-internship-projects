# Data → PDF Report Studio

A desktop Python app with a standout interface for generating polished PDF reports from tabular data.

## Features

- **Modern GUI**: Dark, card-based layout with accent colors and clean typography.
- **CSV import**: Browse for any CSV file and see a live preview of the first rows.
- **Automatic summaries**: Numeric columns get basic statistics (count, min, max, mean) in the PDF.
- **Styled PDF output**: Branded header, overview section, and a striped data table (first 50 rows).

## Requirements

- Python 3.8+ (recommended)
- Dependencies in `requirements.txt`:
  - `reportlab`

Install the dependency with:

```bash
pip install -r requirements.txt
```

## Running the application

From the `pdf_report_app` folder containing `reporting_app.py`, run:

```bash
python reporting_app.py
```

## Using the app

1. **Browse CSV…**  
   Click the button on the left, select a CSV file with a header row.

2. **Preview your data**  
   The main panel shows a scrollable table preview and row count.

3. **Generate PDF Report**  
   Click the button, choose a save location and filename.  
   The app produces a PDF with:
   - Title and timestamp
   - Overview summary
   - Optional numeric column statistics
   - Styled table of the first 50 rows

