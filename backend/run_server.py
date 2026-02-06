"""
VAANI Server Launcher
Run this to start the Flask development server
"""
import os
import sys

# Set working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite:///vaani.db'

print("=" * 50)
print("🚀 Starting VAANI Server...")
print("=" * 50)

try:
    from app import app
except Exception as e:
    print(f"❌ Error importing app: {e}")
    raise

print("📍 Server URL: http://127.0.0.1:5000")
print("📍 Admin Panel: http://127.0.0.1:5000/admin")
print("=" * 50)

if __name__ == "__main__":
    app.run(debug=True)
