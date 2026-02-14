import pickle
import cv2
import mediapipe as mp
import numpy as np
from collections import Counter
from pathlib import Path


class SignLanguageDetector:
    
    def __init__(self, model_path=None, min_detection_confidence=0.3, max_num_hands=2):
        
        if model_path is None:
            possible_paths = [
                Path(__file__).parent.parent / 'model.p',
                Path(__file__).parent / 'model.p',
                Path('./model.p')
            ]
            for path in possible_paths:
                if path.exists():
                    model_path = path
                    break
            else:
                raise FileNotFoundError("Could not find model.p file")
        
        # Load the trained model
        with open(model_path, 'rb') as f:
            model_dict = pickle.load(f)
        self.model = model_dict['model']
        
        # Map specific predicted labels to display labels
        self.label_map = {
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            'hello': 'Hello',
            'goodbye': 'Goodbye',
            'namaste': 'Namaste',
            'help': 'Help',
            'yes': 'Yes',
            'I_love_you': 'I Love You',
            'space': ' '
        }
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )
    
    def process_frame(self, frame, draw_landmarks=True):
        H, W, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = self.hands.process(frame_rgb)
        
        result = {
            'prediction': None,
            'predictions': [],
            'bounding_box': None,
            'frame': frame,
            'hand_landmarks': results.multi_hand_landmarks
        }
        
        if results.multi_hand_landmarks:
            # Draw landmarks if requested
            if draw_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
            
            # Collect coordinates and predictions
            all_x = []
            all_y = []
            predictions = []
            
            for hand_landmarks in results.multi_hand_landmarks:
                data_aux = []
                x_ = []
                y_ = []
                
                # Collect normalized landmarks
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
                
                all_x.extend(x_)
                all_y.extend(y_)
                
                # Pad single hand to 84 features
                if len(data_aux) == 42:
                    data_aux.extend([0.0] * 42)
                
                prediction = self.model.predict([np.asarray(data_aux)])
                predictions.append(str(prediction[0]))
            
            # Map labels and get most common prediction
            display_preds = [self.label_map.get(p, p) for p in predictions]
            label_text = Counter(display_preds).most_common(1)[0][0]
            
            # Compute bounding box
            x1 = max(int(min(all_x) * W) - 10, 0)
            y1 = max(int(min(all_y) * H) - 10, 0)
            x2 = min(int(max(all_x) * W) + 10, W - 1)
            y2 = min(int(max(all_y) * H) + 10, H - 1)
            
            result['prediction'] = label_text
            result['predictions'] = display_preds
            result['bounding_box'] = (x1, y1, x2, y2)
            result['frame'] = frame
        
        return result
    
    def predict_from_frame(self, frame):
        result = self.process_frame(frame, draw_landmarks=False)
        return result['prediction']
    
    def release(self):
        self.hands.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
