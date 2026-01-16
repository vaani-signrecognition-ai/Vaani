"""
Real-time ISL Alphabet Recognition using trained PyTorch model
Uses MediaPipe for hand landmark detection
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import mediapipe as mp

# ================== MODEL DEFINITION ==================
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

# ================== LOAD MODEL ==================
MODEL_PATH = r"C:\Users\Admn\Documents\GitHub\Vaani\backend\models\isl_alphanum_model.pth"

print("Loading model...")
checkpoint = torch.load(MODEL_PATH, map_location='cpu')
classes = checkpoint['classes']
print(f"Classes: {classes}")

model = ISLModel(num_classes=len(classes))
model.load_state_dict(checkpoint['model_state'])
model.eval()
print("✓ Model loaded!")

# ================== MEDIAPIPE SETUP ==================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def extract_hand_landmarks(results):
    """Extract 126 features (21 landmarks * 3 coords * 2 hands) - normalized"""
    left_hand = np.zeros(63)
    right_hand = np.zeros(63)
    
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Get raw landmarks
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            
            # Normalize relative to wrist (landmark 0)
            wrist = landmarks[0]
            landmarks_normalized = landmarks - wrist
            
            hand_data = landmarks_normalized.flatten()
            
            # Note: MediaPipe returns mirrored labels, so swap them
            if handedness.classification[0].label == 'Right':
                left_hand = hand_data
            else:
                right_hand = hand_data
    
    return np.concatenate([left_hand, right_hand])

# ================== CAMERA FEED ==================
print("\n" + "=" * 50)
print("Real-time ISL Alphabet Recognition")
print("=" * 50)
print("Show hand signs to the camera!")
print("Press 'Q' to quit")
print("=" * 50 + "\n")

cap = cv2.VideoCapture(0)
prediction = ""
confidence = 0.0

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # MediaPipe detection
        results = hands.process(image)
        
        # Convert back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Extract features and predict
            features = extract_hand_landmarks(results)
            features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
            
            with torch.no_grad():
                output = model(features_tensor)
                probs = torch.softmax(output, dim=1)
                conf, pred_idx = torch.max(probs, dim=1)
                
                prediction = classes[pred_idx.item()]
                confidence = conf.item()
        
        # Display prediction
        if prediction and confidence > 0.5:
            # Draw background rectangle
            cv2.rectangle(image, (10, 10), (300, 100), (0, 0, 0), -1)
            cv2.rectangle(image, (10, 10), (300, 100), (0, 255, 0), 2)
            
            # Display text
            cv2.putText(image, f"Sign: {prediction}", (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.putText(image, f"Conf: {confidence:.1%}", (20, 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(image, "Show a sign...", (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('ISL Alphabet Recognition', image)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("\nReal-time prediction ended.")
