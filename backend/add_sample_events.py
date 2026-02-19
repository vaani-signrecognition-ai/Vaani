
import os
from datetime import date, timedelta
from flask import Flask
from extensions import db
from models.database_models import NGO, Event

def add_sample_data():
    # Setup App Context
    app = Flask(__name__)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'vaani.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Ensure NGO exists
        test_ngo = NGO.query.filter_by(email="info@deafreach.org").first()
        if not test_ngo:
            test_ngo = NGO(
                ngo_name="Deaf Reach India",
                email="info@deafreach.org",
                phone="9876543210",
                city="Mumbai"
            )
            db.session.add(test_ngo)
            db.session.commit()
            print(f"Created sample NGO: {test_ngo.ngo_name}")
        else:
            print(f"Using existing NGO: {test_ngo.ngo_name}")

        today = date.today()

        sample_events = [
            {
                "title": "ISL Level 1 Workshop",
                "description": "A comprehensive 3-day workshop for beginners to learn basic Indian Sign Language alphabets and common phrases.",
                "event_date": today + timedelta(days=5),
                "location": "Community Center, Mumbai"
            },
            {
                "title": "Inclusive Education Seminar",
                "description": "Discussing strategies for making classrooms more accessible for deaf and hard-of-hearing students.",
                "event_date": today + timedelta(days=15),
                "location": "Online (Zoom)"
            },
            {
                "title": "Signs of Summer Festival",
                "description": "A cultural festival celebrating deaf art, poetry, and performance. All are welcome!",
                "event_date": today + timedelta(days=45),
                "location": "Gateway Park, Delhi"
            },
            {
                "title": "World Deaf Day Celebration",
                "description": "Annual gathering to celebrate our community and advocate for sign language rights.",
                "event_date": today - timedelta(days=30),
                "location": "State Library Hall"
            },
            {
                "title": "Silent Coffee Morning",
                "description": "A casual meetup where everyone communicates only in sign language. Perfect for practice!",
                "event_date": today - timedelta(days=10),
                "location": "Cafe Blue, Bangalore"
            }
        ]

        added_count = 0
        for e_data in sample_events:
            # Check if event already exists to avoid duplicates
            existing = Event.query.filter_by(title=e_data["title"], event_date=e_data["event_date"]).first()
            if not existing:
                new_event = Event(
                    ngo_id=test_ngo.ngo_id,
                    title=e_data["title"],
                    description=e_data["description"],
                    event_date=e_data["event_date"],
                    location=e_data["location"]
                )
                db.session.add(new_event)
                added_count += 1
        
        db.session.commit()
        print(f"Successfully added {added_count} sample events.")

if __name__ == "__main__":
    add_sample_data()
