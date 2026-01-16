import tensorflow as tf
import numpy as np
import cv2
import os

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "170-0.83.hdf5")
LABELS_PATH = os.path.join(BASE_DIR, "word_labels.txt")

# ---------------- LOAD LABELS ----------------
with open(LABELS_PATH, "r") as f:
    WORD_CLASSES = [line.strip() for line in f if line.strip()]

# ---------------- LOAD MODEL (ONCE) ----------------
try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("✓ Word model loaded successfully")
except Exception as e:
    print("✗ Failed to load word model")
    raise e   # IMPORTANT: no silent mock predictions

# ---------------- PREDICT FUNCTION ----------------
def predict_word(image_bytes):
    """
    Input: image bytes
    Output: (word, confidence)
    """

    # Decode image
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        return "invalid_image", 0.0

    # Preprocessing (MUST match training)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    # Prediction
    preds = model.predict(img)
    idx = int(np.argmax(preds))
    confidence = float(preds[0][idx])

    # Confidence threshold
    if confidence < 0.6:
        return "unknown", confidence

    return WORD_CLASSES[idx], confidence
