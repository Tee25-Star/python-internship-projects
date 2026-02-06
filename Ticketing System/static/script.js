// Global state
let allTickets = [];
let filteredTickets = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadTickets();
    setupEventListeners();
    updateStats();
});

// Event Listeners
function setupEventListeners() {
    // New ticket button
    document.getElementById('newTicketBtn').addEventListener('click', () => {
        document.getElementById('newTicketModal').classList.add('active');
    });

    // Close modals
    document.getElementById('closeNewTicketModal').addEventListener('click', closeNewTicketModal);
    document.getElementById('closeDetailModal').addEventListener('click', closeDetailModal);
    document.getElementById('cancelNewTicket').addEventListener('click', closeNewTicketModal);

    // Click outside modal to close
    document.getElementById('newTicketModal').addEventListener('click', (e) => {
        if (e.target.id === 'newTicketModal') closeNewTicketModal();
    });

    document.getElementById('ticketDetailModal').addEventListener('click', (e) => {
        if (e.target.id === 'ticketDetailModal') closeDetailModal();
    });

    // New ticket form
    document.getElementById('newTicketForm').addEventListener('submit', handleNewTicketSubmit);

    // Filters
    document.getElementById('statusFilter').addEventListener('change', applyFilters);
    document.getElementById('priorityFilter').addEventListener('change', applyFilters);
    document.getElementById('searchInput').addEventListener('input', applyFilters);
}

// Load tickets from API
async function loadTickets() {
    try {
        const response = await fetch('/api/tickets');
        allTickets = await response.json();
        filteredTickets = [...allTickets];
        renderTickets();
        updateStats();
    } catch (error) {
        console.error('Error loading tickets:', error);
        showNotification('Error loading tickets', 'error');
    }
}

// Render tickets
function renderTickets() {
    const grid = document.getElementById('ticketsGrid');

    if (filteredTickets.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-secondary);">
                <i class="fas fa-inbox" style="font-size: 64px; margin-bottom: 20px; opacity: 0.5;"></i>
                <h3>No tickets found</h3>
                <p>Create your first ticket to get started!</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = filteredTickets.map(ticket => createTicketCard(ticket)).join('');

    // Add click listeners to ticket cards
    document.querySelectorAll('.ticket-card').forEach(card => {
        card.addEventListener('click', () => {
            const ticketId = card.dataset.ticketId;
            showTicketDetail(ticketId);
        });
    });
}

// Create ticket card HTML
function createTicketCard(ticket) {
    const createdDate = new Date(ticket.created_at).toLocaleDateString();
    const statusClass = ticket.status.replace('_', '-');

    return `
        <div class="ticket-card" data-ticket-id="${ticket.id}">
            <div class="ticket-header">
                <span class="ticket-id">#${ticket.id.substring(0, 8)}</span>
            </div>
            <h3 class="ticket-title">${escapeHtml(ticket.title)}</h3>
            <p class="ticket-description">${escapeHtml(ticket.description)}</p>
            <div class="ticket-meta">
                <span class="badge badge-status ${statusClass}">${ticket.status.replace('_', ' ')}</span>
                <span class="badge badge-priority ${ticket.priority}">${ticket.priority}</span>
                <span class="badge badge-category">${ticket.category}</span>
            </div>
            <div class="ticket-footer">
                <div class="ticket-requester">
                    <i class="fas fa-user"></i>
                    <span>${escapeHtml(ticket.requester)}</span>
                </div>
                <div class="ticket-date">
                    <i class="fas fa-calendar"></i>
                    <span>${createdDate}</span>
                </div>
            </div>
        </div>
    `;
}

