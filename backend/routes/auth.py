from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models.database_models import NGOAccount
from extensions import db
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/ngo/login", methods=["POST"])
def ngo_login():
    data = request.json
    account = NGOAccount.query.filter_by(email=data["email"]).first()

    if not account or not check_password_hash(account.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    if not account.is_active:
        return jsonify({"error": "Account disabled"}), 403

    account.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "success": True,
        "ngo_account_id": account.account_id
    }), 200
