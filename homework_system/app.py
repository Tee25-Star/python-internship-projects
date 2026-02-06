from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import db, User, Assignment, Submission, Grade
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///homework_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'submissions'), exist_ok=True)

db.init_app(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Teacher only decorator
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'teacher':
            flash('Access denied. Teacher privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Student only decorator
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'student':
            flash('Access denied. Student privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    now = datetime.now()
    
    if user.role == 'teacher':
        assignments = Assignment.query.filter_by(teacher_id=user.id).order_by(Assignment.due_date.desc()).all()
        return render_template('teacher_dashboard.html', assignments=assignments, user=user, now=now)
    else:
        assignments = Assignment.query.order_by(Assignment.due_date.desc()).all()
        submissions = {sub.assignment_id: sub for sub in Submission.query.filter_by(student_id=user.id).all()}
        # Get grades for all submissions
        submission_ids = [sub.id for sub in submissions.values()]
        grades = {grade.submission_id: grade for grade in Grade.query.filter(Grade.submission_id.in_(submission_ids)).all()}
        # Attach grades to submissions
        for assignment_id, submission in submissions.items():
            if submission.id in grades:
                submission.grade = grades[submission.id]
        return render_template('student_dashboard.html', assignments=assignments, submissions=submissions, user=user, now=now)

@app.route('/assignment/create', methods=['GET', 'POST'])
@teacher_required
def create_assignment():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        max_points = request.form.get('max_points', 100)
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('create_assignment'))
        
        assignment = Assignment(
            title=title,
            description=description,
            due_date=due_date,
            max_points=max_points,
            teacher_id=session['user_id']
        )
        
        # Handle file upload if provided
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'assignments', filename)
                file.save(filepath)
                assignment.file_path = filepath
        
        db.session.add(assignment)
        db.session.commit()
        
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_assignment.html')

@app.route('/assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    user = User.query.get(session['user_id'])
    now = datetime.now()
    
    submission = None
    grade = None
    
    if user.role == 'student':
        submission = Submission.query.filter_by(
            assignment_id=assignment_id,
            student_id=user.id
        ).first()
        
        if submission:
            grade = Grade.query.filter_by(submission_id=submission.id).first()
    
    return render_template('view_assignment.html', assignment=assignment, submission=submission, grade=grade, user=user, now=now)

@app.route('/assignment/<int:assignment_id>/submit', methods=['POST'])
@student_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Check if already submitted
    existing_submission = Submission.query.filter_by(
        assignment_id=assignment_id,
        student_id=session['user_id']
    ).first()
    
    if existing_submission:
        flash('You have already submitted this assignment.', 'warning')
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    
    # Check if past due date
    if datetime.now() > assignment.due_date:
        flash('The due date has passed. Submission not accepted.', 'danger')
        return redirect(url_for('view_assignment', assignment_id=assignment_id))
    
    file_path = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{session['user_id']}_{assignment_id}_{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'submissions', filename)
            file.save(file_path)
    
    submission = Submission(
        assignment_id=assignment_id,
        student_id=session['user_id'],
        file_path=file_path,
        submitted_at=datetime.now()
    )
    
    db.session.add(submission)
    db.session.commit()
    
    flash('Assignment submitted successfully!', 'success')
    return redirect(url_for('view_assignment', assignment_id=assignment_id))

@app.route('/assignment/<int:assignment_id>/submissions')
@teacher_required
def view_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if assignment.teacher_id != session['user_id']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    students = {sub.student_id: User.query.get(sub.student_id) for sub in submissions}
    grades = {grade.submission_id: grade for grade in Grade.query.filter(
        Grade.submission_id.in_([sub.id for sub in submissions])
    ).all()}
    
    return render_template('view_submissions.html', assignment=assignment, submissions=submissions, students=students, grades=grades)

@app.route('/submission/<int:submission_id>/grade', methods=['POST'])
@teacher_required
def grade_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    assignment = Assignment.query.get(submission.assignment_id)
    
    if assignment.teacher_id != session['user_id']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    points = float(request.form.get('points', 0))
    feedback = request.form.get('feedback', '')
    
    if points < 0 or points > assignment.max_points:
        flash('Invalid points. Must be between 0 and {}.'.format(assignment.max_points), 'danger')
        return redirect(url_for('view_submissions', assignment_id=assignment.id))
    
    grade = Grade.query.filter_by(submission_id=submission_id).first()
    
    if grade:
        grade.points = points
        grade.feedback = feedback
        grade.graded_at = datetime.now()
    else:
        grade = Grade(
            submission_id=submission_id,
            points=points,
            feedback=feedback,
            graded_at=datetime.now()
        )
        db.session.add(grade)
    
    db.session.commit()
    flash('Grade submitted successfully!', 'success')
    return redirect(url_for('view_submissions', assignment_id=assignment.id))

@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
