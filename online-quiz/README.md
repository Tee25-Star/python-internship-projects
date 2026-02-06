# Online Quiz/Examination System

A beautiful, modern web-based quiz application built with Python Flask. Features a stunning dark-themed interface with smooth animations, real-time timer, progress tracking, and detailed results.

## Features

- 🎨 **Visually Stunning Interface**: Modern dark theme with gradient accents and smooth animations
- ⏱️ **Timer Functionality**: Real-time countdown timer with visual progress indicator
- 📊 **Progress Tracking**: Visual progress bar and question navigation dots
- ✅ **Instant Results**: Detailed score breakdown with question-by-question review
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- 🎯 **Multiple Choice Questions**: Easy-to-use option selection with visual feedback

## Installation

1. **Install Python** (3.7 or higher)

2. **Install dependencies**:
   ```bash
   cd online-quiz
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server** (from the `online-quiz` folder):
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Welcome Screen**: View quiz information and click "Start Quiz"
2. **Take Quiz**: 
   - Select answers by clicking on options
   - Navigate between questions using Previous/Next buttons or question dots
   - Monitor your time with the circular timer
   - Watch your progress with the progress bar
3. **Submit**: Click "Submit Quiz" when finished
4. **View Results**: See your score, time taken, and detailed question review

## Customization

### Adding Your Own Questions

Edit the `QUIZ_DATA` dictionary in `app.py`:

```python
QUIZ_DATA = {
    "quiz_name": "Your Quiz Name",
    "duration_minutes": 15,
    "questions": [
        {
            "id": 1,
            "question": "Your question here?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct": 0  # Index of correct answer (0-3)
        },
        # Add more questions...
    ]
}
```

### Styling

Modify `static/style.css` to customize colors, fonts, and layout. The CSS uses CSS variables for easy theming:

```css
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --dark-bg: #1a1a2e;
    /* ... more variables */
}
```

## Project Structure

```
online-quiz/
├── app.py              # Flask backend application
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── templates/
│   ├── index.html      # Welcome page
│   └── quiz.html       # Quiz interface
└── static/
    └── style.css       # Styling and animations
```

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with gradients and animations
- **Fonts**: Google Fonts (Poppins)

## License

This project is open source and available for educational purposes.

## Future Enhancements

- User authentication
- Database integration for storing questions and results
- Multiple quiz categories
- Leaderboard functionality
- Question randomization
- Export results to PDF
