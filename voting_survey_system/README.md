# 🗳️ Voting & Survey System

A beautiful, modern Python application for creating and managing polls and surveys with real-time results visualization.

## Features

- **Voting System**: Create polls with multiple options and track votes in real-time
- **Survey System**: Create comprehensive surveys with multiple question types:
  - Multiple Choice questions
  - Text-based questions
  - Rating questions (1-5 scale)
- **Results & Analytics**: Visualize poll results with bar charts and view survey response summaries
- **Data Persistence**: All polls, surveys, and responses are automatically saved to JSON files
- **Modern UI**: Beautiful dark-themed interface built with CustomTkinter

## Installation

1. Make sure you have Python 3.8 or higher installed

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python voting_survey_app.py
```

### Creating a Poll

1. Navigate to the "🗳️ Voting" tab
2. Enter your poll question
3. Add at least 2 options
4. Click "Create Poll"
5. Vote on active polls by clicking the "Vote" button next to your preferred option

### Creating a Survey

1. Navigate to the "📊 Surveys" tab
2. Enter a survey title
3. Click "+ Add Question" to add questions
4. Select question type for each question:
   - **Multiple Choice**: Radio button selection
   - **Text**: Free-form text response
   - **Rating (1-5)**: 1-5 scale rating
5. Click "Create Survey"
6. Take surveys by clicking "Take Survey" on any active survey

### Viewing Results

1. Navigate to the "📈 Results" tab
2. View poll results with interactive bar charts showing vote counts and percentages
3. View survey response summaries including:
   - Total response count
   - Average ratings for rating questions
   - Sample responses for text and multiple choice questions

## Data Storage

The application automatically saves data to three JSON files:
- `votes.json`: All poll data and vote counts
- `surveys.json`: All survey definitions
- `survey_responses.json`: All survey responses

## Requirements

- Python 3.8+
- customtkinter >= 5.2.0
- matplotlib >= 3.7.0
- numpy >= 1.24.0

## Screenshots

The application features:
- Dark theme with modern color scheme
- Smooth animations and transitions
- Responsive layout
- Interactive charts and visualizations
- Clean, intuitive interface

Enjoy creating polls and surveys! 🎉
