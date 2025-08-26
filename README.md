# Fantasy Football Draft Order Game

A web application that uses the "2/3 of the average" game theory to determine fantasy football draft order.

## How It Works

Players submit numbers between 0-1000, and whoever gets closest to 2/3 of the average wins first pick!

## Features

- Real-time submission tracking
- Admin panel with password protection
- Mobile-responsive design
- Supports 3-30 players
- Turn-based draft position selection

## Deployment

### Quick Deploy to Render

1. Push this code to GitHub
2. Connect your GitHub repo to [Render](https://render.com)
3. Create a new Web Service
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python wsgi.py`
   - **Environment**: Python 3

### Environment Variables (Optional)

- `SECRET_KEY`: Set a secure secret key for sessions

### Admin Access

- Password: `ff2025admin`
- Access admin panel at `/admin`

## Local Development

1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Initialize database: `python init_db.py`
5. Run app: `python app.py`

## Game Rules

- Choose a number between 0 and 1000
- Goal: Get closest to 2/3 of everyone's average
- Winner picks draft position first
- Everyone else picks in turn-based order