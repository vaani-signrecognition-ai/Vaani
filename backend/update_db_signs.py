import os
import sys

# Force SQLite for this script
os.environ["DATABASE_URL"] = "sqlite:///vaani.db"

# Add backend to path to import app and models
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import app
from extensions import db
from models.database_models import SignDictionary

# Directory where we copied the images (relative to frontend root)
image_base_url = "assets/dictionary/"

with app.app_context():
    # Get list of files in the dictionary assets folder
    assets_dir = r"c:\Users\Admn\Documents\GitHub\Vaani\backend\templates\frontend\assets\dictionary"
    image_files = [f for f in os.listdir(assets_dir) if f.endswith(".jpg")]
    
    # Track additions
    added_count = 0
    updated_count = 0
    
    for filename in image_files:
        word = os.path.splitext(filename)[0]
        image_path = f"{image_base_url}{filename}"
        
        # Check if already exists
        existing = SignDictionary.query.filter_by(word=word).first()
        if existing:
            existing.image_path = image_path
            updated_count += 1
        else:
            new_sign = SignDictionary(
                word=word,
                starting_letter=word[0].upper() if word else "",
                image_path=image_path,
                video_path="" # Default empty for now
            )
            db.session.add(new_sign)
            added_count += 1
            
    db.session.commit()
    print(f"Database updated: {added_count} added, {updated_count} updated.")
