from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from datetime import datetime
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from utils.email_sender import send_approval_email, send_rejection_email

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Import models here to avoid circular imports
        from models.database_models import SignDictionary, NGO, Event, NGORequest, NGOAccount
        # Create all tables
        db.create_all()
    
    return app

app = create_app()

# Import models after app creation
from models.database_models import SignDictionary, NGO, Event, NGORequest, NGOAccount

# ---------------- MAIN PAGE ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ngo.html")
def ngo():
    return render_template("ngo.html")

@app.route("/events.html")
def events():
    return render_template("events.html")

@app.route("/admin")
def admin():
    return render_template("admin_requests.html")

# ---------------- SERVE JS/CSS FROM TEMPLATES ----------------
@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(app.template_folder, 'js'), filename)

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(app.template_folder, 'css'), filename)

# ---------------- API ENDPOINTS ----------------
@app.route("/api/dictionary", methods=["GET"])
def get_dictionary():
    try:
        search = request.args.get('search', '').strip()
        
        if search:
            # Search by word or starting letter
            signs = SignDictionary.query.filter(
                (SignDictionary.word.ilike(f'%{search}%')) | 
                (SignDictionary.starting_letter.ilike(search[0] if search else ''))
            ).order_by(SignDictionary.word).all()
        else:
            # Get all signs (limit 100)
            signs = SignDictionary.query.order_by(SignDictionary.word).limit(100).all()

        return jsonify([sign.to_dict() for sign in signs]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        events = Event.query.order_by(Event.event_date.desc()).all()
        return jsonify([event.to_dict() for event in events]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ngo/post-event", methods=["POST"])
def post_event():
    data = request.json

    ngo_id = data.get("ngo_id")
    title = data.get("title")
    description = data.get("description")
    event_date = data.get("event_date")
    location = data.get("location")

    print(f"Received event data: ngo_id={ngo_id}, title={title}, date={event_date}, location={location}")

    if not all([ngo_id, title, event_date, location]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Create new event
        new_event = Event(
            ngo_id=ngo_id,
            title=title,
            description=description,
            event_date=datetime.strptime(event_date, '%Y-%m-%d').date(),
            location=location
        )
        
        db.session.add(new_event)
        db.session.commit()

        print("Event posted successfully")
        return jsonify({
            "message": "Event posted successfully"
        }), 201

    except Exception as e:
        print(f"Error posting event: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/ngo/partner", methods=["POST"])
def partner_with_ngo():
    print("=== Partner request received ===")
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    print(f"Request data: {request.data}")
    
    data = request.json
    print(f"Parsed JSON data: {data}")

    # Match fields from NEW index.html form
    org_name = data.get("org_name")
    contact_person = data.get("contact_person")
    email = data.get("email")
    phone = data.get("phone")
    city = data.get("city")
    purpose = data.get("purpose")
    description = data.get("description")

    print(f"Extracted fields - org: {org_name}, contact: {contact_person}, email: {email}, phone: {phone}, city: {city}, purpose: {purpose}")

    if not all([org_name, contact_person, email, phone, city, purpose, description]):
        print("ERROR: Missing required fields")
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        # Create new NGO request
        new_request = NGORequest(
            org_name=org_name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            city=city,
            purpose=purpose,
            description=description,
            status="PENDING"
        )
        
        db.session.add(new_request)
        db.session.commit()

        print("Partnership request inserted successfully")
        return jsonify({
            "success": True,
            "message": "NGO partnership request submitted successfully"
        }), 201

    except Exception as e:
        print(f"Error in partner_with_ngo: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/admin/ngo-requests", methods=["GET"])
def get_ngo_requests():
    try:
        requests = NGORequest.query.order_by(NGORequest.submitted_at.desc()).all()
        return jsonify([req.to_dict() for req in requests]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/ngo-request/action", methods=["POST"])
def handle_ngo_request_action():
    data = request.json
    request_id = data.get("request_id")
    action = data.get("action")

    if action not in ["APPROVED", "REJECTED"]:
        return jsonify({"error": "Invalid action"}), 400

    try:
        # Get the request
        ngo_request = NGORequest.query.get(request_id)
        if not ngo_request:
            return jsonify({"error": "Request not found"}), 404
        
        # Check if already processed
        if ngo_request.status != "PENDING":
            return jsonify({"error": f"Request already {ngo_request.status.lower()}"}), 400
        
        # Update request status
        ngo_request.status = action

        # If approved → create NGO account and NGO entry
        if action == "APPROVED":
            email = ngo_request.email
            org_name = ngo_request.org_name
            phone = ngo_request.phone
            city = ngo_request.city

            # Check if NGO or account already exists with this email
            existing_ngo = NGO.query.filter_by(email=email).first()
            existing_account = NGOAccount.query.filter_by(email=email).first()
            
            if existing_ngo or existing_account:
                db.session.rollback()
                return jsonify({"error": "An NGO with this email already exists"}), 400

            temp_password = "VAANI@" + ''.join(
                random.choices(string.digits, k=4)
            )

            password_hash = generate_password_hash(temp_password)

            # Create NGO entry in ngos table
            new_ngo = NGO(
                ngo_name=org_name,
                email=email,
                phone=phone,
                city=city,
                is_active=True
            )
            db.session.add(new_ngo)
            db.session.flush()  # Get the ngo_id

            # Create NGO account
            new_account = NGOAccount(
                request_id=request_id,
                email=email,
                password_hash=password_hash,
                is_active=True
            )
            
            db.session.add(new_account)
            db.session.commit()

            # Try to send approval email (don't fail if email fails)
            try:
                send_approval_email(email, org_name, temp_password)
            except Exception as email_error:
                print(f"Warning: Failed to send approval email: {email_error}")

            return jsonify({
                "message": "NGO approved and account created",
                "temp_password": temp_password,   # demo purpose
                "ngo_id": new_ngo.ngo_id
            }), 200
        
        # Send rejection email if rejected
        if action == "REJECTED":
            db.session.commit()
            try:
                send_rejection_email(ngo_request.email, ngo_request.org_name)
            except Exception as email_error:
                print(f"Warning: Failed to send rejection email: {email_error}")
        
        return jsonify({"message": "NGO request rejected"}), 200

    except Exception as e:
        print(f"Error in handle_ngo_request_action: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/ngos", methods=["GET"])
def get_ngos():
    """Get all active NGO partners"""
    try:
        ngos = NGO.query.filter_by(is_active=True).order_by(NGO.created_at.desc()).all()
        return jsonify([ngo.to_dict() for ngo in ngos]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- ML PREDICTION ENDPOINTS ----------------
@app.route("/api/predict/word", methods=["POST"])
def predict_word_endpoint():
    """
    Predict ISL word from image
    Expects: multipart/form-data with 'image' file
    Returns: { "word": "hello", "confidence": 0.95 }
    """
    try:
        # Lazy import to avoid loading TensorFlow at startup
        from models.word_predict import predict_word
        
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        # Read image bytes
        image_bytes = image_file.read()
        
        # Get prediction
        word, confidence = predict_word(image_bytes)
        
        return jsonify({
            "word": word,
            "confidence": confidence
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict/alphabet", methods=["POST"])
def predict_alphabet_endpoint():
    """
    Predict ISL alphabet/letter from image
    Expects: multipart/form-data with 'image' file
    Returns: { "letter": "A", "confidence": 0.98 }
    """
    try:
        # Lazy import to avoid loading TensorFlow at startup
        from models.alpha_predict import predict_alphabet
        
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        # Read image bytes
        image_bytes = image_file.read()
        
        # Get prediction
        letter, confidence = predict_alphabet(image_bytes)
        
        return jsonify({
            "letter": letter,
            "confidence": confidence
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
