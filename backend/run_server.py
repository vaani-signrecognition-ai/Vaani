"""
VAANI Server Launcher
Run this to start the Flask development server
"""
import os
import sys

# Set working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables (default to SQLite if not provided)
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///vaani.db'

print("=" * 50)
print("Starting VAANI Server...")
print("=" * 50)
print("[*] Server URL: http://127.0.0.1:5000")
print("[*] Admin Panel: http://127.0.0.1:5000/admin")
print("=" * 50)
print()

# Import and run the Flask app
try:
    from app import app
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
except KeyboardInterrupt:
    print("\n\nServer stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\nError starting server: {e}")
    sys.exit(1)
