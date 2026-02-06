from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    max_points = db.Column(db.Float, default=100)
    file_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    teacher = db.relationship('User', backref='assignments')
    
    def __repr__(self):
        return f'<Assignment {self.title}>'

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assignment = db.relationship('Assignment', backref='submissions')
    student = db.relationship('User', backref='submissions')
    
    def __repr__(self):
        return f'<Submission {self.id}>'

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False, unique=True)
    points = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    submission = db.relationship('Submission', backref='grade')
    
    def __repr__(self):
        return f'<Grade {self.id}>'
