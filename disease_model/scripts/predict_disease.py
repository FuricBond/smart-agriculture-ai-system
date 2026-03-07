"""
Disease Detection Model — Prediction Script
==============================================
Predicts plant disease from a leaf image using the
trained ResNet50 model. Returns top-5 predictions
with confidence scores.

Project: AI-Based Crop Health and Yield Prediction System
"""

import os
import sys
import json
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

MODEL_DIR = r"C:\CropProject\disease_model\models"
MODEL_PATH = os.path.join(MODEL_DIR, "disease_model.pth")
CLASS_MAP_PATH = os.path.join(MODEL_DIR, "class_names.json")

IMAGE_SIZE = 224
TOP_K = 5

# ImageNet normalization (MUST match training)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


# ═══════════════════════════════════════════════════════════════
# LOAD CLASS NAMES
# ═══════════════════════════════════════════════════════════════

print("=" * 55)
print("  🌿 PLANT DISEASE DETECTION SYSTEM")
print("=" * 55)

try:
    with open(CLASS_MAP_PATH, 'r') as f:
        class_data = json.load(f)
    class_names = class_data['class_names']
    num_classes = len(class_names)
    print(f"  ✅ Loaded {num_classes} disease classes")
except FileNotFoundError:
    # Fallback: scan directory structure
    DATA_DIR = r"C:\CropProject\disease_model\data\combined"
    if os.path.isdir(DATA_DIR):
        class_names = sorted([
            d for d in os.listdir(DATA_DIR)
            if os.path.isdir(os.path.join(DATA_DIR, d))
        ])
        num_classes = len(class_names)
        print(f"  ⚠ Class names loaded from dataset dir ({num_classes} classes)")
    else:
        print("  ❌ Cannot find class_names.json or dataset directory")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# LOAD MODEL
# ═══════════════════════════════════════════════════════════════

print("  Loading model...")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
except FileNotFoundError:
    print(f"  ❌ Model file not found: {MODEL_PATH}")
    print("  Run train_disease_model.py first.")
    sys.exit(1)
except RuntimeError as e:
    # If the model architecture doesn't match (old model format),
    # try loading with the original simple FC layer
    print("  ⚠ Model architecture mismatch. Trying legacy format...")
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    state_dict = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    print("  ✅ Loaded with legacy architecture")

model = model.to(device)
model.eval()
print(f"  ✅ Model loaded on {device}")


# ═══════════════════════════════════════════════════════════════
# IMAGE TRANSFORM (must match validation transform from training)
# ═══════════════════════════════════════════════════════════════

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


# ═══════════════════════════════════════════════════════════════
# GET INPUT
# ═══════════════════════════════════════════════════════════════

# Support command-line argument or interactive input
if len(sys.argv) > 1:
    image_path = sys.argv[1]
else:
    print(f"\n📷 Enter path to a leaf image:")
    image_path = input("   Image path: ").strip().strip('"').strip("'")

# Validate input
if not os.path.isfile(image_path):
    print(f"\n  ❌ Error: File not found: {image_path}")
    sys.exit(1)

# Check if it's a valid image
valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
ext = os.path.splitext(image_path)[1].lower()
if ext not in valid_extensions:
    print(f"\n  ⚠ Warning: '{ext}' may not be a valid image format")


# ═══════════════════════════════════════════════════════════════
# PREDICT
# ═══════════════════════════════════════════════════════════════

print(f"\n🔬 Analyzing image: {os.path.basename(image_path)}")

try:
    img = Image.open(image_path).convert('RGB')
except Exception as e:
    print(f"\n  ❌ Error opening image: {e}")
    sys.exit(1)

img_tensor = transform(img).unsqueeze(0).to(device)

with torch.no_grad():
    outputs = model(img_tensor)
    probabilities = torch.softmax(outputs, dim=1)[0]

    # Top-K predictions
    top_probs, top_indices = torch.topk(probabilities, TOP_K)


# ═══════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════

top_class = class_names[top_indices[0].item()]
top_confidence = top_probs[0].item() * 100

# Parse disease name
parts = top_class.split('___')
plant = parts[0].replace('_', ' ') if len(parts) > 0 else 'Unknown'
disease = parts[1].replace('_', ' ') if len(parts) > 1 else 'Unknown'

print("\n" + "=" * 55)
print(f"  🌿 DISEASE DETECTION RESULTS")
print("=" * 55)
print(f"\n  Plant:      {plant}")
print(f"  Condition:  {disease}")
print(f"  Confidence: {top_confidence:.1f}%")

# Confidence indicator
if top_confidence >= 90:
    indicator = "🟢 HIGH CONFIDENCE"
elif top_confidence >= 70:
    indicator = "🟡 MODERATE CONFIDENCE"
else:
    indicator = "🔴 LOW CONFIDENCE — Consider re-taking image"

print(f"  Status:     {indicator}")

print(f"\n  Top {TOP_K} Predictions:")
print(f"  {'─' * 48}")

for rank, (prob, idx) in enumerate(zip(top_probs, top_indices), 1):
    name = class_names[idx.item()]
    conf = prob.item() * 100
    bar_len = int(conf / 100 * 30)
    bar = '█' * bar_len + '░' * (30 - bar_len)
    print(f"   {rank}. {name:<35} {conf:5.1f}%")
    print(f"      {bar}")

print(f"\n  {'─' * 48}")
print("=" * 55)