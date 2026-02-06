from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active users
active_users = {}
# Store chat messages (in production, use a database)
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle new client connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to chat server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    user_id = request.sid
    if user_id in active_users:
        username = active_users[user_id]['username']
        del active_users[user_id]
        emit('user_left', {
            'username': username,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'active_count': len(active_users)
        }, broadcast=True)
    print(f'Client disconnected: {user_id}')

@socketio.on('join')
def handle_join(data):
    """Handle user joining the chat"""
    username = data.get('username', 'Anonymous')
    user_id = request.sid
    
    active_users[user_id] = {
        'username': username,
        'joined_at': datetime.now().isoformat()
    }
    
    # Send chat history to new user
    emit('chat_history', {'messages': chat_history[-50:]})  # Last 50 messages
    
    # Notify others
    emit('user_joined', {
        'username': username,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'active_count': len(active_users)
    }, broadcast=True, include_self=False)
    
    # Send updated user list
    emit('user_list', {
        'users': [user['username'] for user in active_users.values()],
        'count': len(active_users)
    }, broadcast=True)

@socketio.on('message')
def handle_message(data):
    """Handle incoming chat messages"""
    user_id = request.sid
    username = active_users.get(user_id, {}).get('username', 'Anonymous')
    message = data.get('message', '').strip()
    
    if not message:
        return
    
    message_data = {
        'id': str(uuid.uuid4()),
        'username': username,
        'message': message,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'datetime': datetime.now().isoformat()
    }
    
    # Store message
    chat_history.append(message_data)
    
    # Keep only last 1000 messages in memory
    if len(chat_history) > 1000:
        chat_history.pop(0)
    
    # Broadcast to all clients
    emit('message', message_data, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicators"""
    user_id = request.sid
    username = active_users.get(user_id, {}).get('username', 'Anonymous')
    is_typing = data.get('typing', False)
    
    emit('typing', {
        'username': username,
        'typing': is_typing
    }, broadcast=True, include_self=False)

if __name__ == '__main__':
    print("?? Live Chat Server starting on http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
