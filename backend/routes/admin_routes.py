from flask import Blueprint, request, jsonify
from models.database_models import NGORequest, NGO
from extensions import db
from utils.email_sender import send_approval_email

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/api/admin/ngo-requests", methods=["GET"])
def get_requests():
    return jsonify([
        r.to_dict() for r in NGORequest.query.all()
    ])

@admin_bp.route("/api/admin/ngo-request/action", methods=["POST"])
def handle_action():
    data = request.json
    req = NGORequest.query.get(data["request_id"])

    if not req:
        return jsonify({"error": "Invalid request"}), 400

    if data["action"] == "APPROVED":
        ngo = NGO(
            ngo_name=req.org_name,
            email=req.email,
            phone=req.phone,
            city=req.city,
            is_active=True
        )
        db.session.add(ngo)
        db.session.commit()  # NGO ID GENERATED

        req.status = "APPROVED"
        db.session.commit()

        send_approval_email(req.email, req.org_name, ngo.ngo_id)

    else:
        req.status = "REJECTED"
        db.session.commit()

    return jsonify({"success": True})
