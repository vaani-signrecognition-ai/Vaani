import os
import shutil

# Base directory for the project
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Source and destination directories
data_dir = os.path.join(base_dir, "ai_service", "data")
dest_dir = os.path.join(base_dir, "backend", "templates", "frontend", "assets", "dictionary")

# Create destination directory if it doesn't exist
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
    print(f"Created directory: {dest_dir}")

# Iterate through subdirectories in data_dir
for folder_name in os.listdir(data_dir):
    folder_path = os.path.join(data_dir, folder_name)
    
    if os.path.isdir(folder_path):
        # Look for the first jpg image in the folder
        images = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
        
        if images:
            # Sort to be deterministic (pick 0.jpg if it exists, else the first one)
            if '0.jpg' in images:
                src_image = '0.jpg'
            else:
                src_image = sorted(images)[0]
                
            src_path = os.path.join(folder_path, src_image)
            dest_filename = f"{folder_name}.jpg"
            dest_path = os.path.join(dest_dir, dest_filename)
            
            # Copy and rename image
            shutil.copy2(src_path, dest_path)
            print(f"Copied {src_path} -> {dest_path}")
        else:
            print(f"No images found in {folder_path}")
print("Finished copying images.")
