import os
import pickle
import mediapipe as mp
import cv2
import numpy as np

from pathlib import Path

# Use absolute paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / 'data'
OUTPUT_FILE = SCRIPT_DIR / 'data.pickle'

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

data = []
labels = []

if not DATA_DIR.exists():
    print(f"Error: Data directory not found at {DATA_DIR}")
    exit(1)

for dir_ in os.listdir(DATA_DIR):
    # Skip hidden files/folders
    if dir_.startswith('.'):
        continue
        
    dir_path = os.path.join(DATA_DIR, dir_)
    if not os.path.isdir(dir_path):
        continue

    print(f"Processing category: {dir_}")
    for img_path in os.listdir(dir_path):
        data_aux = []
        x_ = []
        y_ = []

        img = cv2.imread(os.path.join(dir_path, img_path))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = hands.process(img_rgb)
        if results.multi_hand_landmarks:
            # We take the first hand detected (or process both if your model expects it)
            # To be consistent with detector.py padding, we'll process one hand and pad
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)

                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))

                # Pad to 84 features (consistent with detector.py)
                if len(data_aux) == 42:
                    data_aux.extend([0.0] * 42)
                
                if len(data_aux) == 84:
                    data.append(data_aux)
                    labels.append(dir_)
                
                # If you only want one hand per image in training
                break 

with open(OUTPUT_FILE, 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)

print(f"Dataset created with {len(data)} samples across {len(set(labels))} categories at {OUTPUT_FILE}")
