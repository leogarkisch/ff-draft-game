#!/usr/bin/env python3
"""
Database initialization script to ensure correct schema
"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, '/Users/leo/VSCode/4fun/ff_number')

from app import app, db

def init_db():
    """Initialize the database with correct schema"""
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("Database initialized successfully!")
        
        # Verify the schema
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # Check GameState table
        game_state_columns = inspector.get_columns('game_state')
        print("\nGameState table columns:")
        for col in game_state_columns:
            print(f"  - {col['name']}: {col['type']}")
            
        # Check Player table  
        player_columns = inspector.get_columns('player')
        print("\nPlayer table columns:")
        for col in player_columns:
            print(f"  - {col['name']}: {col['type']}")

if __name__ == '__main__':
    init_db()
