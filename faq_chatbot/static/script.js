const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');

// Add message to chat
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    const avatarSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    avatarSvg.setAttribute('viewBox', '0 0 24 24');
    avatarSvg.setAttribute('fill', 'none');
    avatarSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z');
    path.setAttribute('fill', 'currentColor');
    avatarSvg.appendChild(path);
    avatar.appendChild(avatarSvg);
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Format message text (handle line breaks and lists)
    const formattedText = formatMessage(text);
    content.innerHTML = formattedText;
    
    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    });
    content.appendChild(time);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Format message text to handle line breaks and lists
function formatMessage(text) {
    // Split by newlines
    let formatted = text.split('\n').map(line => {
        line = line.trim();
        if (!line) return '';
        
        // Check if it's a list item
        if (line.startsWith('•') || line.startsWith('-') || line.match(/^\d+\./)) {
            return `<li>${line.replace(/^[•\-\d+\.]\s*/, '')}</li>`;
        }
        
        return `<p>${escapeHtml(line)}</p>`;
    }).join('');
    
    // Wrap consecutive list items in <ul>
    formatted = formatted.replace(/(<li>.*?<\/li>(?:\s*<li>.*?<\/li>)*)/g, '<ul>$1</ul>');
    
    return formatted;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show typing indicator
function showTyping() {
    typingIndicator.style.display = 'block';
    scrollToBottom();
}

// Hide typing indicator
function hideTyping() {
    typingIndicator.style.display = 'none';
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Disable input while processing
    userInput.disabled = true;
    sendButton.disabled = true;
    
    // Add user message
    addMessage(message, true);
    userInput.value = '';
    
    // Show typing indicator
    showTyping();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTyping();
        
        // Add bot response
        setTimeout(() => {
            addMessage(data.response, false);
        }, 300);
        
    } catch (error) {
        hideTyping();
        addMessage("I'm sorry, I'm having trouble connecting. Please try again later.", false);
        console.error('Error:', error);
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Focus input on load
window.addEventListener('load', () => {
    userInput.focus();
});

// Smooth scroll on new messages
const observer = new MutationObserver(() => {
    scrollToBottom();
});

observer.observe(chatMessages, { childList: true });
