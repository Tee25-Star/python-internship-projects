# Classified Ads Platform

A full-featured classified ads platform built with Python and Flask.

## Features

- User registration and authentication
- Create, edit, and delete classified ads
- Category-based organization
- Search and filter ads
- User profiles and ad management
- Modern, responsive web interface

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the database:
```bash
python app.py
```
The database will be automatically created on first run.

## Usage

1. Run the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Register a new account or login to start posting ads!

## Project Structure

```
classified_ads_platform/
??? app.py                 # Main Flask application
??? models.py              # Database models
??? forms.py               # WTForms for user input
??? requirements.txt       # Python dependencies
??? templates/             # HTML templates
?   ??? base.html
?   ??? index.html
?   ??? register.html
?   ??? login.html
?   ??? create_ad.html
?   ??? ad_detail.html
?   ??? my_ads.html
?   ??? search.html
??? static/                # CSS and static files
    ??? style.css
```

## Database Models

- **User**: Stores user account information
- **Category**: Ad categories (Electronics, Vehicles, Real Estate, etc.)
- **Ad**: Classified ad listings with title, description, price, etc.
