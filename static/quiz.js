let currentQuestion = 0;
let totalQuestions = 0;
let questions = [];
let answers = {};
let timeLimit = 30; // minutes
let timeRemaining = 0; // seconds
let timerInterval = null;
let timeLimitSeconds = 0;

document.addEventListener('DOMContentLoaded', async function() {
    // Get quiz info including time limit
    await getQuizInfo();
    // Load first question
    await loadQuestion(0);
    startTimer();
    
    // Event listeners
    document.getElementById('next-btn').addEventListener('click', nextQuestion);
    document.getElementById('prev-btn').addEventListener('click', prevQuestion);
    document.getElementById('submit-btn').addEventListener('click', submitQuiz);
});

async function loadQuestion(questionNum) {
    try {
        const response = await fetch(`/get_question/${questionNum}`);
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            window.location.href = '/';
            return;
        }
        
        currentQuestion = questionNum;
        totalQuestions = data.total_questions;
        
        // Update UI
        document.getElementById('question-number').textContent = `Question ${data.question_num}`;
        document.getElementById('question-text').textContent = data.question;
        document.getElementById('question-points').textContent = `${data.points} pts`;
        
        // Update progress
        const progress = ((data.question_num) / totalQuestions) * 100;
        document.getElementById('progress-fill').style.width = `${progress}%`;
        document.getElementById('question-counter').textContent = `${data.question_num} / ${totalQuestions}`;
        
        // Load options
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';
        
        data.options.forEach((option, index) => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'option';
            if (answers[data.id] === index) {
                optionDiv.classList.add('selected');
            }
            optionDiv.textContent = option;
            optionDiv.addEventListener('click', () => selectOption(data.id, index, optionDiv));
            optionsContainer.appendChild(optionDiv);
        });
        
        // Update navigation buttons
        document.getElementById('prev-btn').disabled = questionNum === 0;
        
        if (questionNum === totalQuestions - 1) {
            document.getElementById('next-btn').style.display = 'none';
            document.getElementById('submit-btn').style.display = 'block';
        } else {
            document.getElementById('next-btn').style.display = 'block';
            document.getElementById('submit-btn').style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error loading question:', error);
        alert('Failed to load question. Please try again.');
    }
}

function selectOption(questionId, optionIndex, optionElement) {
    // Remove selected class from all options
    const options = document.querySelectorAll('.option');
    options.forEach(opt => opt.classList.remove('selected'));
    
    // Add selected class to clicked option
    optionElement.classList.add('selected');
    
    // Store answer
    answers[questionId] = optionIndex;
    
    // Save answer to server
    saveAnswer(questionId, optionIndex);
}

async function saveAnswer(questionId, answerIndex) {
    try {
        await fetch('/submit_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question_id: questionId,
                answer_index: answerIndex,
                question_num: currentQuestion
            })
        });
    } catch (error) {
        console.error('Error saving answer:', error);
    }
}

function nextQuestion() {
    if (currentQuestion < totalQuestions - 1) {
        loadQuestion(currentQuestion + 1);
    }
}

function prevQuestion() {
    if (currentQuestion > 0) {
        loadQuestion(currentQuestion - 1);
    }
}

async function submitQuiz() {
    if (!confirm('Are you sure you want to submit the quiz? You cannot change your answers after submission.')) {
        return;
    }
    
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Submitting...';
    
    try {
        const response = await fetch('/submit_quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store results in sessionStorage to pass to results page
            sessionStorage.setItem('quizResults', JSON.stringify(data));
            window.location.href = '/results';
        } else {
            alert('Failed to submit quiz. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Quiz';
        }
    } catch (error) {
        console.error('Error submitting quiz:', error);
        alert('An error occurred. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Quiz';
    }
}

async function getQuizInfo() {
    try {
        const response = await fetch('/get_quiz_info');
        const data = await response.json();
        
        if (data.error) {
            console.error(data.error);
            return;
        }
        
        timeLimit = data.time_limit;
        totalQuestions = data.total_questions;
    } catch (error) {
        console.error('Error getting quiz info:', error);
    }
}

function startTimer() {
    // Convert minutes to seconds
    timeLimitSeconds = timeLimit * 60;
    timeRemaining = timeLimitSeconds;
    
    updateTimerDisplay();
    
    timerInterval = setInterval(() => {
        timeRemaining--;
        updateTimerDisplay();
        
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            alert('Time is up! Submitting your quiz automatically.');
            submitQuiz();
        } else if (timeRemaining <= 60) {
            // Add warning class when less than 1 minute
            document.getElementById('timer').classList.add('warning');
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    const timerElement = document.getElementById('timer');
    timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Prevent accidental page refresh
window.addEventListener('beforeunload', function(e) {
    if (timerInterval) {
        e.preventDefault();
        e.returnValue = '';
    }
});
