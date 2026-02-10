from flask import Blueprint, request, jsonify
from datetime import datetime

from models.database_models import NGORequest, NGO, Event
from extensions import db
from validators import validate_ngo_request

# ======================================================
# BLUEPRINT
# ======================================================
ngo_bp = Blueprint("ngo", __name__)

# ======================================================
# CHECK NGO ID (BEFORE POSTING EVENT)
# ======================================================
@ngo_bp.route("/api/ngo/check/<int:ngo_id>", methods=["GET"])
def check_ngo_id(ngo_id):
    ngo = NGO.query.get(ngo_id)

    if not ngo:
        return jsonify({
            "success": False,
            "error": "NGO ID does not exist"
        }), 404

    if not ngo.is_active:
        return jsonify({
            "success": False,
            "error": "NGO is not approved"
        }), 403

    return jsonify({
        "success": True,
        "ngo_name": ngo.ngo_name
    }), 200


# ======================================================
# PARTNER WITH US (SUBMIT REQUEST)
# ======================================================
@ngo_bp.route("/api/ngo/request", methods=["POST"])
def submit_ngo_request():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "errors": {"form": "Invalid data submitted"}
        }), 400

    errors = validate_ngo_request(data)
    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400

    req = NGORequest(
        org_name=data["org_name"],
        contact_person=data["contact_person"],
        email=data["email"],
        phone=data["phone"],
        city=data["city"],
        purpose=data["purpose"],
        description=data["description"],
        status="PENDING"
    )

    db.session.add(req)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Application submitted successfully"
    }), 201


# ======================================================
# POST EVENT (ONLY APPROVED NGOs WITH NGO ID)
# ======================================================
@ngo_bp.route("/api/ngo/post-event", methods=["POST"])
def post_event():
    data = request.get_json()

    # 1️⃣ Validate JSON
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # 2️⃣ Required fields
    required_fields = ["ngo_id", "title", "event_date", "location"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    # 3️⃣ Check NGO exists
    ngo = NGO.query.get(data["ngo_id"])
    if not ngo:
        return jsonify({"error": "NGO ID does not exist"}), 404

    # 4️⃣ Check NGO is approved
    if not ngo.is_active:
        return jsonify({"error": "NGO is not approved"}), 403

    # 5️⃣ Validate date
    try:
        event_date = datetime.strptime(
            data["event_date"], "%Y-%m-%d"
        ).date()
    except ValueError:
        return jsonify({
            "error": "event_date must be in YYYY-MM-DD format"
        }), 400

    # 6️⃣ Create event
    event = Event(
        ngo_id=ngo.ngo_id,
        title=data["title"],
        description=data.get("description"),
        location=data["location"],
        event_date=event_date
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Event posted successfully",
        "ngo_name": ngo.ngo_name,
        "event_id": event.event_id
    }), 201


# ======================================================
# GET EVENTS OF A PARTICULAR NGO (NGO DASHBOARD)
# ======================================================
@ngo_bp.route("/api/ngo/<int:ngo_id>/events", methods=["GET"])
def get_ngo_events(ngo_id):
    ngo = NGO.query.get(ngo_id)

    if not ngo or not ngo.is_active:
        return jsonify({"error": "Unauthorized NGO"}), 403

    events = Event.query.filter_by(
        ngo_id=ngo_id
    ).order_by(Event.event_date.desc()).all()

    return jsonify(
        [event.to_dict() for event in events]
    ), 200
