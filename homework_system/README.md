# Online Homework Submission and Grading System

A modern, web-based homework submission and grading system built with Flask. This system allows teachers to create assignments and grade student submissions, while students can submit their homework and view their grades.

## Features

### For Students:
- Register and login to the system
- View all available assignments
- Submit homework assignments with file uploads
- View grades and feedback from teachers
- Track submission status and deadlines

### For Teachers:
- Create assignments with descriptions, due dates, and point values
- Upload assignment files (PDF, DOC, DOCX, TXT)
- View all student submissions for each assignment
- Grade submissions with points and feedback
- Track assignment statistics

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your web browser and navigate to `http://localhost:5000`

## Usage

### First Time Setup

1. **Register an account:**
   - Click "Register" on the homepage
   - Choose your role (Student or Teacher)
   - Fill in your username, email, and password

2. **Login:**
   - Use your credentials to login

### For Teachers

1. **Create an Assignment:**
   - Click "Create Assignment" on your dashboard
   - Fill in the assignment details:
     - Title
     - Description
     - Due date and time
     - Maximum points
     - Optional: Upload an assignment file
   - Click "Create Assignment"

2. **View Submissions:**
   - Click "Submissions" on any assignment card
   - View all student submissions
   - Download submission files
   - Grade each submission with points and feedback

### For Students

1. **View Assignments:**
   - All available assignments are shown on your dashboard
   - Color-coded status indicators:
     - Green: Submitted
     - Red: Overdue
     - Yellow: Pending

2. **Submit Homework:**
   - Click "View Details" on an assignment
   - Upload your work file (PDF, DOC, DOCX, TXT, ZIP, RAR)
   - Click "Submit Assignment"

3. **View Grades:**
   - Grades appear on assignment cards once graded
   - View detailed feedback on the assignment page

## File Structure

```
homework_system/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── teacher_dashboard.html
│   ├── student_dashboard.html
│   ├── create_assignment.html
│   ├── view_assignment.html
│   └── view_submissions.html
├── static/               # Static files
│   └── css/
│       └── style.css
└── uploads/              # Uploaded files (created automatically)
    ├── assignments/
    └── submissions/
```

## Technical Details

- **Framework:** Flask 3.0.0
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** Bootstrap 5.3.0 with custom CSS
- **Icons:** Bootstrap Icons
- **File Upload:** Supports PDF, DOC, DOCX, TXT, ZIP, RAR (max 16MB)

## Security Notes

⚠️ **Important:** This is a development application. For production use, you should:

1. Change the `SECRET_KEY` in `app.py` to a secure random value
2. Use a production-grade database (PostgreSQL, MySQL)
3. Implement proper file validation and virus scanning
4. Add rate limiting and CSRF protection
5. Use HTTPS
6. Implement proper session management
7. Add input validation and sanitization

## Database Schema

- **User:** Stores user accounts (username, email, password hash, role)
- **Assignment:** Stores assignment details (title, description, due date, max points, file path)
- **Submission:** Stores student submissions (assignment ID, student ID, file path, submission time)
- **Grade:** Stores grades and feedback (submission ID, points, feedback, grading time)

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please check the code comments or create an issue in the repository.
