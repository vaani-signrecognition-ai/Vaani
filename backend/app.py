from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from datetime import datetime
import random
import string
from routes import auth
from werkzeug.security import generate_password_hash, check_password_hash
from utils.email_sender import send_approval_email, send_rejection_email
from models.word_predict import predict_word


app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

# ---------------- DB CONNECTION ----------------
def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

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

# ---------------- SERVE JS/CSS FROM TEMPLATES ----------------
@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(app.template_folder, 'js'), filename)

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(app.template_folder, 'css'), filename)

# ---------------- HEALTH CHECK ----------------
@app.route("/api/health")
def health():
    return jsonify({"message": "VAANI backend connected to PostgreSQL"})

@app.route("/api/ngos", methods=["GET"])
def get_ngos():
    try:
        conn = get_db()
        cur = conn.cursor()

        # Use the approved_ngos view or join tables
        cur.execute("""
            SELECT 
                n.ngo_id,
                nr.org_name,
                nr.contact_person,
                nr.phone,
                nr.email,
                nr.description,
                nr.city,
                nr.status,
                n.created_at
            FROM ngo_accounts n
            INNER JOIN ngo_requests nr ON n.request_id = nr.request_id
            WHERE nr.status = 'APPROVED' AND n.is_active = TRUE
            ORDER BY n.created_at DESC
        """)

        ngos = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(ngos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dictionary", methods=["GET"])
def get_dictionary():
    try:
        search = request.args.get('search', '').strip()
        
        conn = get_db()
        cur = conn.cursor()

        if search:
            # Search by word or starting letter
            cur.execute("""
                SELECT sign_id, word, starting_letter, video_path
                FROM sign_dictionary
                WHERE LOWER(word) LIKE LOWER(%s) OR LOWER(starting_letter) = LOWER(%s)
                ORDER BY word
            """, (f'%{search}%', search[0] if search else ''))
        else:
            # Get all signs
            cur.execute("""
                SELECT sign_id, word, starting_letter, video_path
                FROM sign_dictionary
                ORDER BY word
                LIMIT 100
            """)

        signs = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(signs), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sign/search", methods=["GET"])
def search_sign():
    """
    Search for a specific sign by word
    Usage: GET /api/sign/search?word=apple
    Returns: { "word": "apple", "video": "/static/isl_words/A/apple.mp4" }
    """
    try:
        word = request.args.get('word', '').strip().lower()
        
        if not word:
            return jsonify({"error": "Word parameter is required"}), 400
        
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT word, starting_letter, video_path
            FROM sign_dictionary
            WHERE LOWER(word) = LOWER(%s)
            LIMIT 1
        """, (word,))

        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return jsonify({
                "word": result['word'],
                "letter": result['starting_letter'],
                "video": result['video_path']
            }), 200
        else:
            return jsonify({"error": "Sign not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dictionary/<int:sign_id>", methods=["GET"])
def get_sign(sign_id):
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT sign_id, word, starting_letter, video_path
            FROM sign_dictionary
            WHERE sign_id = %s
        """, (sign_id,))

        sign = cur.fetchone()
        cur.close()
        conn.close()

        if sign:
            return jsonify(sign), 200
        else:
            return jsonify({"error": "Sign not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT e.event_id, e.title, e.description,
                   e.event_date, e.location,
                   n.ngo_name
            FROM events e
            LEFT JOIN ngos n ON e.ngo_id = n.ngo_id
            ORDER BY e.event_date DESC
        """)

        events = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(events), 200

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
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO events
            (ngo_id, title, description, event_date, location)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            ngo_id,
            title,
            description,
            event_date,
            location
        ))

        conn.commit()
        cur.close()
        conn.close()

        print("Event posted successfully")
        return jsonify({
            "message": "Event posted successfully"
        }), 201

    except Exception as e:
        print(f"Error posting event: {str(e)}")
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
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
        conn = get_db()
        cur = conn.cursor()

        # First, let's check if the table exists and get its columns
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ngo_requests'
        """)
        columns = cur.fetchall()
        print("Available columns in ngo_requests:", columns)

        query = """
        INSERT INTO ngo_requests
        (org_name, contact_person, email, phone, city, purpose, description, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        print(f"Attempting to insert: {org_name}, {contact_person}, {email}, {phone}, {city}, {purpose}, {description}")

        cur.execute(query, (
            org_name,
            contact_person,
            email,
            phone,
            city,
            purpose,
            description,
            "PENDING"
        ))

        conn.commit()
        cur.close()
        conn.close()

        print("Partnership request inserted successfully")
        return jsonify({
            "success": True,
            "message": "NGO partnership request submitted successfully"
        }), 201

    except Exception as e:
        print(f"Error in partner_with_ngo: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/admin/ngo-requests", methods=["GET"])
def get_ngo_requests():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT request_id, org_name, contact_person, phone,
                   email, purpose, description, city, status, submitted_at
            FROM ngo_requests
            ORDER BY submitted_at DESC
        """)

        requests = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(requests), 200

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
        conn = get_db()
        cur = conn.cursor()

        # Update request status
        cur.execute("""
            UPDATE ngo_requests
            SET status = %s
            WHERE request_id = %s
        """, (action, request_id))

        # If approved → create NGO account
        if action == "APPROVED":
            cur.execute("""
                SELECT email, org_name FROM ngo_requests WHERE request_id = %s
            """, (request_id,))
            result = cur.fetchone()
            email = result['email']
            org_name = result['org_name']

            temp_password = "VAANI@" + ''.join(
                random.choices(string.digits, k=4)
            )

            password_hash = generate_password_hash(temp_password)

            cur.execute("""
                INSERT INTO ngo_accounts (request_id, email, password_hash, is_active)
                VALUES (%s, %s, %s, TRUE)
            """, (request_id, email, password_hash))

            conn.commit()
            cur.close()
            conn.close()

            # Send approval email
            send_approval_email(email, org_name, temp_password)

            return jsonify({
                "message": "NGO approved and account created",
                "temp_password": temp_password   # demo purpose
            }), 200

        conn.commit()
        cur.close()
        conn.close()
        
        # Send rejection email if rejected
        if action == "REJECTED":
            cur.execute("""
                SELECT email, org_name FROM ngo_requests WHERE request_id = %s
            """, (request_id,))
            result = cur.fetchone()
            if result:
                send_rejection_email(result['email'], result['org_name'])
        
        return jsonify({"message": "NGO request rejected"}), 200

    except Exception as e:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({"error": str(e)}), 500


@app.route("/api/ngo/login", methods=["POST"])
def ngo_login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT ngo_id, password_hash
            FROM ngo_accounts
            WHERE email = %s
        """, (email,))

        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        ngo_id, password_hash = user

        if check_password_hash(password_hash, password):
            return jsonify({
                "message": "Login successful",
                "ngo_id": ngo_id
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

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

# ---------------- ERROR HANDLERS ----------------
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors - page not found"""
    # Check if request is for API endpoint
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Endpoint not found",
            "message": "The requested API endpoint does not exist",
            "status": 404
        }), 404
    # Return HTML template for regular pages
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors - internal server error"""
    # Check if request is for API endpoint
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "status": 500
        }), 500
    # Return HTML template for regular pages
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
