import cv2
import pyttsx3
import threading
from pathlib import Path
from .detector import SignLanguageDetector


class DetectorUI:
    
    def __init__(self, model_path=None, frame_width=1280, frame_height=720):
        self.detector = SignLanguageDetector(model_path=model_path)
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # State variables
        self.sentence = ""
        self.current_prediction = ""
        self.mirror_mode = False
        self.running = True
        self.is_speaking = False
        
        # Button definitions with light colors
        BUTTON_HEIGHT = 50
        BUTTON_Y = 10
        self.buttons = {
            'add': {'x': 10, 'y': BUTTON_Y, 'w': 120, 'h': BUTTON_HEIGHT, 'label': 'ADD LETTER', 'color': (144, 238, 144)},
            'space': {'x': 140, 'y': BUTTON_Y, 'w': 100, 'h': BUTTON_HEIGHT, 'label': 'SPACE', 'color': (250, 200, 120)},
            'clear': {'x': 250, 'y': BUTTON_Y, 'w': 100, 'h': BUTTON_HEIGHT, 'label': 'CLEAR', 'color': (147, 181, 255)},
            'speak': {'x': 360, 'y': BUTTON_Y, 'w': 100, 'h': BUTTON_HEIGHT, 'label': 'SPEAK', 'color': (238, 180, 238)},
            'mirror': {'x': 470, 'y': BUTTON_Y, 'w': 100, 'h': BUTTON_HEIGHT, 'label': 'MIRROR', 'color': (200, 200, 200)},
            'stop': {'x': 580, 'y': BUTTON_Y, 'w': 100, 'h': BUTTON_HEIGHT, 'label': 'STOP', 'color': (180, 150, 255)},
        }
    
    def speak_text(self, text):
        if self.is_speaking:
            return
        
        def speak():
            self.is_speaking = True
            try:
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"Speech error: {e}")
            finally:
                self.is_speaking = False
        
        thread = threading.Thread(target=speak, daemon=True)
        thread.start()
    
    def draw_button(self, frame, btn):
        color = btn['color']
        
        # Draw button background
        cv2.rectangle(frame, (btn['x'], btn['y']), (btn['x'] + btn['w'], btn['y'] + btn['h']), color, -1)
        # Draw button border
        cv2.rectangle(frame, (btn['x'], btn['y']), (btn['x'] + btn['w'], btn['y'] + btn['h']), (80, 80, 80), 2)
        
        # Draw button text (black for light backgrounds)
        text_size = cv2.getTextSize(btn['label'], cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        text_x = btn['x'] + (btn['w'] - text_size[0]) // 2
        text_y = btn['y'] + (btn['h'] + text_size[1]) // 2
        cv2.putText(frame, btn['label'], (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    def is_point_in_button(self, x, y, btn):
        return btn['x'] <= x <= btn['x'] + btn['w'] and btn['y'] <= y <= btn['y'] + btn['h']
    
    def mouse_callback(self, event, x, y, flags, param):
        # Adjust x coordinate if mirror mode is on
        click_x = self.frame_width - x if self.mirror_mode else x
        
        if event == cv2.EVENT_LBUTTONDOWN:
            for name, btn in self.buttons.items():
                if self.is_point_in_button(click_x, y, btn):
                    if name == 'add' and self.current_prediction:
                        self.sentence += self.current_prediction
                    elif name == 'space':
                        self.sentence += ' '
                    elif name == 'clear':
                        self.sentence = ''
                    elif name == 'speak':
                        if self.sentence.strip():
                            self.speak_text(self.sentence)
                    elif name == 'mirror':
                        self.mirror_mode = not self.mirror_mode
                    elif name == 'stop':
                        self.running = False
                    break
    
    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        
        cv2.namedWindow('Sign Language Detector')
        cv2.setMouseCallback('Sign Language Detector', self.mouse_callback)
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Apply mirror effect if enabled
            if self.mirror_mode:
                frame = cv2.flip(frame, 1)
            
            H, W, _ = frame.shape
            self.frame_width = W
            
            # Process frame
            result = self.detector.process_frame(frame, draw_landmarks=True)
            frame = result['frame']
            self.current_prediction = result['prediction'] or ""
            
            # Draw bounding box if detection exists
            if result['bounding_box']:
                x1, y1, x2, y2 = result['bounding_box']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
                cv2.putText(frame, self.current_prediction, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)
            
            # Draw buttons
            for name, btn in self.buttons.items():
                if name == 'mirror':
                    btn['color'] = (144, 238, 144) if self.mirror_mode else (200, 200, 200)
                self.draw_button(frame, btn)
            
            # Draw sentence display area
            sentence_y = 80
            cv2.rectangle(frame, (10, sentence_y), (W - 10, sentence_y + 50), (50, 50, 50), -1)
            cv2.rectangle(frame, (10, sentence_y), (W - 10, sentence_y + 50), (255, 255, 255), 2)
            
            # Display the current sentence
            display_sentence = self.sentence if self.sentence else "Your sentence will appear here..."
            cv2.putText(frame, display_sentence, (20, sentence_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Display current prediction indicator
            if self.current_prediction:
                cv2.putText(frame, f"Current: {self.current_prediction}", (W - 200, sentence_y + 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Sign Language Detector', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        self.detector.release()
    
    def get_sentence(self):
        return self.sentence
    
    def clear_sentence(self):
        self.sentence = ""


def run_detector_ui(model_path=None, frame_width=1280, frame_height=720):
    ui = DetectorUI(model_path=model_path, frame_width=frame_width, frame_height=frame_height)
    ui.run()



if __name__ == "__main__":
    run_detector_ui()
