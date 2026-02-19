import os
import sys
from dotenv import load_dotenv

# Ensure we are in the backend directory context
sys.path.append(os.getcwd())

# Load .env
load_dotenv(override=True)

from app import app
from extensions import db
from models.database_models import SignDictionary, NGO, Event, NGORequest, NGOAccount

def init_database():
    print("--- VAANI Database Initialization ---")
    db_url = os.getenv("DATABASE_URL")
    print(f"Target Database: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    with app.app_context():
        try:
            print("Creating tables if they don't exist...")
            db.create_all()
            print("SUCCESS: Tables created / already exist.")
            
            # Check if dictionary is empty
            count = SignDictionary.query.count()
            print(f"Current dictionary entries: {count}")
            
            if count == 0:
                print("Dictionary is empty. You should run 'python backend/update_db_signs.py' to populate it.")
            
        except Exception as e:
            print(f"ERROR: Could not initialize database: {e}")
            print("\nPRO TIP: If you see 'password authentication failed' or 'connection timed out':")
            print("1. Verify your DATABASE_URL in .env is correct.")
            print("2. Ensure your IP address is whitelisted in Render's 'Access Control' settings.")

if __name__ == "__main__":
    init_database()
