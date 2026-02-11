import sqlite3
import os

db_path = r"c:\Users\Admn\Documents\GitHub\Vaani\backend\instance\vaani.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if image_path already exists
    cursor.execute("PRAGMA table_info(sign_dictionary)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "image_path" not in columns:
        print("Adding image_path column to sign_dictionary table...")
        cursor.execute("ALTER TABLE sign_dictionary ADD COLUMN image_path VARCHAR(255)")
        conn.commit()
        print("Done.")
    else:
        print("image_path column already exists.")
        
    # Also fix video_path to be nullable if it's not
    # SQLite doesn't support ALTER TABLE ALTER COLUMN well, but we can try making it nullable in SQLAlchemy model (already done)
    # Existing data might cause issues if we try to enforce non-null later.
    
    conn.close()
else:
    print(f"Database not found at {db_path}")
