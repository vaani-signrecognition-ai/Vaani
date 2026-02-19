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
        self.mirror_mode = True
        self.running = True
        self.is_speaking = False
        self.mouse_pos = (0, 0)
        
        # Premium Color Palette (BGR)
        self.COLORS = {
            'bg_dark': (30, 25, 25),
            'accent': (255, 120, 80),      # Coral/Bright Orange
            'secondary': (180, 180, 180),
            'text': (245, 245, 245),
            'success': (100, 220, 100),
            'btn_normal': (60, 50, 50),
            'btn_hover': (90, 80, 80),
            'glass_bg': (40, 35, 35),
            'sidebar': (25, 20, 20)
        }
        
        # Button definitions (Adjusted to fit 640px width)
        self.BUTTON_H = 40
        self.BUTTON_W = 95
        self.PAD = 10
        self.buttons = {
            'add': {'x': 10, 'y': 20, 'w': 110, 'h': self.BUTTON_H, 'label': 'ADD WORD'},
            'space': {'x': 130, 'y': 20, 'w': 80, 'h': self.BUTTON_H, 'label': 'SPACE'},
            'clear': {'x': 220, 'y': 20, 'w': 80, 'h': self.BUTTON_H, 'label': 'CLEAR'},
            'speak': {'x': 310, 'y': 20, 'w': 80, 'h': self.BUTTON_H, 'label': 'SPEAK'},
            'mirror': {'x': 400, 'y': 20, 'w': 90, 'h': self.BUTTON_H, 'label': 'MIRROR'},
            'stop': {'x': 520, 'y': 20, 'w': 100, 'h': self.BUTTON_H, 'label': 'STOP (Q)'},
        }
    
    def draw_rounded_rect(self, img, pt1, pt2, color, thickness=-1, radius=10):
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Draw corners
        cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness)
        cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness)
        cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness)
        cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness)
        
        # Draw rectangles
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)

    def draw_ui_overlay(self, frame):
        H, W, _ = frame.shape
        overlay = frame.copy()
        
        # 1. Top Bar Background (Glass effect)
        cv2.rectangle(overlay, (0, 0), (W, 85), self.COLORS['bg_dark'], -1)
        
        # 2. Bottom Bar (Sentence Display)
        cv2.rectangle(overlay, (0, H - 100), (W, H), self.COLORS['bg_dark'], -1)
        
        # Apply transparency
        alpha = 0.85
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # 3. Draw Buttons
        for name, btn in self.buttons.items():
            is_hover = self.is_point_in_button(self.mouse_pos[0], self.mouse_pos[1], btn)
            color = self.COLORS['btn_hover'] if is_hover else self.COLORS['btn_normal']
            if name == 'mirror' and self.mirror_mode:
                color = self.COLORS['accent']
                
            self.draw_rounded_rect(frame, (btn['x'], btn['y']), (btn['x'] + btn['w'], btn['y'] + btn['h']), color, radius=8)
            
            # Text placement
            font = cv2.FONT_HERSHEY_DUPLEX
            text_size = cv2.getTextSize(btn['label'], font, 0.5, 1)[0]
            text_x = btn['x'] + (btn['w'] - text_size[0]) // 2
            text_y = btn['y'] + (btn['h'] + text_size[1]) // 2
            cv2.putText(frame, btn['label'], (text_x, text_y), font, 0.5, self.COLORS['text'], 1, cv2.LINE_AA)

        # 4. Draw Sentence Text
        sentence_label = "SENTENCE:"
        cv2.putText(frame, sentence_label, (25, H - 70), cv2.FONT_HERSHEY_DUPLEX, 0.6, self.COLORS['accent'], 1, cv2.LINE_AA)
        
        display_text = self.sentence if self.sentence else "Start signing and click 'ADD WORD'..."
        txt_color = self.COLORS['text'] if self.sentence else self.COLORS['secondary']
        cv2.putText(frame, display_text, (25, H - 35), cv2.FONT_HERSHEY_DUPLEX, 0.9, txt_color, 2, cv2.LINE_AA)

    def is_point_in_button(self, x, y, btn):
        return btn['x'] <= x <= btn['x'] + btn['w'] and btn['y'] <= y <= btn['y'] + btn['h']
    
    def mouse_callback(self, event, x, y, flags, param):
        self.mouse_pos = (x, y)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            for name, btn in self.buttons.items():
                if self.is_point_in_button(x, y, btn):
                    if name == 'add' and self.current_prediction:
                        if self.sentence and not self.sentence.endswith(' '):
                            self.sentence += ' '
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
    
    def speak_text(self, text):
        if self.is_speaking: return
        def speak():
            self.is_speaking = True
            try:
                # Initialize engine inside the thread
                import platform
                driver = 'sapi5' if platform.system() == 'Windows' else None
                engine = pyttsx3.init(driver)
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                self.is_speaking = False
        threading.Thread(target=speak, daemon=True).start()

    def run(self):
        cap = cv2.VideoCapture(0)
        # Use higher resolution if possible
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        window_name = 'Vaani Sign Detector'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        while self.running:
            ret, frame = cap.read()
            if not ret: break
            
            if self.mirror_mode: frame = cv2.flip(frame, 1)
            H, W, _ = frame.shape
            
            # Reposition buttons to center if W changes
            total_buttons_width = 620 # Approx width of all buttons
            start_x = (W - total_buttons_width) // 2
            offset = start_x
            for name, btn in self.buttons.items():
                btn['x'] = offset
                offset += btn['w'] + 10
            
            # Process frame
            result = self.detector.process_frame(frame, draw_landmarks=False)
            self.current_prediction = result['prediction'] or ""
            
            # Custom Landmark Drawing (Cleaner)
            if result['hand_landmarks']:
                for hand_landmarks in result['hand_landmarks']:
                    self.detector.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.detector.mp_hands.HAND_CONNECTIONS,
                        self.detector.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.detector.mp_drawing_styles.get_default_hand_connections_style()
                    )

            # Bounding Box with Label
            if result['bounding_box']:
                x1, y1, x2, y2 = result['bounding_box']
                # Draw sleek label background
                cv2.rectangle(frame, (x1, y1 - 35), (x1 + 120, y1), self.COLORS['accent'], -1)
                cv2.putText(frame, self.current_prediction, (x1 + 5, y1 - 10), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.rectangle(frame, (x1, y1), (x2, y2), self.COLORS['accent'], 2)
            
            # UI Overlay
            self.draw_ui_overlay(frame)
            
            cv2.imshow('Vaani Sign Detector', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        
        cap.release()
        cv2.destroyAllWindows()
        self.detector.release()

def run_detector_ui(model_path=None, frame_width=1280, frame_height=720):
    ui = DetectorUI(model_path=model_path, frame_width=frame_width, frame_height=frame_height)
    ui.run()

if __name__ == "__main__":
    run_detector_ui()
