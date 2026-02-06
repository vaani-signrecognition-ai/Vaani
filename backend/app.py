<<<<<<< Updated upstream
=======
import re
import os
import random
import string
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from config import Config
from extensions import db
from utils.email_sender import send_approval_email, send_rejection_email

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# ================= ENV SETUP =================
load_dotenv()
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"


# ================= APP FACTORY =================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    with app.app_context():
        from models.database_models import (
            SignDictionary,
            NGO,
            Event,
            NGORequest,
            NGOAccount
        )
        db.create_all()

    return app


# ================= CREATE APP =================
app = create_app()

from models.database_models import (
    SignDictionary,
    NGO,
    Event,
    NGORequest,
    NGOAccount
)


# ================= FRONTEND SERVING =================
@app.route("/")
def serve_loading():
    return send_from_directory(FRONTEND_DIR, "loading.html")


@app.route("/<path:filename>")
def serve_frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)



# ================= HEALTH CHECK =================
@app.route("/ping")
def ping():
    return "FLASK ROUTES ARE WORKING"


# ================= API: DICTIONARY =================
@app.route("/api/dictionary", methods=["GET"])
def get_dictionary():
    try:
        search = request.args.get("search", "").strip()

        if search:
            signs = SignDictionary.query.filter(
                (SignDictionary.word.ilike(f"%{search}%")) |
                (SignDictionary.starting_letter.ilike(search[0]))
            ).order_by(SignDictionary.word).all()
        else:
            signs = SignDictionary.query.order_by(SignDictionary.word).limit(100).all()

        return jsonify([sign.to_dict() for sign in signs]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= API: EVENTS =================
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        events = Event.query.order_by(Event.event_date.asc()).all()
        return jsonify([event.to_dict() for event in events]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ngo/post-event", methods=["POST"])
def post_event():
    data = request.json

    if not all([data.get("ngo_id"), data.get("title"),
                data.get("event_date"), data.get("location")]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        event = Event(
            ngo_id=data["ngo_id"],
            title=data["title"],
            description=data.get("description"),
            location=data["location"],
            event_date=datetime.strptime(data["event_date"], "%Y-%m-%d").date()
        )

        db.session.add(event)
        db.session.commit()
        return jsonify({"message": "Event posted successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ================= NGO PARTNERSHIP =================
@app.route("/api/ngo/partner", methods=["POST"])
def partner_with_ngo():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        required_fields = [
            "org_name", "contact_person", "email",
            "phone", "city", "purpose", "description"
        ]

        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400

        if not is_valid_email(data["email"]):
            return jsonify({"success": False, "error": "Invalid email"}), 400

        if not is_valid_phone(data["phone"]):
            return jsonify({"success": False, "error": "Invalid phone"}), 400

        if not is_valid_city(data["city"]):
            return jsonify({"success": False, "error": "Invalid city"}), 400

        new_request = NGORequest(
            org_name=data["org_name"],
            contact_person=data["contact_person"],
            email=data["email"],
            phone=data["phone"],
            city=data["city"],
            purpose=data["purpose"],
            description=data["description"],
            status="PENDING"
        )

        db.session.add(new_request)
        db.session.commit()

        return jsonify({"success": True}), 201

    except Exception:
        db.session.rollback()
        return jsonify({"success": False}), 500


# ================= VALIDATORS =================
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)


def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10


def is_valid_city(city):
    return city.replace(" ", "").isalpha()


# ================= ADMIN =================
@app.route("/api/admin/ngo-requests", methods=["GET"])
def get_ngo_requests():
    requests = NGORequest.query.order_by(
        NGORequest.submitted_at.desc()
    ).all()

    return jsonify([req.to_dict() for req in requests]), 200


@app.route("/api/admin/ngo-request/action", methods=["POST"])
def handle_ngo_request_action():
    data = request.json
    request_id = data.get("request_id")
    action = data.get("action")

    ngo_request = NGORequest.query.get(request_id)
    if not ngo_request:
        return jsonify({"error": "Invalid request"}), 400

    ngo_request.status = action

    if action == "APPROVED":
        temp_password = "VAANI@" + ''.join(random.choices(string.digits, k=4))
        password_hash = generate_password_hash(temp_password)

        new_ngo = NGO(
            ngo_name=ngo_request.org_name,
            email=ngo_request.email,
            phone=ngo_request.phone,
            city=ngo_request.city,
            is_active=True
        )

        db.session.add(new_ngo)
        db.session.commit()

        send_approval_email(
            ngo_request.email,
            ngo_request.org_name,
            temp_password
        )
    else:
        send_rejection_email(
            ngo_request.email,
            ngo_request.org_name
        )

    db.session.commit()
    return jsonify({"message": "Action completed"}), 200

def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

# Serve any html file (about.html, events.html, etc.)
@app.route("/<path:filename>")
def serve_frontend(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> Stashed changes
