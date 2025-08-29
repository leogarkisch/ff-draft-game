# Fantasy Football Draft Order Game - Claude Setup Guide

## Quick Start Checklist

### 📋 Before Running Commands
Always verify you're in the correct directory before running any commands:

```bash
# Check current directory
pwd

# Should show: /Users/leo/VSCode/4fun/ff_number
# If not, navigate there first:
cd /Users/leo/VSCode/4fun/ff_number
```

### 🚀 Single Command Startup
Once in the correct directory, run:
```bash
./run.sh
```

This single script handles everything:
- ✅ Directory validation
- ✅ Process cleanup (kills any existing Flask on port 5001)
- ✅ Virtual environment activation
- ✅ Dependency installation
- ✅ Database initialization/migration
- ✅ Flask app startup

### 🔧 Manual Setup (if needed)
If the run script fails, you can run steps manually:

```bash
# 1. Ensure you're in the right directory
cd /Users/leo/VSCode/4fun/ff_number

# 2. Kill any existing processes
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install flask flask-sqlalchemy pytz

# 5. Initialize database (first time)
python init_db.py

# 6. Start app
python app.py
```

### 🗂️ Project Structure
```
ff_number/
├── app.py              # Main Flask application
├── init_db.py          # Database initialization
├── migrate_db.py       # Database migration utility
├── run.sh              # Consolidated startup script
├── setup_and_run.sh    # Alternative setup script
├── venv/               # Python virtual environment
├── templates/          # HTML templates
│   ├── not_initialized.html # Message for uninitialized game
│   ├── admin.html      # Admin panel with initialization controls
│   └── ...
├── static/             # CSS, JS, images
│   ├── style.css       # Consolidated Bears-themed CSS (202 lines)
│   └── script.js
└── my_data.db          # SQLite database (created automatically)
```

### 🎮 Game Features
- **Admin-Only Initialization**: Game setup handled entirely through admin console
- **Initialization System**: Must complete setup in admin panel before users can access game
- **Simulation Mode**: Toggle between real and simulation runs (admin control)
- **Admin Panel**: Full game control and initialization at http://localhost:5001/admin
- **Bears Theme**: Consolidated CSS with Chicago Bears colors
- **Database Migration**: Automatic schema updates

### 🔍 Troubleshooting

#### "Not in the correct directory" Error
```bash
# The run.sh script will show this error if you're not in the right place
# Solution: Always navigate to the project directory first
cd /Users/leo/VSCode/4fun/ff_number
./run.sh
```

#### "Port 5001 already in use"
```bash
# Kill existing processes
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
```

#### Database Issues
```bash
# Reset database completely
rm -f my_data.db
python init_db.py
```

#### Template Syntax Errors
```bash
# If you see Jinja2 template errors, check for:
# - Duplicate {% endblock %} tags
# - Unclosed template blocks
# - Missing template inheritance
# Recent fix: Removed duplicate endblock in draft_selection.html
```

#### CSS/Styling Issues
```bash
# If styling looks broken:
# - Clear browser cache (Cmd+Shift+R)
# - Check if style.css is loading properly
# - Verify consolidated CSS includes all necessary classes
# Recent enhancement: Snake draft table now has professional styling
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install flask flask-sqlalchemy pytz
```

### 📊 Database Schema
The database includes these key fields:
- `GameState`: phase, winner_id, num_teams, league_name, **is_simulation**, **is_initialized**
- `Player`: name, email, guess, timestamp, draft_position, ip_address

### 🎯 Recent Updates
- **CSS Consolidation**: Reduced from 1119 to 202+ lines (82% reduction) with enhanced snake draft styling
- **Bears Branding Fix**: Ensured ALL colors use proper Chicago Bears color variables (Navy/Orange theme)
- **Admin-Only Initialization**: All game setup moved to admin panel (no separate setup page)
- **Initialization System**: Mandatory setup phase accessible only through admin console
- **Simulation Mode**: Integrated toggle for real vs simulation runs (admin control)
- **Directory Validation**: Run script validates location before execution
- **Database Migration**: Seamless schema updates for new features
- **Template Fixes**: Resolved Jinja2 syntax errors in draft_selection.html
- **Snake Draft Enhancement**: Professional table styling with Bears theming and interactive elements

### ⚡ Quick Commands Reference
```bash
# Start everything (main command)
cd /Users/leo/VSCode/4fun/ff_number && ./run.sh

# Just check directory
pwd

# Quick app restart (if already set up)
cd /Users/leo/VSCode/4fun/ff_number && source venv/bin/activate && python app.py

# Reset everything
cd /Users/leo/VSCode/4fun/ff_number && rm -f my_data.db && ./run.sh
```
