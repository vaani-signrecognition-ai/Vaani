# 📚 ISL Sign Dictionary System - Complete Documentation

## 🎯 Overview

A complete system to manage and display Indian Sign Language (ISL) videos with automatic database loading and web-based search.

---

## 📁 Project Structure

```
Vaani/
├── backend/
│   ├── app.py                           # Flask backend with API endpoints
│   ├── templates/
│   │   └── index.html                   # Frontend UI
│   └── static/
│       └── isl_words/                   # Video storage
│           ├── A/                       # Folder for words starting with A
│           │   ├── apple.mp4
│           │   ├── about.mp4
│           │   └── ...
│           ├── B/                       # Folder for words starting with B
│           ├── C/
│           └── ... (through Z)
├── scripts/
│   ├── load_isl_videos_to_db.py        # Python script for video loading
│   └── load_isl_videos.ipynb           # Google Colab notebook
└── database/
    └── schema.sql                       # Database schema
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE sign_dictionary (
    sign_id SERIAL PRIMARY KEY,
    word TEXT NOT NULL,
    starting_letter CHAR(1) NOT NULL,
    video_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(word, starting_letter)
);
```

**Fields:**
- `sign_id`: Auto-incrementing primary key
- `word`: The word being signed (extracted from filename)
- `starting_letter`: A-Z (folder name)
- `video_path`: Relative path to video file
- `created_at`: Timestamp of record creation

---

## 🚀 Setup Instructions

### Step 1: Prepare Your Videos

1. **Organize videos** in A-Z folders:
   ```
   ISL_Videos/
   ├── A/
   │   ├── apple.mp4
   │   ├── about.mp4
   ├── B/
   │   ├── book.mp4
   ```

2. **Naming convention**:
   - Filename = word (e.g., `apple.mp4`)
   - Lowercase recommended
   - No special characters

### Step 2: Upload to Google Drive

1. Create a folder in Google Drive (e.g., `ISL_Videos`)
2. Upload your A-Z folders there
3. Maintain the folder structure

### Step 3: Load Videos to Database

#### Option A: Google Colab (Recommended)

1. Open `scripts/load_isl_videos.ipynb` in Google Colab
2. Update the `DRIVE_BASE_PATH` variable:
   ```python
   DRIVE_BASE_PATH = "/content/drive/MyDrive/ISL_Videos"
   ```
3. Run all cells in order
4. Verify loading summary

#### Option B: Local Python Script

1. Install dependencies:
   ```bash
   pip install psycopg2-binary
   ```

2. Update `scripts/load_isl_videos_to_db.py`:
   - Set `DATABASE_URL`
   - Set `DRIVE_BASE_PATH` to your local folder

3. Run the script:
   ```bash
   python scripts/load_isl_videos_to_db.py
   ```

### Step 4: Copy Videos to Backend

After loading to database, copy videos to backend:

```bash
# Copy from Google Drive or local source
cp -r ISL_Videos/* backend/static/isl_words/
```

Or manually create the structure:
```
backend/static/isl_words/
├── A/
├── B/
├── C/
└── ... (through Z)
```

---

## 🔌 API Endpoints

### 1. Search All Signs (with optional filter)

**Endpoint:** `GET /api/dictionary`

**Parameters:**
- `search` (optional): Search term for word or letter

**Examples:**
```bash
# Get all signs (limit 100)
GET http://127.0.0.1:5000/api/dictionary

# Search for "apple"
GET http://127.0.0.1:5000/api/dictionary?search=apple

# Get all words starting with "A"
GET http://127.0.0.1:5000/api/dictionary?search=A
```

**Response:**
```json
[
  {
    "sign_id": 1,
    "word": "apple",
    "starting_letter": "A",
    "video_path": "/static/isl_words/A/apple.mp4"
  }
]
```

### 2. Search Specific Sign

**Endpoint:** `GET /api/sign/search`

**Parameters:**
- `word` (required): Exact word to search

**Example:**
```bash
GET http://127.0.0.1:5000/api/sign/search?word=apple
```

**Response:**
```json
{
  "word": "apple",
  "letter": "A",
  "video": "/static/isl_words/A/apple.mp4"
}
```

### 3. Get Sign by ID

