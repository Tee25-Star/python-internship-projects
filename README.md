# Online Quiz/Examination System

A beautiful, modern, and interactive online quiz system built with Python Flask. Features a stunning user interface with smooth animations, real-time timer, progress tracking, and detailed results.

## Features

✨ **Beautiful Modern UI**
- Gradient backgrounds and smooth animations
- Responsive design that works on all devices
- Interactive elements with hover effects
- Clean and intuitive user interface

📊 **Quiz Features**
- Multiple choice questions
- Configurable time limits (15, 30, 45, or 60 minutes)
- Real-time timer with visual warnings
- Progress tracking
- Question navigation (Previous/Next)
- Automatic quiz submission when time expires

📈 **Results & Analytics**
- Instant score calculation
- Percentage-based scoring
- Detailed results for each question
- Visual score representation with animated progress circle
- Shows correct/incorrect answers
- Points earned per question

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server:**
   ```bash
   python quiz_app.py
   ```

2. **Open your web browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Usage

1. **Start a Quiz:**
   - Enter your name
   - Select a time limit
   - Click "Start Quiz"

2. **Take the Quiz:**
   - Read each question carefully
   - Select your answer by clicking on an option
   - Use "Previous" and "Next" buttons to navigate
   - Monitor your time using the timer
   - Click "Submit Quiz" when finished

3. **View Results:**
   - See your overall score and percentage
   - Review detailed results for each question
   - Check which answers were correct/incorrect
   - View points earned per question

## Project Structure

```
quiz-system/
├── quiz_app.py          # Main Flask application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── templates/          # HTML templates
│   ├── index.html      # Home page
│   ├── quiz.html       # Quiz interface
│   └── results.html    # Results page
└── static/            # Static files
    ├── style.css      # Styling and animations
    ├── script.js      # Home page JavaScript
    ├── quiz.js        # Quiz functionality
    └── results.js     # Results display
```

## Customization

### Adding More Questions

Edit the `QUIZ_QUESTIONS` list in `quiz_app.py`:

```python
{
    "id": 11,
    "question": "Your question here?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct": 0,  # Index of correct answer (0-3)
    "points": 10
}
```

### Changing Time Limits

Modify the time limit options in `templates/index.html`:

```html
<option value="20">20 minutes</option>
```

### Styling

Customize colors and styles in `static/style.css` by modifying the CSS variables:

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    /* ... */
}
```

## Technologies Used

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Styling:** Custom CSS with gradients and animations
- **Architecture:** RESTful API design

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Future Enhancements

- Database integration for storing questions and results
- User authentication and accounts
- Multiple quiz categories
- Question randomization
- Export results as PDF
- Admin panel for question management

## License

This project is open source and available for educational purposes.

## Author

Created with ❤️ for interactive learning and assessment.

---

**Enjoy taking quizzes!** 🎓✨
