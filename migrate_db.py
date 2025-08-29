#!/usr/bin/env python3
"""
Migration script to add initialization fields to GameState table
"""

import sqlite3
import os

def migrate_database():
    # Path to the main database
    db_path = 'my_data.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the main app first to create it.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the new columns exist
    cursor.execute("PRAGMA table_info(game_state)")
    columns = [column[1] for column in cursor.fetchall()]
    
    changes_made = False
    
    # Add is_simulation column if it doesn't exist
    if 'is_simulation' not in columns:
        try:
            cursor.execute("ALTER TABLE game_state ADD COLUMN is_simulation BOOLEAN DEFAULT 0")
            print("✅ Added is_simulation column")
            changes_made = True
        except sqlite3.Error as e:
            print(f"❌ Error adding is_simulation column: {e}")
    else:
        print("ℹ️  is_simulation column already exists")
    
    # Add is_initialized column if it doesn't exist
    if 'is_initialized' not in columns:
        try:
            cursor.execute("ALTER TABLE game_state ADD COLUMN is_initialized BOOLEAN DEFAULT 0")
            print("✅ Added is_initialized column")
            changes_made = True
        except sqlite3.Error as e:
            print(f"❌ Error adding is_initialized column: {e}")
    else:
        print("ℹ️  is_initialized column already exists")
    
    # Commit changes
    if changes_made:
        conn.commit()
        print("✅ Database migration completed successfully")
    else:
        print("ℹ️  No migration needed - all columns exist")
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate_database()
    print("✨ Migration process complete!")