**Endpoint:** `GET /api/dictionary/<sign_id>`

**Example:**
```bash
GET http://127.0.0.1:5000/api/dictionary/1
```

**Response:**
```json
{
  "sign_id": 1,
  "word": "apple",
  "starting_letter": "A",
  "video_path": "/static/isl_words/A/apple.mp4"
}
```

---

## 🌐 Frontend UI

The Sign Dictionary section in `index.html` provides:

1. **Search Box**: Enter word to search
2. **Search Button**: Triggers search
3. **Video Player**: Displays ISL video if found
4. **Result Display**: Shows word, letter badge, and video

### Usage:

1. Navigate to **Dictionary** section
2. Type a word (e.g., "apple")
3. Click **Search**
4. Video plays automatically

---

## 🧪 Testing

### Test API Endpoints

```bash
# Test health check
curl http://127.0.0.1:5000/api/health

# Test dictionary search
curl "http://127.0.0.1:5000/api/dictionary?search=apple"

# Test specific sign search
curl "http://127.0.0.1:5000/api/sign/search?word=apple"
```

### Verify Database

```sql
-- Check total signs loaded
SELECT COUNT(*) FROM sign_dictionary;

-- View sample records
SELECT * FROM sign_dictionary LIMIT 10;

-- Search for specific word
SELECT * FROM sign_dictionary WHERE word = 'apple';

-- Get all words starting with A
SELECT * FROM sign_dictionary WHERE starting_letter = 'A';
```

---

## 📊 Google Colab Notebook Features

The `load_isl_videos.ipynb` notebook includes:

1. ✅ **Google Drive mounting**
2. ✅ **PostgreSQL connection**
3. ✅ **Table creation**
4. ✅ **A-Z folder traversal**
5. ✅ **Video file detection**
6. ✅ **Word extraction from filename**
7. ✅ **Batch insertion with conflict handling**
8. ✅ **Progress tracking**
9. ✅ **Summary statistics**
10. ✅ **Verification queries**

### Notebook Cells:

1. **Install packages**: `psycopg2-binary`
2. **Mount Drive**: Connect to Google Drive
3. **Configuration**: Set DATABASE_URL and path
4. **Verify folders**: Check A-Z structure
5. **Create table**: Initialize database
6. **Load functions**: Helper functions
7. **Main loading**: Process all videos
8. **Verify data**: Check loaded records

---

## 🎥 Video Requirements

- **Format**: MP4 (H.264 codec recommended)
- **Resolution**: 640x480 or higher
- **Duration**: 3-10 seconds
- **File size**: < 5MB per video recommended
- **Content**: Clear ISL sign demonstration
- **Background**: Plain or neutral
- **Lighting**: Good visibility

---

## 🔧 Troubleshooting

### Issue: Videos not loading

**Solution:**
- Check folder structure (A-Z folders)
- Verify video filenames (no special chars)
- Check DATABASE_URL connection
- Run Colab notebook again

### Issue: Video not playing in browser

**Solution:**
- Ensure MP4 format with H.264 codec
- Check video file exists in `static/isl_words/`
- Verify video_path in database
- Check browser console for errors

### Issue: Database connection failed

**Solution:**
- Verify DATABASE_URL is correct
- Check PostgreSQL credentials
- Ensure database server is running
- Test connection with psql client

---

## 📈 Scalability

- Database can handle **10,000+** signs efficiently
- Add indexes for faster searches:
  ```sql
  CREATE INDEX idx_word ON sign_dictionary(word);
  CREATE INDEX idx_letter ON sign_dictionary(starting_letter);
  ```

---

## 🎉 Summary

✅ **Complete system** for ISL video management  
✅ **Automatic loading** from Google Drive  
✅ **RESTful API** endpoints  
✅ **Web UI** with video player  
✅ **PostgreSQL** database backend  
✅ **Google Colab** notebook for easy loading  

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review terminal/console logs
3. Verify database records
4. Test API endpoints individually

**Database Connection:**
```
postgresql://vaanidb_user:OFQoXaRdKpYS0IiCYeTHrejZ39jsvqKm@dpg-d5dbsv2li9vc73dfgio0-a.virginia-postgres.render.com/vaanidb
```
