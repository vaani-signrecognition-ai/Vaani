import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from pathlib import Path

# Use absolute paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DATA_PATH = SCRIPT_DIR / 'data.pickle'
MODEL_PATH = SCRIPT_DIR / 'model.p'

# Load data
if not DATA_PATH.exists():
    print(f"Error: Data file not found at {DATA_PATH}. Please run create_dataset.py first.")
    exit(1)

data_dict = pickle.load(open(DATA_PATH, 'rb'))

data = np.asarray(data_dict['data'])
labels = np.asarray(data_dict['labels'])

# Split data
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

# Initialize and train model
model = RandomForestClassifier(n_estimators=100)
model.fit(x_train, y_train)

# Predict and evaluate
y_predict = model.predict(x_test)
score = accuracy_score(y_predict, y_test)

print(f'{score * 100}% of samples were classified correctly !')

# Save model
with open(MODEL_PATH, 'wb') as f:
    pickle.dump({'model': model}, f)

print(f"Model saved to {MODEL_PATH}")
