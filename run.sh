#!/bin/bash

# Fantasy Football Draft Order Game - Local Setup Script
echo "🏈 Starting Fantasy Football Draft Order Game..."

# Navigate to the correct directory and validate
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Validate we're in the right directory by checking for required files
if [[ ! -f "app.py" ]] || [[ ! -f "init_db.py" ]] || [[ ! -d "venv" ]]; then
    echo "❌ ERROR: Not in the correct directory or missing required files!"
    echo "📁 Current directory: $(pwd)"
    echo "📋 Required files: app.py, init_db.py, venv/"
    echo "💡 Make sure you're running this script from the ff_number directory"
    echo "💡 Or run: cd /Users/leo/VSCode/4fun/ff_number && ./run.sh"
    exit 1
fi

echo "✅ Directory validated: $(pwd)"

# Kill any existing processes on port 5001
echo "🔄 Cleaning up any existing processes..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q flask flask-sqlalchemy pytz

# Initialize database if it doesn't exist, or migrate if it does
echo "🗄️ Setting up database..."
if [ ! -f "my_data.db" ]; then
    echo "Creating new database..."
    python init_db.py
else
    echo "Database exists, checking for migrations..."
    python migrate_db.py
fi

# Start the Flask application
echo "🚀 Starting Flask app on http://localhost:5001"
echo "📱 Admin panel: http://localhost:5001/admin (password: ff2025admin)"
echo "✨ New features: Customizable league name & improved dark mode!"
echo "⚠️  Press Ctrl+C to stop the server"
echo ""

python app.py
