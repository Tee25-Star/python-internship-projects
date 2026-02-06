# Simple Online Store (Flask)

A small e?commerce prototype built with Python (Flask) showcasing:

- A modern, standout UI using Tailwind CSS (via CDN)
- Product catalog with detail pages
- Session-based shopping cart
- Simple checkout simulation (no real payments)

## Features

- **Home page** with a hero section and product grid
- **Product details** page with larger preview and description
- **Cart** page with quantity updates and item removal
- **Checkout** page that collects basic customer details and shows an order summary

## Getting Started

### 1. Create and activate a virtual environment (recommended)

```bash
cd simple_online_store

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# On macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the development server

```bash
python app.py
```

The app will start on `http://127.0.0.1:5000/` by default.

## Project Structure

- `app.py` � main Flask application
- `templates/` � Jinja2 HTML templates
  - `layout.html` � base layout and navigation
  - `index.html` � home page with product grid
  - `product_detail.html` � product details view
  - `cart.html` � shopping cart view
  - `checkout.html` � checkout form and confirmation
- `static/`
  - `css/styles.css` � custom styles (on top of Tailwind)
  - `js/main.js` � small interactive behaviors

## Notes

- This is a demo/prototype: products are stored in memory on the server.
- The checkout flow does **not** process real payments; it only simulates an order confirmation screen.

