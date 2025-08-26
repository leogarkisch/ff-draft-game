#!/bin/bash

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install flask==2.3.3 flask-sqlalchemy==3.0.5 pytz==2023.3

# Run the Flask app
echo "Starting Flask application..."
echo "Open your browser to: http://localhost:5000"
echo "Admin panel at: http://localhost:5000/admin"
python app.py