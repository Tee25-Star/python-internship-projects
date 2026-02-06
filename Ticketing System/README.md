# Service Request / Ticketing System

A beautiful, modern web-based ticketing system built with Python Flask. Create, manage, and track service requests with an intuitive and visually stunning interface.

## Features

- ?? **Create Tickets** - Submit new service requests with title, description, priority, and category
- ?? **Dashboard** - Real-time statistics showing total, open, in-progress, and resolved tickets
- ?? **Filter & Search** - Filter tickets by status and priority, search by keywords
- ?? **Comments** - Add comments to tickets for collaboration
- ?? **Responsive Design** - Beautiful interface that works on all devices
- ?? **Modern UI** - Stunning gradient design with smooth animations

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Usage

### Creating a Ticket
1. Click the "New Ticket" button in the header
2. Fill in the ticket details:
   - Title (required)
   - Requester name (required)
   - Category (General, Technical, Billing, Support, Feature Request)
   - Priority (Low, Medium, High)
   - Description (required)
3. Click "Create Ticket"

### Managing Tickets
- Click on any ticket card to view full details
- Update ticket status (Open, In Progress, Resolved, Closed)
- Add comments to tickets
- Filter tickets by status or priority
- Search tickets by title, description, or requester name

### Ticket Statuses
- **Open** - Newly created ticket
- **In Progress** - Ticket is being worked on
- **Resolved** - Issue has been resolved
- **Closed** - Ticket is closed

### Priorities
- **High** - Urgent issues requiring immediate attention
- **Medium** - Standard priority (default)
- **Low** - Non-urgent requests

## Project Structure

```
ticketing_system/
??? app.py              # Flask application and API routes
??? templates/
?   ??? index.html      # Main HTML template
??? static/
?   ??? style.css       # Stunning CSS styles
?   ??? script.js        # JavaScript for interactivity
??? tickets.json        # Data storage (created automatically)
??? requirements.txt    # Python dependencies
??? README.md          # This file
```

## API Endpoints

- `GET /api/tickets` - Get all tickets
- `POST /api/tickets` - Create a new ticket
- `GET /api/tickets/<id>` - Get a specific ticket
- `PUT /api/tickets/<id>` - Update a ticket
- `DELETE /api/tickets/<id>` - Delete a ticket
- `POST /api/tickets/<id>/comments` - Add a comment to a ticket
- `GET /api/stats` - Get ticket statistics

## Data Storage

Tickets are stored in a JSON file (`tickets.json`) for simplicity. For production use, consider migrating to a proper database like PostgreSQL or SQLite.

## Customization

### Changing Colors
Edit the CSS variables in `static/style.css`:
```css
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    /* ... */
}
```

### Adding Categories
Edit the category options in `templates/index.html`:
```html
<select id="ticketCategory">
    <option value="your-category">Your Category</option>
</select>
```

## Technologies Used

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Icons:** Font Awesome 6.4.0
- **Fonts:** Inter (Google Fonts)

## License

This project is open source and available for personal and commercial use.

## Future Enhancements

- User authentication and authorization
- Email notifications
- File attachments
- Ticket assignment to team members
- Advanced reporting and analytics
- Database integration (PostgreSQL/SQLite)
- Real-time updates with WebSockets
