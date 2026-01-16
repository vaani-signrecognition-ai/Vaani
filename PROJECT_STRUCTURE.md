# Vaani Project Structure

```
Vaani/
│
├── 📄 README.md                          # Project documentation
├── 📄 LICENSE                            # Project license
├── 📄 .gitignore                         # Git ignore rules
├── 📄 .env.example                       # Environment variables template
├── 📄 check_data.py                      # Training data verification utility
├── 📄 realtime_predict.py                # Real-time ISL prediction script
├── 📄 train_model.py                     # Model training script
│
├── 📁 .venv/                             # Python Virtual Environment
│   ├── 📄 pyvenv.cfg                     # Virtual environment configuration
│   │
│   ├── 📁 Include/                       # C/C++ header files
│   │
│   ├── 📁 Lib/                           # Python libraries
│   │   └── 📁 site-packages/             # Installed Python packages
│   │       ├── 📦 flask/                 # Flask web framework
│   │       ├── 📦 tensorflow/            # TensorFlow ML framework
│   │       ├── 📦 torch/                 # PyTorch ML framework
│   │       ├── 📦 mediapipe/             # Hand tracking library
│   │       ├── 📦 numpy/                 # NumPy numerical computing
│   │       ├── 📦 opencv-python/         # OpenCV computer vision
│   │       ├── 📦 h5py/                  # HDF5 file support
│   │       ├── 📦 psycopg2/              # PostgreSQL adapter
│   │       ├── 📦 flask_cors/            # Flask CORS support
│   │       └── ... (other dependencies)
│   │
│   └── 📁 Scripts/                       # Virtual environment scripts
│       ├── 📄 activate                   # Bash activation script
│       ├── 📄 Activate.ps1               # PowerShell activation script
│       ├── 📄 python.exe                 # Python interpreter
│       ├── 📄 pip.exe                    # Package installer
│       └── ... (other executables)
│
├── 📁 backend/                           # Flask Backend Application
│   ├── 📄 app.py                         # Main Flask application
│   ├── 📄 config.py                      # Configuration settings
│   ├── 📄 requirements.txt               # Python dependencies
│   │
│   ├── 📁 models/                        # ML Models & Prediction
│   │   ├── 📄 __init__.py                # Package initializer
│   │   ├── 📄 alpha_predict.py           # Alphabet/number prediction module
│   │   ├── 📄 word_predict.py            # Word prediction module
│   │   ├── 📄 isl_alphanum_model.pth     # PyTorch alphabet model
│   │   ├── 📄 170-0.83.hdf5              # Keras word model
│   │   ├── 📄 words_model.h5             # Alternative word model
│   │   └── 📄 word_labels.txt            # Word class labels
│   │
│   ├── 📁 processed_keypoints/           # Training data (hand landmarks)
│   │   ├── 📁 0/ to 📁 9/                # Numbers 0-9
│   │   └── 📁 A/ to 📁 Z/                # Alphabets A-Z
│   │
│   ├── 📁 routes/                        # API Routes
│   │   └── 📄 __init__.py                # Package initializer
│   │
│   ├── 📁 static/                        # Static Assets
│   │   └── 📁 isl_words/                 # ISL word videos
│   │       └── 📄 README.md              # ISL dictionary guide
│   │
│   ├── 📁 templates/                     # HTML Templates
│   │   ├── 📄 index.html                 # Home page with camera recognition
│   │   ├── 📄 login.html                 # Login page
│   │   ├── 📄 events.html                # Events page
│   │   ├── 📄 admin_requests.html        # Admin panel for NGO requests
│   │   ├── 📄 404.html                   # Not found error page
│   │   ├── 📄 500.html                   # Server error page
│   │   │
│   │   ├── 📁 css/                       # Stylesheets
│   │   │   └── 📄 style.css              # Custom styles
│   │   │
│   │   └── 📁 js/                        # JavaScript files
│   │       ├── 📄 events.js              # Event management
│   │       ├── 📄 home.js                # Home page logic
│   │       ├── 📄 ngo.js                 # NGO functionality
│   │       └── 📄 recognize.js           # Recognition logic
│   │
│   └── 📁 utils/                         # Utility Functions
│       ├── 📄 __init__.py                # Package initializer
│       └── 📄 email_sender.py            # Email notification utility
│
├── 📁 database/                          # Database Scripts
│   ├── 📄 schema.sql                     # Database schema
│   └── 📄 sample_data.sql                # Sample/seed data
│
├── 📁 docs/                              # Documentation
│   └── 📄 ISL_DICTIONARY_GUIDE.md        # ISL dictionary guide
│
├── 📁 ml/                                # Machine Learning Components
│   ├── 📄 hand_tracking.py               # Hand tracking implementation
│   ├── 📄 predict.py                     # Prediction utilities
│   ├── 📄 model.h5                       # Trained model
│   └── 📄 labels.txt                     # Model labels
│
└── 📁 scripts/                           # Utility Scripts
    ├── 📄 create_folder_structure.ps1    # PowerShell setup script
│
├── 📁 database/                          # Database Setup
│   ├── 📄 README.md                      # Database documentation
│   ├── 📄 schema.sql                     # PostgreSQL schema
│   ├── 📄 setup_db.py                    # Database setup script
│   └── 📄 migrate_ngo_accounts.py        # NGO migration script
│
├── 📁 docs/                              # Documentation
│   ├── 📄 EMAIL_SETUP.md                 # Email configuration guide
│   └── 📄 ISL_DICTIONARY_GUIDE.md        # ISL dictionary usage guide
│
├── 📁 ml/                                # Machine Learning experiments
│
└── 📁 scripts/                           # Utility Scripts
    ├── 📄 create_folder_structure.ps1    # Project structure creator
    ├── 📄 load_isl_videos_to_db.py       # Database loader for videos
    ├── 📄 load_isl_videos.ipynb          # Jupyter notebook for video loading
    ├── 📄 test_email_config.py           # Email configuration test
    ├── 📄 test_word_model.py             # Word model test script
    └── 📄 test_image.jpg                 # Test image for API testing
```

