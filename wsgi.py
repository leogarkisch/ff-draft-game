import os
from app import app, db

if __name__ == '__main__':
    # Ensure database tables are created
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database error: {e}")
    
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
