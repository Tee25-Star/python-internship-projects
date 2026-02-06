// Initialize Socket.IO connection
const socket = io();

// DOM Elements
const usernameModal = document.getElementById('usernameModal');
const usernameInput = document.getElementById('usernameInput');
const joinButton = document.getElementById('joinButton');
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const emojiBtn = document.getElementById('emojiBtn');
const connectionStatus = document.getElementById('connectionStatus');
const statusText = document.getElementById('statusText');
const userCount = document.getElementById('userCount');
const userList = document.getElementById('userList');
const typingIndicator = document.getElementById('typingIndicator');
const typingText = document.getElementById('typingText');
const charCount = document.getElementById('charCount');

// State
let currentUsername = '';
let isTyping = false;
let typingTimeout = null;
let welcomeMessageShown = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkStoredUsername();
});

// Event Listeners
function setupEventListeners() {
    // Join chat
    joinButton.addEventListener('click', joinChat);
    usernameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') joinChat();
    });

    // Send message
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Typing indicator
    messageInput.addEventListener('input', handleTyping);
    messageInput.addEventListener('input', updateCharCount);

    // Emoji button (placeholder)
    emojiBtn.addEventListener('click', () => {
        // Future: Add emoji picker
        messageInput.focus();
    });
}

// Check for stored username
function checkStoredUsername() {
    const stored = localStorage.getItem('chatUsername');
    if (stored) {
        usernameInput.value = stored;
    }
}

// Join Chat
function joinChat() {
    const username = usernameInput.value.trim();
    if (!username) {
        usernameInput.focus();
        return;
    }

    currentUsername = username;
    localStorage.setItem('chatUsername', username);
    
    socket.emit('join', { username });
    usernameModal.classList.add('hidden');
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.focus();
    
    // Remove welcome message
    if (!welcomeMessageShown) {
        const welcomeMsg = messagesContainer.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
            welcomeMessageShown = true;
        }
    }
}

// Send Message
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !currentUsername) return;

    socket.emit('message', { message });
    messageInput.value = '';
    updateCharCount();
    stopTyping();
}

// Handle Typing
function handleTyping() {
    if (!isTyping) {
        isTyping = true;
        socket.emit('typing', { typing: true });
    }

    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        stopTyping();
    }, 1000);
}

function stopTyping() {
    if (isTyping) {
        isTyping = false;
        socket.emit('typing', { typing: false });
    }
    clearTimeout(typingTimeout);
}

// Update Character Count
function updateCharCount() {
    const count = messageInput.value.length;
    charCount.textContent = count;
    if (count > 450) {
        charCount.style.color = '#f5576c';
    } else {
        charCount.style.color = '';
    }
}

// Socket Event Handlers

// Connection Status
socket.on('connect', () => {
    connectionStatus.classList.add('connected');
    statusText.textContent = 'Connected';
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    connectionStatus.classList.remove('connected');
    statusText.textContent = 'Disconnected';
    console.log('Disconnected from server');
});

socket.on('connected', (data) => {
    console.log('Server:', data.message);
});

// Chat History
socket.on('chat_history', (data) => {
    if (data.messages && data.messages.length > 0) {
        data.messages.forEach(msg => {
            displayMessage(msg);
        });
        scrollToBottom();
    }
});

// New Message
socket.on('message', (data) => {
    displayMessage(data);
    scrollToBottom();
});

// Display Message
function displayMessage(data) {
    const isOwnMessage = data.username === currentUsername;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isOwnMessage ? 'own-message' : ''}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = data.username.charAt(0).toUpperCase();
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const header = document.createElement('div');
    header.className = 'message-header';
    
    const username = document.createElement('span');
    username.className = 'message-username';
    username.textContent = data.username;
    
    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = data.timestamp;
    
    header.appendChild(username);
    header.appendChild(time);
    
    const text = document.createElement('div');
    text.className = 'message-text';
    text.textContent = data.message;
    
    content.appendChild(header);
    content.appendChild(text);
    
    if (!isOwnMessage) {
        messageDiv.appendChild(avatar);
    }
    messageDiv.appendChild(content);
    if (isOwnMessage) {
        messageDiv.appendChild(avatar);
    }
    
    messageDiv.classList.add('notification');
    messagesContainer.appendChild(messageDiv);
}

// User Joined
socket.on('user_joined', (data) => {
    displaySystemMessage(`${data.username} joined the chat`, 'join');
    updateUserCount(data.active_count);
});

// User Left
socket.on('user_left', (data) => {
    displaySystemMessage(`${data.username} left the chat`, 'leave');
    updateUserCount(data.active_count);
});

// System Message
function displaySystemMessage(message, type = '') {
    const systemDiv = document.createElement('div');
    systemDiv.className = `system-message ${type}`;
    systemDiv.textContent = message;
    messagesContainer.appendChild(systemDiv);
    scrollToBottom();
}

// User List
socket.on('user_list', (data) => {
    updateUserList(data.users);
    updateUserCount(data.count);
});

function updateUserList(users) {
    userList.innerHTML = '';
    
    if (users.length === 0) {
        userList.innerHTML = '<div class="empty-users">No users online</div>';
        return;
    }
    
    users.forEach(username => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';
        
        const avatar = document.createElement('div');
        avatar.className = 'user-avatar';
        avatar.textContent = username.charAt(0).toUpperCase();
        
        const name = document.createElement('div');
        name.className = 'user-name';
        name.textContent = username;
        
        userItem.appendChild(avatar);
        userItem.appendChild(name);
        userList.appendChild(userItem);
    });
}

function updateUserCount(count) {
    userCount.textContent = count;
}

// Typing Indicator
socket.on('typing', (data) => {
    if (data.typing && data.username !== currentUsername) {
        typingText.textContent = `${data.username} is typing...`;
        typingIndicator.style.display = 'flex';
    } else {
        typingIndicator.style.display = 'none';
    }
});

// Scroll to Bottom
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Auto-scroll on new messages
const observer = new MutationObserver(() => {
    scrollToBottom();
});

observer.observe(messagesContainer, { childList: true });
