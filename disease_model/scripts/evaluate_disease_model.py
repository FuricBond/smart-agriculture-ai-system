"""
Disease Detection Model — Evaluation Script
==============================================
Runs the trained model on the full validation set and generates:
- Confusion matrix (saved as PNG)
- Classification report (precision, recall, F1 per class)
- Top-1 and Top-5 accuracy

Project: AI-Based Crop Health and Yield Prediction System
"""

import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

DATA_DIR = r"C:\CropProject\disease_model\data\combined"
MODEL_DIR = r"C:\CropProject\disease_model\models"
REPORT_DIR = r"C:\CropProject\disease_model\reports"

MODEL_PATH = os.path.join(MODEL_DIR, "disease_model.pth")
CLASS_MAP_PATH = os.path.join(MODEL_DIR, "class_names.json")

IMAGE_SIZE = 224
BATCH_SIZE = 32
NUM_WORKERS = 4

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

os.makedirs(REPORT_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  DISEASE DETECTION MODEL — EVALUATION")
print("=" * 60)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n🖥  Device: {device}")


# ═══════════════════════════════════════════════════════════════
# LOAD CLASS NAMES
# ═══════════════════════════════════════════════════════════════

try:
    with open(CLASS_MAP_PATH, 'r') as f:
        class_data = json.load(f)
    class_names = class_data['class_names']
except FileNotFoundError:
    class_names = sorted([
        d for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    ])

num_classes = len(class_names)
print(f"   Classes: {num_classes}")


# ═══════════════════════════════════════════════════════════════
# LOAD DATASET (Validation Transform Only)
# ═══════════════════════════════════════════════════════════════

print(f"\n📂 Loading dataset...")

val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

dataset = datasets.ImageFolder(root=DATA_DIR, transform=val_transform)

# Use 20% as validation (same split ratio as training)
torch.manual_seed(42)
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
_, val_dataset = torch.utils.data.random_split(
    dataset, [train_size, val_size],
    generator=torch.Generator().manual_seed(42)
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
    pin_memory=True if device.type == 'cuda' else False
)

print(f"   Validation images: {len(val_dataset):,}")


# ═══════════════════════════════════════════════════════════════
# LOAD MODEL
# ═══════════════════════════════════════════════════════════════

print(f"\n🤖 Loading model...")

model = models.resnet50(weights=None)
num_features = model.fc.in_features
model.fc = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(num_features, 512),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(512, num_classes)
)

try:
    state_dict = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
except RuntimeError:
    # Legacy model format
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    state_dict = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)

model = model.to(device)
model.eval()
print(f"   ✅ Model loaded")


# ═══════════════════════════════════════════════════════════════
# EVALUATE
# ═══════════════════════════════════════════════════════════════

print(f"\n🔬 Running evaluation on {len(val_dataset):,} images...")

all_preds = []
all_labels = []
all_top5_correct = 0
total = 0

with torch.no_grad():
    for batch_idx, (images, labels) in enumerate(val_loader):
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)

        # Top-1
        _, predicted = outputs.max(1)
        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

        # Top-5
        _, top5_pred = outputs.topk(5, dim=1)
        for i in range(labels.size(0)):
            if labels[i].item() in top5_pred[i].cpu().numpy():
                all_top5_correct += 1
        total += labels.size(0)

        if (batch_idx + 1) % 50 == 0:
            print(f"   Processed {(batch_idx + 1) * BATCH_SIZE:,} / {len(val_dataset):,} images")

all_preds = np.array(all_preds)
all_labels = np.array(all_labels)


# ═══════════════════════════════════════════════════════════════
# METRICS
# ═══════════════════════════════════════════════════════════════

top1_acc = (all_preds == all_labels).mean()
top5_acc = all_top5_correct / total

print(f"\n   ┌─────────────────────────────────┐")
print(f"   │  EVALUATION RESULTS             │")
print(f"   ├─────────────────────────────────┤")
print(f"   │  Top-1 Accuracy: {top1_acc:.4f}         │")
print(f"   │  Top-5 Accuracy: {top5_acc:.4f}         │")
print(f"   │  Total Images:   {total:,}        │")
print(f"   └─────────────────────────────────┘")


# ═══════════════════════════════════════════════════════════════
# CLASSIFICATION REPORT
# ═══════════════════════════════════════════════════════════════

print(f"\n📋 Generating classification report...")

report = classification_report(
    all_labels, all_preds,
    target_names=class_names,
    digits=4,
    zero_division=0
)
print(report)

# Save report
report_path = os.path.join(REPORT_DIR, "classification_report.txt")
with open(report_path, 'w') as f:
    f.write("DISEASE DETECTION MODEL — CLASSIFICATION REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Top-1 Accuracy: {top1_acc:.4f}\n")
    f.write(f"Top-5 Accuracy: {top5_acc:.4f}\n")
    f.write(f"Total Images:   {total:,}\n\n")
    f.write("=" * 60 + "\n\n")
    f.write(report)
print(f"   ✅ Report saved: {report_path}")


# ═══════════════════════════════════════════════════════════════
# CONFUSION MATRIX
# ═══════════════════════════════════════════════════════════════

print(f"\n📊 Generating confusion matrix...")

cm = confusion_matrix(all_labels, all_preds)

# Full confusion matrix (may be large with 52 classes)
fig, ax = plt.subplots(figsize=(24, 22))
sns.heatmap(
    cm, annot=False, cmap='Blues', ax=ax,
    xticklabels=class_names,
    yticklabels=class_names,
    linewidths=0.2
)
ax.set_title('Disease Detection — Confusion Matrix', fontsize=16, fontweight='bold')
ax.set_xlabel('Predicted', fontsize=12)
ax.set_ylabel('Actual', fontsize=12)
plt.xticks(rotation=90, fontsize=5)
plt.yticks(rotation=0, fontsize=5)
plt.tight_layout()

cm_path = os.path.join(REPORT_DIR, "confusion_matrix.png")
fig.savefig(cm_path, dpi=150)
plt.close(fig)
print(f"   ✅ Confusion matrix saved: {cm_path}")

# Per-class accuracy
print(f"\n📊 Per-class accuracy:")
per_class_acc = cm.diagonal() / cm.sum(axis=1).clip(min=1)
for i, (cls, acc) in enumerate(zip(class_names, per_class_acc)):
    indicator = "✅" if acc >= 0.9 else ("⚠" if acc >= 0.7 else "❌")
    print(f"   {indicator} {cls:<40} {acc:.4f}")


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  ✅ EVALUATION COMPLETE")
print("=" * 60)
print(f"  Top-1 Accuracy: {top1_acc:.4f}")
print(f"  Top-5 Accuracy: {top5_acc:.4f}")
print(f"  Classes:        {num_classes}")
print("=" * 60)
print("  📁 Files saved:")
print(f"     Report:           {report_path}")
print(f"     Confusion Matrix: {cm_path}")
print("=" * 60)
