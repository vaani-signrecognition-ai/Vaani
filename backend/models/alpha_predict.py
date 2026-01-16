"""
Alphabet/Number prediction using PyTorch model with MediaPipe
"""
import numpy as np
import cv2
import torch
import torch.nn as nn
import os

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "isl_alphanum_model.pth")

# ---------------- MODEL DEFINITION ----------------
class ISLModel(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(126, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.net(x)

# ---------------- LOAD MODEL ----------------
try:
    checkpoint = torch.load(MODEL_PATH, map_location='cpu')
    CLASSES = checkpoint['classes']
    model = ISLModel(num_classes=len(CLASSES))
    model.load_state_dict(checkpoint['model_state'])
    model.eval()
    print("✓ Alphabet model loaded successfully")
except Exception as e:
    print(f"✗ Failed to load alphabet model: {e}")
    raise e

# ---------------- MEDIAPIPE SETUP ----------------
import mediapipe as mp
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5
)

def extract_hand_landmarks(results):
    """Extract 126 features (21 landmarks * 3 coords * 2 hands) - normalized"""
    left_hand = np.zeros(63)
    right_hand = np.zeros(63)
    
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            
            # Normalize relative to wrist (landmark 0)
            wrist = landmarks[0]
            landmarks_normalized = landmarks - wrist
            hand_data = landmarks_normalized.flatten()
            
            # MediaPipe returns mirrored labels, so swap them
            if handedness.classification[0].label == 'Right':
                left_hand = hand_data
            else:
                right_hand = hand_data
    
    return np.concatenate([left_hand, right_hand])

# ---------------- PREDICT FUNCTION ----------------
def predict_alphabet(image_bytes):
    """
    Input: image bytes
    Output: (letter, confidence)
    """
    # Decode image
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        return "invalid_image", 0.0

    # Convert BGR to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Process with MediaPipe
    results = hands.process(img_rgb)
    
    if not results.multi_hand_landmarks:
        return "no_hand_detected", 0.0
    
    # Extract features
    features = extract_hand_landmarks(results)
    features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
    
    # Prediction
    with torch.no_grad():
        output = model(features_tensor)
        probs = torch.softmax(output, dim=1)
        confidence, pred_idx = torch.max(probs, dim=1)
        
        confidence = confidence.item()
        letter = CLASSES[pred_idx.item()]
    
    # Confidence threshold
    if confidence < 0.5:
        return "unknown", confidence

    return letter, confidence
