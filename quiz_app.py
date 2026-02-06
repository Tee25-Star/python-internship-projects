from flask import Flask, render_template, request, jsonify, session
import random
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Sample quiz questions - you can expand this or load from a database
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct": 2,
        "points": 10
    },
    {
        "id": 2,
        "question": "Which programming language is known as the 'language of the web'?",
        "options": ["Python", "JavaScript", "Java", "C++"],
        "correct": 1,
        "points": 10
    },
    {
        "id": 3,
        "question": "What does HTML stand for?",
        "options": [
            "HyperText Markup Language",
            "High Tech Modern Language",
            "Home Tool Markup Language",
            "Hyperlink and Text Markup Language"
        ],
        "correct": 0,
        "points": 10
    },
    {
        "id": 4,
        "question": "Which of the following is NOT a Python data type?",
        "options": ["List", "Dictionary", "Array", "Tuple"],
        "correct": 2,
        "points": 15
    },
    {
        "id": 5,
        "question": "What is the result of 2 ** 3 in Python?",
        "options": ["6", "8", "9", "5"],
        "correct": 1,
        "points": 10
    },
    {
        "id": 6,
        "question": "Which protocol is used for secure web communication?",
        "options": ["HTTP", "FTP", "HTTPS", "SMTP"],
        "correct": 2,
        "points": 15
    },
    {
        "id": 7,
        "question": "What is the time complexity of binary search?",
        "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
        "correct": 1,
        "points": 20
    },
    {
        "id": 8,
        "question": "Which CSS property is used to change text color?",
        "options": ["text-color", "font-color", "color", "text-style"],
        "correct": 2,
        "points": 10
    },
    {
        "id": 9,
        "question": "What is the main purpose of a database?",
        "options": [
            "To store and organize data",
            "To create websites",
            "To run applications",
            "To manage networks"
        ],
        "correct": 0,
        "points": 15
    },
    {
        "id": 10,
        "question": "Which of these is a NoSQL database?",
        "options": ["MySQL", "PostgreSQL", "MongoDB", "Oracle"],
        "correct": 2,
        "points": 15
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    data = request.json
    student_name = data.get('name', 'Student')
    time_limit = int(data.get('time_limit', 30))  # minutes
    
    # Shuffle questions for variety
    questions = random.sample(QUIZ_QUESTIONS, min(10, len(QUIZ_QUESTIONS)))
    
    session['student_name'] = student_name
    session['questions'] = questions
    session['answers'] = {}
    session['start_time'] = datetime.now().isoformat()
    session['time_limit'] = time_limit
    session['current_question'] = 0
    
    return jsonify({
        'success': True,
        'total_questions': len(questions),
        'time_limit': time_limit
    })

@app.route('/quiz')
def quiz():
    if 'questions' not in session:
        return render_template('index.html')
    return render_template('quiz.html')

@app.route('/get_quiz_info')
def get_quiz_info():
    if 'questions' not in session:
        return jsonify({'error': 'No quiz started'}), 400
    
    return jsonify({
        'time_limit': session.get('time_limit', 30),
        'total_questions': len(session['questions']),
        'start_time': session.get('start_time')
    })

@app.route('/get_question/<int:question_num>')
def get_question(question_num):
    if 'questions' not in session:
        return jsonify({'error': 'No quiz started'}), 400
    
    questions = session['questions']
    if question_num < 0 or question_num >= len(questions):
        return jsonify({'error': 'Invalid question number'}), 400
    
    question = questions[question_num]
    # Don't send the correct answer to the client
    question_data = {
        'id': question['id'],
        'question': question['question'],
        'options': question['options'],
        'points': question['points'],
        'question_num': question_num + 1,
        'total_questions': len(questions)
    }
    
    return jsonify(question_data)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'questions' not in session:
        return jsonify({'error': 'No quiz started'}), 400
    
    data = request.json
    question_id = data.get('question_id')
    answer_index = data.get('answer_index')
    question_num = data.get('question_num')
    
    if question_id is None or answer_index is None:
        return jsonify({'error': 'Missing data'}), 400
    
    # Store the answer
    if 'answers' not in session:
        session['answers'] = {}
    
    session['answers'][question_id] = answer_index
    session['current_question'] = question_num
    
    return jsonify({'success': True})

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'questions' not in session or 'answers' not in session:
        return jsonify({'error': 'No quiz to submit'}), 400
    
    questions = session['questions']
    answers = session['answers']
    student_name = session.get('student_name', 'Student')
    
    # Calculate score
    total_score = 0
    max_score = 0
    results = []
    
    for question in questions:
        max_score += question['points']
        question_id = question['id']
        user_answer = answers.get(question_id)
        correct_answer = question['correct']
        
        is_correct = (user_answer == correct_answer)
        if is_correct:
            total_score += question['points']
        
        results.append({
            'question': question['question'],
            'user_answer': question['options'][user_answer] if user_answer is not None else 'Not answered',
            'correct_answer': question['options'][correct_answer],
            'is_correct': is_correct,
            'points': question['points'] if is_correct else 0
        })
    
    # Calculate percentage
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Clear session
    session.clear()
    
    return jsonify({
        'success': True,
        'student_name': student_name,
        'total_score': total_score,
        'max_score': max_score,
        'percentage': round(percentage, 2),
        'results': results
    })

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
