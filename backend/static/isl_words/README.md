# ISL Words Video Storage

## Structure

```
static/
└── isl_words/
    ├── A/
    │   ├── apple.mp4
    │   ├── about.mp4
    │   └── ...
    ├── B/
    │   ├── book.mp4
    │   ├── boy.mp4
    │   └── ...
    ├── C/
    └── ... (Z)
```

## Instructions

1. **Create folders A-Z** in this directory
2. **Place video files** (.mp4) in corresponding letter folders
3. **Naming convention**: 
   - Filename = word (e.g., `apple.mp4`, `book.mp4`)
   - Lowercase recommended
   - No special characters

## Loading Videos to Database

After placing your videos:

1. Open `scripts/load_isl_videos.ipynb` in Google Colab
2. Upload your videos to Google Drive (maintain A-Z folder structure)
3. Run the Colab notebook to populate the database
4. Videos will be accessible via the Sign Dictionary UI

## Video Requirements

- **Format**: MP4
- **Resolution**: 640x480 or higher recommended
- **Duration**: 3-10 seconds per sign
- **Content**: Clear ISL sign demonstration

## Example

```
isl_words/
├── A/
│   ├── apple.mp4      → Word: "apple"
│   ├── about.mp4      → Word: "about"
│   └── airplane.mp4   → Word: "airplane"
├── B/
│   ├── book.mp4       → Word: "book"
│   └── beautiful.mp4  → Word: "beautiful"
```

## API Access

Once loaded, videos are accessible via:
- `GET /api/sign/search?word=apple`
- Returns: `{"word": "apple", "video": "/static/isl_words/A/apple.mp4"}`
