from flask import Flask, render_template, jsonify, request, session
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Sample quiz questions
QUIZ_DATA = {
    "quiz_name": "General Knowledge Quiz",
    "duration_minutes": 10,
    "questions": [
        {
            "id": 1,
            "question": "What is the capital of France?",
            "options": ["London", "Berlin", "Paris", "Madrid"],
            "correct": 2
        },
        {
            "id": 2,
            "question": "Which planet is known as the Red Planet?",
            "options": ["Venus", "Mars", "Jupiter", "Saturn"],
            "correct": 1
        },
        {
            "id": 3,
            "question": "What is the largest ocean on Earth?",
            "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
            "correct": 3
        },
        {
            "id": 4,
            "question": "Who wrote 'Romeo and Juliet'?",
            "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
            "correct": 1
        },
        {
            "id": 5,
            "question": "What is the chemical symbol for gold?",
            "options": ["Go", "Gd", "Au", "Ag"],
            "correct": 2
        },
        {
            "id": 6,
            "question": "Which programming language is known as the 'language of the web'?",
            "options": ["Python", "Java", "JavaScript", "C++"],
            "correct": 2
        },
        {
            "id": 7,
            "question": "What is the smallest prime number?",
            "options": ["0", "1", "2", "3"],
            "correct": 2
        },
        {
            "id": 8,
            "question": "In which year did World War II end?",
            "options": ["1943", "1944", "1945", "1946"],
            "correct": 2
        },
        {
            "id": 9,
            "question": "What is the speed of light in vacuum (approximately)?",
            "options": ["300,000 km/s", "150,000 km/s", "450,000 km/s", "600,000 km/s"],
            "correct": 0
        },
        {
            "id": 10,
            "question": "Which gas makes up most of Earth's atmosphere?",
            "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Argon"],
            "correct": 2
        }
    ]
}

@app.route('/')
def index():
    return render_template('index.html', quiz_data=QUIZ_DATA)

@app.route('/quiz')
def quiz():
    return render_template('quiz.html', quiz_data=QUIZ_DATA)

@app.route('/api/quiz-data')
def get_quiz_data():
    return jsonify(QUIZ_DATA)

@app.route('/api/submit-quiz', methods=['POST'])
def submit_quiz():
    data = request.json
    answers = data.get('answers', {})
    time_taken = data.get('time_taken', 0)
    
    # Calculate score
    correct = 0
    total = len(QUIZ_DATA['questions'])
    results = []
    
    for question in QUIZ_DATA['questions']:
        q_id = str(question['id'])
        user_answer = answers.get(q_id)
        correct_answer = question['correct']
        
        is_correct = user_answer is not None and int(user_answer) == correct_answer
        if is_correct:
            correct += 1
        
        results.append({
            'question_id': question['id'],
            'question': question['question'],
            'user_answer': int(user_answer) if user_answer is not None else None,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'options': question['options']
        })
    
    score_percentage = (correct / total) * 100
    
    return jsonify({
        'score': correct,
        'total': total,
        'percentage': round(score_percentage, 2),
        'time_taken': time_taken,
        'results': results
    })

if __name__ == '__main__':
    # use_reloader=False avoids watching site-packages (e.g. pip), which causes constant restarts
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
