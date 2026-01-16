import os
import cv2
import numpy as np
import tensorflow as tf

# paths
MODEL_PATH = "backend/models/words_model.h5"
LABELS_PATH = "backend/models/word_labels.txt"
DATASET_DIR = r"C:\Users\Admn\Downloads\Frames_Word_Level"

# load model
model = tf.keras.models.load_model(MODEL_PATH, compile=False)

# load labels
with open(LABELS_PATH) as f:
    labels = [l.strip() for l in f if l.strip()]

print("Labels:", labels)

# test one image per word (only for words the model knows)
for word in labels:
    word_path = os.path.join(DATASET_DIR, word)
    if not os.path.isdir(word_path):
        continue

    images = os.listdir(word_path)
    if not images:
        continue

    img_path = os.path.join(word_path, images[0])
    img = cv2.imread(img_path)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img)
    idx = np.argmax(preds)

    print(f"GT: {word:15s} → Predicted: {labels[idx]} ({preds[0][idx]:.2f})")
