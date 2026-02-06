# FAQ Chatbot for Company Website

A beautiful, modern FAQ chatbot built with Python Flask and a standout web interface. This chatbot can answer common questions about your company, including business hours, contact information, products, pricing, shipping, returns, and account management.

## Features

- ?? **Modern, Standout Interface**: Beautiful gradient design with smooth animations
- ?? **Interactive Chat**: Real-time conversation with typing indicators
- ?? **Smart FAQ Matching**: Intelligent pattern matching for user queries
- ?? **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- ? **Fast & Lightweight**: Quick responses with minimal dependencies
- ?? **Easy to Customize**: Simple to add new FAQ categories and responses

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd faq_chatbot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Customization

### Adding New FAQ Categories

Edit `app.py` and add new entries to the `FAQ_DATABASE` dictionary:

```python
"new_category": {
    "patterns": ["keyword1", "keyword2", "phrase"],
    "responses": [
        "Response 1",
        "Response 2"
    ]
}
```

### Styling

- Modify `static/style.css` to change colors, fonts, and layout
- The color scheme uses CSS variables in `:root` for easy customization

### Adding More Features

- The chatbot can be extended with:
  - Database integration for FAQ storage
  - Machine learning for better intent recognition
  - Multi-language support
  - Chat history persistence
  - Admin panel for FAQ management

## Project Structure

```
faq_chatbot/
??? app.py                 # Flask backend with FAQ logic
??? requirements.txt       # Python dependencies
??? README.md             # This file
??? templates/
?   ??? index.html        # Main HTML template
??? static/
    ??? style.css         # Beautiful styling
    ??? script.js         # Frontend JavaScript
```

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Modern CSS with gradients, animations, and responsive design

## License

This project is open source and available for use in your company website.

## Support

For questions or issues, please contact your development team.
