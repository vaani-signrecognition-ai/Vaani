# VAANI - Indian Sign Language Recognition Platform

A web-based platform for Indian Sign Language (ISL) recognition, NGO partnerships, and community events.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Git

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Vaani
```

2. **Create a virtual environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Set up environment variables**
   
   Copy the example environment file:
```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

   The default `.env` file should work out of the box with SQLite:
```env
DATABASE_URL=sqlite:///vaani.db
SECRET_KEY=vaani-secret-key
DEBUG=True
FLASK_ENV=development
```

5. **Run the server**
```bash
python run_server.py
```

Or directly:
```bash
python app.py
```

6. **Access the application**
   - Main app: http://127.0.0.1:5000
   - Admin panel: http://127.0.0.1:5000/admin

## 📧 Email Configuration (Optional)

To enable email notifications for NGO approvals:

1. Get a Gmail App Password:
   - Enable 2FA on your Gmail account
   - Go to https://myaccount.google.com/apppasswords
   - Generate an app password

2. Update `.env` file:
```env
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-char-app-password
```

## 🗂️ Project Structure

```
Vaani/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── run_server.py          # Server launcher
│   ├── config.py              # Configuration
│   ├── extensions.py          # Flask extensions
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (create this)
│   ├── models/
│   │   └── database_models.py # SQLAlchemy models
│   ├── templates/             # HTML templates
│   ├── utils/
│   │   └── email_sender.py   # Email utilities
│   └── instance/
│       └── vaani.db          # SQLite database (auto-created)
└── docs/                     # Documentation
```

## 🛠️ Features

- 🤝 NGO Partnership Management
- 📅 Community Events
- 🔤 ISL Dictionary
- 🎓 Sign Language Recognition (ML features)
- ✉️ Email Notifications

## 🐛 Troubleshooting

### Database automatically creates
The SQLite database (`vaani.db`) is created automatically when you first run the server.

### Port already in use
If port 5000 is busy, stop other Flask apps or change the port in `app.py`:
```python
app.run(debug=True, host="127.0.0.1", port=5001)  # Use different port
```

### ML Models (Optional)
The machine learning features are optional. If you don't need them, you can skip installing:
- tensorflow
- torch
- opencv-python
- mediapipe

Just comment them out in `requirements.txt` before installing.

## 📝 License

MIT License

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
