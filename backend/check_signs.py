import os
import sys

# Add backend to path to import app and models
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import app
from extensions import db
from models.database_models import SignDictionary

with app.app_context():
    signs = SignDictionary.query.all()
    print(f"Total signs in database: {len(signs)}")
    for sign in signs:
        print(f"- {sign.word}: {sign.image_url}")
