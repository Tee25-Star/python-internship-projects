from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os
from uuid import uuid4

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# File to store tickets (simple JSON storage)
TICKETS_FILE = 'tickets.json'


def load_tickets():
    """Load tickets from JSON file"""
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_tickets(tickets):
    """Save tickets to JSON file"""
    with open(TICKETS_FILE, 'w') as f:
        json.dump(tickets, f, indent=2)


def get_ticket_by_id(ticket_id):
    """Get a specific ticket by ID"""
    tickets = load_tickets()
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            return ticket
    return None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get all tickets"""
    tickets = load_tickets()
    # Sort by created date (newest first)
    tickets.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(tickets)


@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    """Create a new ticket"""
    data = request.json
    tickets = load_tickets()

    new_ticket = {
        'id': str(uuid4()),
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'priority': data.get('priority', 'medium'),
        'status': 'open',
        'category': data.get('category', 'general'),
        'requester': data.get('requester', 'Anonymous'),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'assigned_to': None,
        'comments': []
    }

    tickets.append(new_ticket)
    save_tickets(tickets)
    return jsonify(new_ticket), 201


@app.route('/api/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a specific ticket"""
    ticket = get_ticket_by_id(ticket_id)
    if ticket:
        return jsonify(ticket)
    return jsonify({'error': 'Ticket not found'}), 404


@app.route('/api/tickets/<ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """Update a ticket"""
    tickets = load_tickets()
    data = request.json

    for i, ticket in enumerate(tickets):
        if ticket['id'] == ticket_id:
            # Update allowed fields
            if 'title' in data:
                ticket['title'] = data['title']
            if 'description' in data:
                ticket['description'] = data['description']
            if 'priority' in data:
                ticket['priority'] = data['priority']
            if 'status' in data:
                ticket['status'] = data['status']
            if 'category' in data:
                ticket['category'] = data['category']
            if 'assigned_to' in data:
                ticket['assigned_to'] = data['assigned_to']

            ticket['updated_at'] = datetime.now().isoformat()
            save_tickets(tickets)
            return jsonify(ticket)

    return jsonify({'error': 'Ticket not found'}), 404


@app.route('/api/tickets/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """Delete a ticket"""
    tickets = load_tickets()
    tickets = [t for t in tickets if t['id'] != ticket_id]
    save_tickets(tickets)
    return jsonify({'message': 'Ticket deleted'}), 200


@app.route('/api/tickets/<ticket_id>/comments', methods=['POST'])
def add_comment(ticket_id):
    """Add a comment to a ticket"""
    tickets = load_tickets()
    data = request.json

    for ticket in tickets:
        if ticket['id'] == ticket_id:
            comment = {
                'id': str(uuid4()),
                'text': data.get('text', ''),
                'author': data.get('author', 'Anonymous'),
                'created_at': datetime.now().isoformat()
            }
            ticket['comments'].append(comment)
            ticket['updated_at'] = datetime.now().isoformat()
            save_tickets(tickets)
            return jsonify(comment), 201

    return jsonify({'error': 'Ticket not found'}), 404


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about tickets"""
    tickets = load_tickets()
    stats = {
        'total': len(tickets),
        'open': len([t for t in tickets if t['status'] == 'open']),
        'in_progress': len([t for t in tickets if t['status'] == 'in_progress']),
        'resolved': len([t for t in tickets if t['status'] == 'resolved']),
        'closed': len([t for t in tickets if t['status'] == 'closed']),
        'high_priority': len([t for t in tickets if t['priority'] == 'high']),
        'medium_priority': len([t for t in tickets if t['priority'] == 'medium']),
        'low_priority': len([t for t in tickets if t['priority'] == 'low'])
    }
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
