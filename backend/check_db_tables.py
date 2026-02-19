
import os
import sys
from flask import Flask
from extensions import db
from models.database_models import NGORequest, NGO, Event, SignDictionary, NGOAccount

def check_tables():
    print("Checking database tables...")
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    local_db_path = os.path.join(BASE_DIR, 'vaani.db')
    
    if not os.path.exists(local_db_path):
        print(f"Error: Database file not found at {local_db_path}")
        return
        
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{local_db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # This will create any missing tables
        db.create_all()
        print("Database tables verified/created.")
        
        # Check NGORequest table
        try:
            count = NGORequest.query.count()
            print(f"NGORequest table exists, current count: {count}")
        except Exception as e:
            print(f"Error checking NGORequest table: {str(e)}")

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    check_tables()
