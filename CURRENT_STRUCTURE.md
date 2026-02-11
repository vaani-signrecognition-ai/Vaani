# Vaani - Updated Project Structure

```
Vaani/
│
├── 📄 .env.example                      # Environment variables template
├── 📄 .gitignore                        # Git ignore rules
├── 📄 README.md                         # Main readme
│
├── 📁 .venv/                            # Python Virtual Environment (root)
│
├── 📁 ai_service/                       # 🤖 AI/ML Service (STANDALONE)
│   ├── 📄 ai_app.py                     # ⭐ Flask API for AI predictions
│   ├── 📄 requirements.txt              # AI service dependencies
│   ├── 📄 model.p                       # Trained model (pickle)
│   ├── 📄 sign_predict.py               # Sign prediction module
│   ├── 📄 word_predict.py               # Word prediction module
│   ├── 📄 inference_classifier.py       # Realtime inference script
│   ├── 📄 hand_landmarker.task          # MediaPipe hand model
│   ├── 📄 data.pickle                   # Processed training data
│   ├── 📄 train_classifier.py           # Model training script
│   ├── 📄 create_dataset.py             # Dataset creation
│   ├── 📄 collect_imgs.py               # Image collection
│   ├── 📄 collect_labels.py             # Label collection
│   ├── 📄 check_dataset.py              # Dataset verification
│   ├── 📄 License                       # License file
│   ├── 📄 README.md                     # AI documentation
│   └── 📁 data/                         # Training images (A-Z folders)
│       ├── 📁 A/ to Z/                  # Images for each letter
│       └── 📁 0/ to 9/                  # Images for numbers
│
├── 📁 backend/                          # 🌐 Flask Backend (Web + DB)
│   ├── 📄 app.py                        # Main Flask application
│   ├── 📄 run_server.py                 # Server startup script
│   ├── 📄 config.py                     # Configuration settings
│   ├── 📄 extensions.py                 # Flask extensions
│   ├── 📄 .env                          # Environment variables (local)
│   ├── 📄 requirements.txt              # Backend dependencies
│   │
│   ├── 📁 instance/                     # Instance folder
│   │   └── 📄 vaani.db                  # SQLite database
│   │
│   ├── 📁 models/                       # Database Models ONLY
│   │   ├── 📄 __init__.py               # Package initializer
│   │   └── 📄 database_models.py        # SQLAlchemy models
│   │
│   ├── 📁 routes/                       # API Routes
│   │
│   ├── 📁 templates/                    # HTML Templates
│   │   ├── 📄 admin_requests.html       # Admin panel
│   │   ├── 📄 events.html               # Events page
│   │   ├── 📄 old_index.html            # Old homepage
│   │   │
│   │   ├── 📁 css/                      # Stylesheets
│   │   ├── 📁 js/                       # JavaScript files
│   │   │
│   │   └── 📁 new_frontend/             # ⭐ New Frontend Design
│   │       ├── 📄 index.html            # Main homepage
│   │       ├── 📄 about.html            # About page
│   │       ├── 📄 contact.html          # Contact page
│   │       ├── 📄 dictionary.html       # ISL dictionary
│   │       ├── 📄 events.html           # Events page
│   │       ├── 📄 loading.html          # Loading page
│   │       ├── 📄 ngo-partners.html     # NGO partners
│   │       ├── 📄 style.css             # Frontend CSS
│   │       └── 📁 js/                   # Frontend JS
│   │
│   └── 📁 utils/                        # Utility Functions
│       ├── 📄 __init__.py               # Package initializer
│       └── 📄 email_sender.py           # Email utility
│
├── 📁 database/                         # 📊 Database Scripts
│   ├── 📄 README.md                     # Database documentation
│   ├── 📄 schema.sql                    # PostgreSQL schema
│   ├── 📄 setup_db.py                   # Database setup
│   └── 📄 migrate_ngo_accounts.py       # Migration script
│
├── 📁 docs/                             # 📚 Documentation
│   ├── 📄 EMAIL_SETUP.md                # Email config guide
│   └── 📄 ISL_DICTIONARY_GUIDE.md       # ISL dictionary guide
│
├── 📁 instance/                         # Flask instance folder
│   └── 📄 vaani.db                      # SQLite database
│
└── 📁 scripts/                          # 🔧 Utility Scripts
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│              (backend/templates/new_frontend)               │
│                     HTML + CSS + JS                         │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP Requests
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask)                          │
│                   (backend/app.py)                          │
│  • Serves frontend pages                                    │
│  • Handles user authentication                              │
│  • Manages database operations                              │
│  • Routes API requests to AI Service                        │
└────────────────────┬───────────────────┬────────────────────┘
                     │                   │
         Database    │                   │ HTTP/Internal Call
                     ▼                   ▼
         ┌───────────────────┐  ┌─────────────────────────────┐
         │    SQLite/        │  │      AI SERVICE (Flask)     │
         │    PostgreSQL     │  │    (ai_service/ai_app.py)   │
         │                   │  │                             │
         │  • Users          │  │  • Sign prediction API      │
         │  • NGOs           │  │  • MediaPipe processing     │
         │  • Events         │  │  • ML model inference       │
         │  • Dictionary     │  │  • Runs on port 5001        │
         └───────────────────┘  └─────────────────────────────┘
```

## 🚀 How to Run

### 1. Backend Server (Port 5000)
```bash
cd backend
python run_server.py
```

### 2. AI Service (Port 5001)
```bash
cd ai_service
python ai_app.py
```

### 3. Train New Model
```bash
cd ai_service
python train_classifier.py
```

### 4. Realtime Inference (Webcam)
```bash
cd ai_service
python inference_classifier.py
```

## 📡 AI Service API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict/sign` | Predict sign from base64 image |
| GET | `/api/predict/signs` | Get list of available signs |
| GET | `/api/health` | Health check |

## 🔑 Key Technologies

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python) |
| **AI Service** | Flask + MediaPipe + scikit-learn |
| **Database** | SQLite / PostgreSQL |
| **Frontend** | HTML, CSS, JavaScript |
| **ML Model** | Random Forest (pickle) |
