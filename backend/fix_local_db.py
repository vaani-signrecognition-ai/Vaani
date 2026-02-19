
import os
import sys
from flask import Flask
from extensions import db
from models.database_models import SignDictionary
from config import Config

def fix_db():
    print("Setting up local SQLite database for Dictionary...")
    
    local_db_path = os.path.join(os.path.dirname(__file__), 'vaani.db')
    
    # Delete old DB to ensure fresh schema
    if os.path.exists(local_db_path):
        print(f"Removing old database: {local_db_path}")
        os.remove(local_db_path)
        
    database_uri = f"sqlite:///{local_db_path}"
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()

        # Path to images
        assets_dir = os.path.join(os.path.dirname(__file__), 'templates', 'frontend', 'assets', 'dictionary')
        
        if not os.path.exists(assets_dir):
            print(f"Error: Dictionary assets not found at {assets_dir}")
            return
            
        print(f"Scanning images in {assets_dir}...")
        
        files = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for filename in files:
            # Get word from filename (e.g., hello.jpg -> hello)
            word = os.path.splitext(filename)[0].replace('_', ' ')
            starting_letter = word[0].upper() if word else '?'
            
            # Path for frontend (relative to assets/)
            image_path = f"assets/dictionary/{filename}"
            
            new_sign = SignDictionary(
                word=word,
                starting_letter=starting_letter,
                image_path=image_path
            )
            db.session.add(new_sign)
            
        db.session.commit()
        print(f"Success! Populated {len(files)} signs into local database.")
        print(f"Database saved to: {local_db_path}")

if __name__ == "__main__":
    # Add parent dir to path to import models and extensions
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    fix_db()