// Show ticket detail
async function showTicketDetail(ticketId) {
    try {
        const response = await fetch(`/api/tickets/${ticketId}`);
        const ticket = await response.json();

        const modal = document.getElementById('ticketDetailModal');
        const content = document.getElementById('ticketDetailContent');

        const createdDate = new Date(ticket.created_at).toLocaleString();
        const updatedDate = new Date(ticket.updated_at).toLocaleString();
        const statusClass = ticket.status.replace('_', '-');

        content.innerHTML = `
            <div class="detail-section">
                <h3>Ticket Information</h3>
                <div class="detail-info">
                    <div class="detail-item">
                        <label>ID</label>
                        <span>#${ticket.id.substring(0, 8)}</span>
                    </div>
                    <div class="detail-item">
                        <label>Status</label>
                        <span>
                            <span class="badge badge-status ${statusClass}">${ticket.status.replace('_', ' ')}</span>
                        </span>
                    </div>
                    <div class="detail-item">
                        <label>Priority</label>
                        <span>
                            <span class="badge badge-priority ${ticket.priority}">${ticket.priority}</span>
                        </span>
                    </div>
                    <div class="detail-item">
                        <label>Category</label>
                        <span>
                            <span class="badge badge-category">${ticket.category}</span>
                        </span>
                    </div>
                    <div class="detail-item">
                        <label>Requester</label>
                        <span>${escapeHtml(ticket.requester)}</span>
                    </div>
                    <div class="detail-item">
                        <label>Assigned To</label>
                        <span>${ticket.assigned_to || 'Unassigned'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Created</label>
                        <span>${createdDate}</span>
                    </div>
                    <div class="detail-item">
                        <label>Last Updated</label>
                        <span>${updatedDate}</span>
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3>Title</h3>
                <h2 style="font-size: 24px; font-weight: 600; margin-bottom: 15px;">${escapeHtml(ticket.title)}</h2>
            </div>
            
            <div class="detail-section">
                <h3>Description</h3>
                <div class="detail-description">${escapeHtml(ticket.description).replace(/\n/g, '<br>')}</div>
            </div>
            
            <div class="detail-section">
                <h3>Status</h3>
                <select id="detailStatus" class="form-group" style="width: 200px; padding: 10px; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);">
                    <option value="open" ${ticket.status === 'open' ? 'selected' : ''}>Open</option>
                    <option value="in_progress" ${ticket.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                    <option value="resolved" ${ticket.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                    <option value="closed" ${ticket.status === 'closed' ? 'selected' : ''}>Closed</option>
                </select>
                <button class="btn-primary" style="margin-top: 10px;" onclick="updateTicketStatus('${ticket.id}')">Update Status</button>
            </div>
            
            <div class="comments-section">
                <h3>Comments (${ticket.comments.length})</h3>
                <div id="commentsList">
                    ${ticket.comments.map(comment => `
                        <div class="comment">
                            <div class="comment-header">
                                <span class="comment-author">${escapeHtml(comment.author)}</span>
                                <span class="comment-date">${new Date(comment.created_at).toLocaleString()}</span>
                            </div>
                            <div class="comment-text">${escapeHtml(comment.text).replace(/\n/g, '<br>')}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="add-comment-form">
                    <textarea id="newCommentText" placeholder="Add a comment..."></textarea>
                    <button class="btn-primary" onclick="addComment('${ticket.id}')">Add Comment</button>
                </div>
            </div>
        `;

        document.getElementById('detailTitle').textContent = ticket.title;
        modal.classList.add('active');
    } catch (error) {
        console.error('Error loading ticket detail:', error);
        showNotification('Error loading ticket details', 'error');
    }
}

// Update ticket status
async function updateTicketStatus(ticketId) {
    const status = document.getElementById('detailStatus').value;

    try {
        const response = await fetch(`/api/tickets/${ticketId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });

        if (response.ok) {
            showNotification('Status updated successfully', 'success');
            loadTickets();
            showTicketDetail(ticketId); // Refresh detail view
        } else {
            showNotification('Error updating status', 'error');
        }
    } catch (error) {
        console.error('Error updating status:', error);
        showNotification('Error updating status', 'error');
    }
}

// Add comment
async function addComment(ticketId) {
    const text = document.getElementById('newCommentText').value.trim();
    if (!text) {
        showNotification('Please enter a comment', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/tickets/${ticketId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                author: 'Current User' // In a real app, this would come from authentication
            })
        });

        if (response.ok) {
            document.getElementById('newCommentText').value = '';
            showNotification('Comment added successfully', 'success');
            showTicketDetail(ticketId); // Refresh detail view
        } else {
            showNotification('Error adding comment', 'error');
        }
    } catch (error) {
        console.error('Error adding comment:', error);
        showNotification('Error adding comment', 'error');
    }
}

// Handle new ticket form submission
async function handleNewTicketSubmit(e) {
    e.preventDefault();

    const ticketData = {
        title: document.getElementById('ticketTitle').value,
        description: document.getElementById('ticketDescription').value,
        requester: document.getElementById('ticketRequester').value,
        category: document.getElementById('ticketCategory').value,
        priority: document.getElementById('ticketPriority').value
    };

    try {
        const response = await fetch('/api/tickets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ticketData)
        });

        if (response.ok) {
            showNotification('Ticket created successfully!', 'success');
            closeNewTicketModal();
            document.getElementById('newTicketForm').reset();
            loadTickets();
        } else {
            showNotification('Error creating ticket', 'error');
        }
    } catch (error) {
        console.error('Error creating ticket:', error);
        showNotification('Error creating ticket', 'error');
    }
}

// Apply filters
function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value;
    const priorityFilter = document.getElementById('priorityFilter').value;
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();

    filteredTickets = allTickets.filter(ticket => {
        const matchesStatus = statusFilter === 'all' || ticket.status === statusFilter;
        const matchesPriority = priorityFilter === 'all' || ticket.priority === priorityFilter;
        const matchesSearch = searchTerm === '' ||
            ticket.title.toLowerCase().includes(searchTerm) ||
            ticket.description.toLowerCase().includes(searchTerm) ||
            ticket.requester.toLowerCase().includes(searchTerm);

        return matchesStatus && matchesPriority && matchesSearch;
    });

    renderTickets();
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-open').textContent = stats.open;
        document.getElementById('stat-progress').textContent = stats.in_progress;
        document.getElementById('stat-resolved').textContent = stats.resolved;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Close modals
function closeNewTicketModal() {
    document.getElementById('newTicketModal').classList.remove('active');
}

function closeDetailModal() {
    document.getElementById('ticketDetailModal').classList.remove('active');
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // Simple notification - you could enhance this with a toast library
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS for notification animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
