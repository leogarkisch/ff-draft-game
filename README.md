# Fantasy Football Draft Order Game 🏈

A Flask web application that uses game theory to determine fantasy football draft order. Players submit number guesses, and the person closest to 2/3 of the average wins first pick!

## Features

- **Game Theory Based**: Uses the "2/3 of the average" concept
- **Chicago Bears Themed**: Navy and orange color scheme throughout
- **Mobile Responsive**: Works on all devices
- **Admin Panel**: Manage game phases and view results
- **Automatic Backups**: Data is automatically backed up
- **Draft Position Selection**: Winners choose their preferred draft spots

## Quick Start

### Local Development
```bash
./run.sh
```
This single command handles everything: environment setup, dependencies, database initialization, and starting the app.

### Manual Setup
```bash
cd /Users/leo/VSCode/4fun/ff_number
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

## Game Flow

1. **Submission Phase**: Players enter guesses (0-1000)
2. **Results Phase**: System calculates 2/3 of average
3. **Selection Phase**: Winners choose draft positions in order
4. **Completed**: Final draft order is set

## Admin Access

- URL: `/admin/login`
- Password: `ff2025admin`
- Features: Game management, backups, phase control

## Deployment

Deployed on Railway at: https://ff-draft-game-production.up.railway.app

### Deploy Updates
```bash
railway up
```

## Technology Stack

- **Backend**: Flask + SQLAlchemy
- **Database**: SQLite (local) / PostgreSQL (production)
- **Frontend**: Bootstrap 5 + Custom CSS
- **Deployment**: Railway

## File Structure

```
├── app.py              # Main Flask application
├── init_db.py          # Database setup
├── requirements.txt    # Python dependencies
├── run.sh             # Local development script
├── static/            # CSS and JavaScript
├── templates/         # HTML templates
└── backups/           # Automatic backups
```