import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import h5py

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

class ISLDataset(Dataset):
    def __init__(self, root_dir):
        self.samples = []
        self.class_names = sorted(os.listdir(root_dir))

        for idx, cls in enumerate(self.class_names):
            cls_path = os.path.join(root_dir, cls)
            if not os.path.isdir(cls_path):
                continue
            for f in os.listdir(cls_path):
                if f.endswith(".npy"):
                    self.samples.append((os.path.join(cls_path, f), idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x_path, y = self.samples[idx]
        x = np.load(x_path)
        return torch.tensor(x, dtype=torch.float32), y

# Test the dataset class
if __name__ == "__main__":
    DATA_DIR = r"C:\Users\Admn\Documents\GitHub\Vaani\backend\processed_keypoints"

    dataset = ISLDataset(DATA_DIR)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model = ISLModel(num_classes=len(dataset.class_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    EPOCHS = 30 

    for epoch in range(EPOCHS):
        correct = 0
        total_loss = 0

        for x, y in loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            correct += (out.argmax(1) == y).sum().item()

        acc = correct / len(dataset)
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss:.4f} | Acc: {acc:.4f}")

    # Save the trained model
    torch.save({
        "model_state": model.state_dict(),
        "classes": dataset.class_names
    }, r"C:\Users\Admn\Documents\GitHub\Vaani\backend\models\isl_alphanum_model.pth")

    print("🎉 Model saved!")
