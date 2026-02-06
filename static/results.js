document.addEventListener('DOMContentLoaded', function() {
    // Get results from sessionStorage
    const resultsData = sessionStorage.getItem('quizResults');
    
    if (!resultsData) {
        alert('No quiz results found. Redirecting to home page.');
        window.location.href = '/';
        return;
    }
    
    const data = JSON.parse(resultsData);
    
    // Display results
    displayResults(data);
    
    // Clear sessionStorage
    sessionStorage.removeItem('quizResults');
});

function displayResults(data) {
    // Update header
    document.getElementById('student-name').textContent = data.student_name;
    
    // Update score
    const percentage = data.percentage;
    document.getElementById('score-value').textContent = `${percentage}%`;
    document.getElementById('total-score').textContent = data.total_score;
    document.getElementById('max-score').textContent = data.max_score;
    
    // Animate score circle
    const circumference = 2 * Math.PI * 45; // radius is 45
    const offset = circumference - (percentage / 100) * circumference;
    const scoreProgress = document.getElementById('score-progress');
    scoreProgress.style.strokeDashoffset = offset;
    
    // Set gradient for score circle
    const svg = document.querySelector('.score-svg');
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    gradient.setAttribute('id', 'scoreGradient');
    gradient.setAttribute('x1', '0%');
    gradient.setAttribute('y1', '0%');
    gradient.setAttribute('x2', '100%');
    gradient.setAttribute('y2', '100%');
    
    const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop1.setAttribute('offset', '0%');
    stop1.setAttribute('stop-color', '#6366f1');
    
    const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop2.setAttribute('offset', '100%');
    stop2.setAttribute('stop-color', '#8b5cf6');
    
    gradient.appendChild(stop1);
    gradient.appendChild(stop2);
    defs.appendChild(gradient);
    svg.appendChild(defs);
    
    // Update results icon based on score
    const resultsIcon = document.getElementById('results-icon');
    if (percentage >= 80) {
        resultsIcon.textContent = '??';
    } else if (percentage >= 60) {
        resultsIcon.textContent = '??';
    } else if (percentage >= 40) {
        resultsIcon.textContent = '??';
    } else {
        resultsIcon.textContent = '??';
    }
    
    // Display detailed results
    const resultsSummary = document.getElementById('results-summary');
    resultsSummary.innerHTML = '<h3 style="margin-bottom: 20px; color: var(--text-primary);">Detailed Results</h3>';
    
    data.results.forEach((result, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${result.is_correct ? 'correct' : 'incorrect'}`;
        resultItem.style.animationDelay = `${index * 0.1}s`;
        
        const questionDiv = document.createElement('div');
        questionDiv.className = 'result-question';
        questionDiv.textContent = `${index + 1}. ${result.question}`;
        resultItem.appendChild(questionDiv);
        
        const answersDiv = document.createElement('div');
        answersDiv.className = 'result-answer';
        
        const userAnswerDiv = document.createElement('div');
        userAnswerDiv.className = 'result-answer-item user';
        userAnswerDiv.innerHTML = `<strong>Your Answer:</strong> ${result.user_answer}`;
        answersDiv.appendChild(userAnswerDiv);
        
        if (!result.is_correct) {
            const correctAnswerDiv = document.createElement('div');
            correctAnswerDiv.className = 'result-answer-item correct';
            correctAnswerDiv.innerHTML = `<strong>Correct Answer:</strong> ${result.correct_answer}`;
            answersDiv.appendChild(correctAnswerDiv);
        }
        
        resultItem.appendChild(answersDiv);
        
        const pointsDiv = document.createElement('div');
        pointsDiv.className = 'result-points';
        if (result.is_correct) {
            pointsDiv.textContent = `? Earned ${result.points} points`;
            pointsDiv.style.color = '#059669';
        } else {
            pointsDiv.textContent = `? No points earned`;
            pointsDiv.style.color = '#dc2626';
        }
        resultItem.appendChild(pointsDiv);
        
        resultsSummary.appendChild(resultItem);
    });
}
