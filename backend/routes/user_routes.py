from flask import Blueprint, jsonify
from models.database_models import Event

# Blueprint MUST be defined before using it
user_bp = Blueprint("user", __name__)

@user_bp.route("/api/events", methods=["GET"])
def get_events():
    events = Event.query.order_by(Event.event_date.asc()).all()
    return jsonify([event.to_dict() for event in events]), 200
