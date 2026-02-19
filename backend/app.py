print("[DEBUG] backend/app.py loaded!")
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db
import os
from datetime import datetime
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from utils.email_sender import send_approval_email, send_rejection_email

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
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

# ---------------- MAIN PAGE (NEW FRONTEND) ----------------
@app.route("/")
@app.route("/index.html")
def home():
    return render_template("frontend/index.html")

@app.route("/loading.html")
def loading():
    return render_template("frontend/loading.html")

@app.route("/about.html")
def about():
    return render_template("frontend/about.html")

@app.route("/dictionary.html")
def dictionary():
    return render_template("frontend/dictionary.html")

@app.route("/events.html")
def events():
    return render_template("frontend/events.html")

@app.route("/ngo-partners.html")
def ngo_partners():
    return render_template("frontend/ngo-partners.html")

@app.route("/contact.html")
def contact():
    return render_template("frontend/contact.html")

@app.route("/admin")
def admin():
    return render_template("admin_requests.html")

# ---------------- SERVE STATIC FILES FROM NEW FRONTEND ----------------
@app.route("/style.css")
def serve_new_frontend_css():
    return send_from_directory(os.path.join(app.template_folder, 'frontend'), 'style.css')

@app.route("/<path:filename>")
def serve_new_frontend_assets(filename):
    # Serve images and other assets from new_frontend folder
    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.avif')):
        return send_from_directory(os.path.join(app.template_folder, 'frontend'), filename)
    # Fallback to templates folder for other static files
    return send_from_directory(app.template_folder, filename)

# ---------------- SERVE JS/CSS FROM TEMPLATES ----------------
@app.route("/js/<path:filename>")
def serve_js(filename):
    # Try main js folder first, then frontend/js
    main_js = os.path.join(app.template_folder, 'js')
    frontend_js = os.path.join(app.template_folder, 'frontend', 'js')
    if os.path.exists(os.path.join(main_js, filename)):
        return send_from_directory(main_js, filename)
    return send_from_directory(frontend_js, filename)

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(app.template_folder, 'css'), filename)

# ---------------- API ENDPOINTS ----------------
@app.route("/api/dictionary", methods=["GET"])
def get_dictionary():
    try:
        search = request.args.get('search', '').strip()
        
        if search:
            # 1. Try exact match first
            exact_match = SignDictionary.query.filter(SignDictionary.word.ilike(search)).first()
            
            # 2. Get fuzzy matches on the word
            other_matches = SignDictionary.query.filter(
                SignDictionary.word.ilike(f'%{search}%'),
                SignDictionary.word.is_not(search)
            ).all()

            # 3. If it's a single letter, include other signs starting with that letter
            letter_matches = []
            if len(search) == 1:
                letter_matches = SignDictionary.query.filter(
                    SignDictionary.starting_letter.ilike(search),
                    SignDictionary.word.is_not(search),
                    ~SignDictionary.word.ilike(f'%{search}%') # Don't duplicate
                ).all()

            # Combine: Exact first, then others
            signs = ([exact_match] if exact_match else []) + other_matches + letter_matches
            
            # Limit total results
            signs = signs[:50]
        else:
            # Get all signs (limit 100)
            signs = SignDictionary.query.order_by(SignDictionary.word).limit(100).all()

        return jsonify([sign.to_dict() for sign in signs if sign is not None]), 200

    except Exception as e:
        print(f"[ERROR] Dictionary API failure: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        import heapq
        from datetime import date
        
        # Get all events
        all_events = Event.query.all()
        
        # Use simple sorting first, or implement a Priority Queue (Min-Heap) 
        # to efficiently get upcoming events
        
        today = date.today()
        upcoming_heap = []
        past_events = []
        
        for event in all_events:
            event_data = event.to_dict()
            event_date = date.fromisoformat(event_data['event_date'])
            
            if event_date >= today:
                # Priority Queue stores (date, event_data)
                # Python's heapq is a min-heap, so earliest date comes first
                heapq.heappush(upcoming_heap, (event_data['event_date'], event_data))
            else:
                past_events.append(event_data)
        
        # Extract sorted upcoming events from heap
        sorted_upcoming = []
        while upcoming_heap:
            sorted_upcoming.append(heapq.heappop(upcoming_heap)[1])
            
        # Sort past events by date descending
        past_events.sort(key=lambda x: x['event_date'], reverse=True)
            
        return jsonify({
            "upcoming": sorted_upcoming,
            "past": past_events
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
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


@app.route("/api/ngo/partner", methods=["POST", "OPTIONS"])
def partner_with_ngo():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
        
    print("\n" + "="*50)
    print(f"NGO PARTNER REQUEST RECEIVED: {datetime.now()}")
    print(f"Origin: {request.headers.get('Origin')}")
    
    try:
        data = request.json
        print(f"Data: {data}")
    except Exception as e:
        print(f"Error parsing JSON: {str(e)}")
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

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

@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400
            
        # Check NGO accounts
        account = NGOAccount.query.filter_by(email=email).first()
        if account and account.is_active and check_password_hash(account.password_hash, password):
            # Get NGO info
            ngo = NGO.query.filter_by(email=email).first()
            return jsonify({
                "success": True,
                "message": "NGO Login successful",
                "user_type": "ngo",
                "ngo_id": ngo.ngo_id if ngo else None,
                "ngo_name": ngo.ngo_name if ngo else "NGO Partner",
                "email": email
            }), 200
            
        return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ngos", methods=["GET"])
def get_ngos():
    """Get all active NGO partners"""
    try:
        ngos = NGO.query.filter_by(is_active=True).order_by(NGO.created_at.desc()).all()
        return jsonify([ngo.to_dict() for ngo in ngos]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- PRACTICE SESSION LAUNCHER ----------------
@app.route("/api/practice/start", methods=["POST"])
def start_practice_session():
    """
    Launch the standalone Sign Language Detector UI application.
    This opens the OpenCV-based inference classifier with full features:
    - ADD LETTER, SPACE, CLEAR buttons
    - SPEAK (text-to-speech)
    - MIRROR mode
    - Sentence building
    """
    import subprocess
    import sys
    
    try:
        # Path to the ai_service directory
        ai_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai_service'))
        inference_script = os.path.join(ai_service_path, 'inference_classifier.py')
        
        if not os.path.exists(inference_script):
            return jsonify({
                "success": False,
                "error": f"Inference classifier not found at {inference_script}"
            }), 404
        
        # Launch the inference classifier as a separate process
        # Use the Python executable from the current environment
        python_exe = sys.executable
        
        # Start the process (non-blocking)
        process = subprocess.Popen(
            [python_exe, inference_script],
            cwd=ai_service_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        return jsonify({
            "success": True,
            "message": "Sign Language Detector UI launched successfully",
            "pid": process.pid
        }), 200
        
    except Exception as e:
        print(f"Error launching practice session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
