import numpy as np
import os

path = r"C:\Users\Admn\Documents\GitHub\Vaani\backend\processed_keypoints"

print("Checking training data format:")
print("=" * 50)

for cls in ['A', 'B', 'C', '1', 'T']:
    files = os.listdir(os.path.join(path, cls))
    data = np.load(os.path.join(path, cls, files[0]))
    h1 = np.abs(data[:63]).sum()
    h2 = np.abs(data[63:]).sum()
    print(f"{cls}: hand1={h1:.3f}, hand2={h2:.3f}")

print("\n" + "=" * 50)
print("Sample A data structure:")
files = os.listdir(os.path.join(path, 'A'))
data = np.load(os.path.join(path, 'A', files[0]))
print(f"Shape: {data.shape}")
print(f"First hand landmarks [0:63]: min={data[:63].min():.4f}, max={data[:63].max():.4f}")
print(f"Second hand landmarks [63:126]: min={data[63:].min():.4f}, max={data[63:].max():.4f}")