## 🔑 Key Components

### Backend (Flask Application)
- **Main App**: Flask web server with REST API endpoints
- **ML Models**: TensorFlow/PyTorch models for ISL recognition
  - Alphabet/Number recognition (PyTorch + MediaPipe)
  - Word recognition (TensorFlow/Keras)
- **Database**: PostgreSQL integration for data storage
- **Authentication**: User authentication and authorization
- **Static Files**: ISL video dictionary organized alphabetically

### Machine Learning
- Hand tracking using MediaPipe
- Pre-trained models for sign language recognition
- Support for both alphabets/numbers and complete words
- Real-time prediction using webcam

### Frontend
- HTML templates with Bootstrap 5 styling
- Three.js 3D animated background
- JavaScript modules for:
  - Camera access and image capture
  - Real-time sign recognition
  - Text-to-speech functionality
  - Event management
  - NGO integration

### Database
- PostgreSQL schema for:
  - NGO accounts and requests
  - Sign dictionary
  - Events

## 📊 Project Statistics

- **Total Directories**: 10+ main folders
- **Python Modules**: 15+ files
- **HTML Templates**: 6 pages
- **JavaScript Files**: 4 modules
- **ML Models**: 3 trained models (.pth, .h5, .hdf5)
- **Database Scripts**: 4 SQL/Python files

## 🚀 API Endpoints

### Prediction Endpoints
- `POST /api/predict/alphabet` - Predict ISL alphabet/letter from image
- `POST /api/predict/word` - Predict ISL word from image

### Data Endpoints
- `GET /api/dictionary` - Get sign dictionary entries
- `GET /api/sign/search?word=<word>` - Search for specific signs
- `GET /api/ngos` - Get approved NGO list
- `GET /api/events` - Get events information

### NGO Endpoints
- `POST /api/ngo/partner` - Submit NGO partnership request
- `POST /api/ngo/login` - NGO account login
- `POST /api/ngo/post-event` - Post new event

### Admin Endpoints
- `GET /api/admin/ngo-requests` - Get all NGO requests
- `POST /api/admin/ngo-request/action` - Approve/reject NGO request

### Health Check
- `GET /api/health` - Backend health status
