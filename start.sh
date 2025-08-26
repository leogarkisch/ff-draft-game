#!/bin/bash
# Deploy script for Render or similar platforms

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start the application
gunicorn wsgi:app
