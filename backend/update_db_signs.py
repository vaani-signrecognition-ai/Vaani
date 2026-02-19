import os
import sys

# Default to SQLite if no DATABASE_URL is set, but don't force it
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///vaani.db"

# Add current directory to path
sys.path.append(os.getcwd())

from app import app
from extensions import db
from models.database_models import SignDictionary

# Directory where we copied the images (relative to backend)
image_base_url = "assets/dictionary/"
# Path to assets directory relative to this script's location
base_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(base_dir, "templates", "frontend", "assets", "dictionary")

with app.app_context():
    if not os.path.exists(assets_dir):
        print(f"Assets directory not found at {assets_dir}")
        sys.exit(1)
        
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
