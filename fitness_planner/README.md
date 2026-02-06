# Fitness Training Planner (Python)

A modern desktop **fitness planner** built with Python and `customtkinter`.  
It includes preset training plans, daily workout details, and progress tracking in a standout dark UI.

All app files now live inside the `fitness_planner` folder.

## Features

- **Beautiful dark UI** with accent colors and card-style layout.
- **Built-in training plans** (beginner, intermediate, advanced).
- **Day-by-day breakdown** with exercises, sets, and notes.
- **Progress tracking** per plan (stored locally in `progress.json` in this folder).

## Requirements

- Python 3.9+ (recommended)
- Pip

Install dependencies (from inside `fitness_planner`):

```bash
cd fitness_planner
pip install -r requirements.txt
```

## Run the app

Still inside the `fitness_planner` folder:

```bash
python fitness_app.py
```

The app will open a window with:

- A sidebar showing the app title and filters.
- A plan list you can click to select.
- A main area showing plan summary, days, and detailed exercises.

