import os
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config
from extensions import db

# ================= ENV =================
load_dotenv()
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# ================= APP FACTORY =================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    # ================= DATABASE =================
    with app.app_context():
        import models.database_models  # ✅ CORRECT WAY
        db.create_all()

    # ================= BLUEPRINTS =================
    from routes.ngo_routes import ngo_bp
    from routes.admin_routes import admin_bp
    from routes.user_routes import user_bp
    # from routes.auth import auth_bp  # only if exists

    app.register_blueprint(ngo_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    # app.register_blueprint(auth_bp)

    return app


# ================= CREATE APP =================
app = create_app()

# ================= FRONTEND =================
@app.route("/")
def serve_root():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_frontend(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# ================= HEALTH =================
@app.route("/ping")
def ping():
    return "FLASK ROUTES ARE WORKING"

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
