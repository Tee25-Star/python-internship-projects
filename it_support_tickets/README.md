# IT Support Ticketing System

A modern desktop application for managing IT support tickets with a distinctive cyberpunk-inspired interface.

## Features

- **Create tickets** — Add new support requests with title, description, category, priority, and requester
- **Dashboard** — Real-time stats for total, open, in-progress, and resolved tickets
- **Search & filter** — Find tickets by keyword or filter by status
- **Ticket details** — View full ticket information and update status
- **Persistent storage** — Data saved automatically to `tickets.json`

## Interface Highlights

- Dark theme with electric cyan and amber accents
- Card-based layout with priority-colored indicators
- Status badges (Open, In Progress, Resolved, Closed)
- Hover effects and smooth interactions

## Requirements

- Python 3.10+
- customtkinter
- Pillow

## Installation

```bash
cd it_support_tickets
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Usage

1. Click **＋ New Ticket** to create a support request
2. Fill in the form (title, requester, category, priority, description)
3. Click a ticket in the list to view details
4. Use the status buttons to update ticket progress
5. Use the search bar to find specific tickets
6. Use the filter dropdown to show tickets by status
