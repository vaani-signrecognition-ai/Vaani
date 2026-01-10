"""
Google Colab Script to Load ISL Videos into PostgreSQL Database
=================================================================

This script:
1. Mounts Google Drive
2. Traverses A-Z folders containing ISL sign videos
3. Extracts word from filename and folder letter
4. Inserts into PostgreSQL sign_dictionary table

Usage in Google Colab:
- Upload this script
- Set your DATABASE_URL
- Run the script
"""

import os
import psycopg2
from psycopg2 import sql
import re
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================
DATABASE_URL = "postgresql://vaanidb_user:OFQoXaRdKpYS0IiCYeTHrejZ39jsvqKm@dpg-d5dbsv2li9vc73dfgio0-a.virginia-postgres.render.com/vaanidb"

# Base path in Google Drive where A-Z folders are located
# Adjust this path based on your Google Drive structure
DRIVE_BASE_PATH = "/content/drive/MyDrive/ISL_Videos"  # Change this to your actual path

# ============================================
# DATABASE CONNECTION
# ============================================
def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# ============================================
# CREATE TABLE IF NOT EXISTS
# ============================================
def create_table():
    """Create sign_dictionary table if it doesn't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sign_dictionary (
                sign_id SERIAL PRIMARY KEY,
                word TEXT NOT NULL,
                starting_letter CHAR(1) NOT NULL,
                video_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(word, starting_letter)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table created/verified successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

# ============================================
# EXTRACT WORD FROM FILENAME
# ============================================
def extract_word_from_filename(filename):
    """
    Extract word from video filename
    Example: 'apple.mp4' -> 'apple'
    """
    # Remove extension
    word = os.path.splitext(filename)[0]
    # Clean up: remove numbers, special chars, convert to lowercase
    word = re.sub(r'[^a-zA-Z\s]', '', word).strip().lower()
    return word

# ============================================
# INSERT VIDEO INTO DATABASE
# ============================================
def insert_video(word, starting_letter, video_path):
    """Insert video record into database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sign_dictionary (word, starting_letter, video_path)
            VALUES (%s, %s, %s)
            ON CONFLICT (word, starting_letter) DO UPDATE 
            SET video_path = EXCLUDED.video_path
        """, (word, starting_letter.upper(), video_path))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error inserting {word}: {e}")
        return False

# ============================================
# TRAVERSE AND LOAD VIDEOS
# ============================================
def load_videos_from_drive():
    """
    Main function to traverse A-Z folders and load videos
    """
    print("=" * 60)
    print("🚀 Starting ISL Video Loading Process")
    print("=" * 60)
    
    # Check if base path exists
    if not os.path.exists(DRIVE_BASE_PATH):
        print(f"❌ Error: Base path not found: {DRIVE_BASE_PATH}")
        print("Please mount Google Drive first and update DRIVE_BASE_PATH")
        return
    
    total_videos = 0
    successful = 0
    failed = 0
    
    # Iterate through A-Z folders
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        folder_path = os.path.join(DRIVE_BASE_PATH, letter)
        
        if not os.path.exists(folder_path):
            print(f"⚠️  Folder {letter} not found, skipping...")
            continue
        
        print(f"\n📁 Processing folder: {letter}")
        
        # Get all .mp4 files in the folder
        video_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
        
        if not video_files:
            print(f"   No videos found in {letter}")
            continue
        
        print(f"   Found {len(video_files)} videos")
        
        # Process each video
        for video_file in video_files:
            total_videos += 1
            
            # Extract word from filename
            word = extract_word_from_filename(video_file)
            
            if not word:
                print(f"   ⚠️  Skipping invalid filename: {video_file}")
                failed += 1
                continue
            
            # Construct video path (relative path for web serving)
            video_path = f"/static/isl_words/{letter}/{video_file}"
            
            # Insert into database
            if insert_video(word, letter, video_path):
                successful += 1
                print(f"   ✅ {word} -> {video_path}")
            else:
                failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 LOADING SUMMARY")
    print("=" * 60)
    print(f"Total videos processed: {total_videos}")
    print(f"✅ Successfully loaded: {successful}")
    print(f"❌ Failed: {failed}")
    print("=" * 60)

# ============================================
# MOUNT GOOGLE DRIVE (Colab Only)
# ============================================
def mount_drive():
    """Mount Google Drive in Colab"""
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print("✅ Google Drive mounted successfully")
        return True
    except ImportError:
        print("ℹ️  Not running in Google Colab, skipping drive mount")
        return True
    except Exception as e:
        print(f"❌ Error mounting drive: {e}")
        return False

# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  ISL Video Database Loader for VAANI                     ║
    ║  Loads A-Z folders of ISL sign videos into PostgreSQL   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Mount Google Drive (if in Colab)
    if not mount_drive():
        print("❌ Failed to mount drive. Exiting...")
        exit(1)
    
    # Step 2: Create table
    if not create_table():
        print("❌ Failed to create table. Exiting...")
        exit(1)
    
    # Step 3: Load videos
    load_videos_from_drive()
    
    print("\n🎉 Process completed!")
    print("You can now use the Sign Dictionary in your web application.")
