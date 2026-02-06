# Team Project Management Application (TeamFlow)

A modern-looking **Team Project Management** desktop application built with Python + CustomTkinter.

## What you can do

- Create and manage **Projects**
- Create and manage **Tasks** (status, priority, assignee, due date)
- Manage **Team Members**
- View a **Dashboard** with quick stats and upcoming tasks
- Data is saved locally to a JSON file (auto-saved)

## Requirements

- Python 3.9+ recommended

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

From this folder:

```bash
python app.py
```

## Data storage

- App data is stored locally at `data/teamflow.json`
- If the file is missing, the app will create it with sample data.

