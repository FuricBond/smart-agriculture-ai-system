"""
Disease Detection Model — Professional Training Pipeline
==========================================================
Trains a ResNet50 CNN for plant disease classification with:
- Separate train/val transforms
- Validation loop with metrics
- Learning rate scheduler
- Early stopping
- Best model checkpoint saving
- Class name mapping (saved as JSON)
- Mixed precision training (AMP)

Project: AI-Based Crop Health and Yield Prediction System
"""

import os
import sys
import json
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import GradScaler, autocast
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import classification_report


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

DATA_DIR = r"D:\Project\CropProject\disease_model\data\combined"
MODEL_DIR = r"D:\Project\CropProject\disease_model\models"
REPORT_DIR = r"D:\Project\CropProject\disease_model\reports"

# Hyperparameters
IMAGE_SIZE = 224
BATCH_SIZE = 32
LEARNING_RATE = 1e-4
EPOCHS = 15
PATIENCE = 4           # Early stopping patience
NUM_WORKERS = 0         # 0 on Windows (GPU compute compensates)
TRAIN_SPLIT = 0.8

RANDOM_SEED = 42

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)



def main():
    print("=" * 60)
    print("  DISEASE DETECTION MODEL — TRAINING PIPELINE")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n🖥  Device: {device}")
    if device.type == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    use_amp = device.type == 'cuda'  # Mixed precision only on GPU

    torch.manual_seed(RANDOM_SEED)
    if device.type == 'cuda':
        torch.cuda.manual_seed(RANDOM_SEED)


    # ═══════════════════════════════════════════════════════════════
    # 2. DATA TRANSFORMS (Separate for train and validation)
    # ═══════════════════════════════════════════════════════════════

    # ImageNet normalization constants
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]

    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),
        transforms.RandomCrop(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(15),
        transforms.ColorJitter(
            brightness=0.2, contrast=0.2,
            saturation=0.2, hue=0.1
        ),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


    # ═══════════════════════════════════════════════════════════════
    # 3. LOAD DATASET
    # ═══════════════════════════════════════════════════════════════

    print(f"\n📂 Loading dataset from {DATA_DIR}...")

    # Load full dataset with train transform (we'll override for val)
    full_dataset = datasets.ImageFolder(root=DATA_DIR, transform=train_transform)
    num_classes = len(full_dataset.classes)

    print(f"   Total Classes: {num_classes}")
    print(f"   Total Images:  {len(full_dataset):,}")

    # Save class name mapping
    class_names = full_dataset.classes
    class_to_idx = full_dataset.class_to_idx

    class_map_path = os.path.join(MODEL_DIR, "class_names.json")
    with open(class_map_path, 'w') as f:
        json.dump({
            'class_names': class_names,
            'class_to_idx': class_to_idx,
            'idx_to_class': {str(v): k for k, v in class_to_idx.items()}
        }, f, indent=2)
    print(f"   ✅ Class mapping saved: {class_map_path}")

    # Train/Validation Split
    train_size = int(TRAIN_SPLIT * len(full_dataset))
    val_size = len(full_dataset) - train_size

    train_dataset, val_dataset = random_split(
        full_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(RANDOM_SEED)
    )

    # Override validation transform
    class ValSubset(torch.utils.data.Dataset):
        """Wraps a Subset to apply a different transform."""
        def __init__(self, subset, transform):
            self.subset = subset
            self.transform = transform

        def __len__(self):
            return len(self.subset)

        def __getitem__(self, idx):
            img, label = self.subset[idx]
            # img is already transformed; we need the original
            # Re-load from disk with val transform
            img_path = self.subset.dataset.samples[self.subset.indices[idx]][0]
            from PIL import Image
            img = Image.open(img_path).convert('RGB')
            img = self.transform(img)
            return img, label

    val_dataset = ValSubset(val_dataset, val_transform)

    print(f"\n📊 Split:")
    print(f"   Training:   {train_size:,} images")
    print(f"   Validation: {val_size:,} images")

    # DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=True if device.type == 'cuda' else False
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=True if device.type == 'cuda' else False
    )


    # ═══════════════════════════════════════════════════════════════
    # 4. MODEL ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════

    print(f"\n🤖 Building EfficientNet-B0 model (D4 Upgrade)...")

    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)

    # Freeze early feature blocks, fine-tune last 2 blocks + classifier
    for name, param in model.named_parameters():
        if 'features.7' not in name and 'features.8' not in name and 'classifier' not in name:
            param.requires_grad = False

    # Replace classifier head
    num_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_features, num_classes)
    )

    model = model.to(device)

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Total parameters:     {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")
    print(f"   Frozen parameters:    {total_params - trainable_params:,}")


    # ═══════════════════════════════════════════════════════════════
    # 5. LOSS, OPTIMIZER, SCHEDULER
    # ═══════════════════════════════════════════════════════════════

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LEARNING_RATE,
        weight_decay=1e-4
    )

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=2
    )

    scaler = GradScaler('cuda', enabled=use_amp)


    # ═══════════════════════════════════════════════════════════════
    # 6. TRAINING LOOP
    # ═══════════════════════════════════════════════════════════════

    print(f"\n🚀 Starting Training ({EPOCHS} epochs)...")
    print(f"   {'─' * 56}")

    best_val_acc = 0.0
    patience_counter = 0
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}

    for epoch in range(1, EPOCHS + 1):
        epoch_start = time.time()

        # ── Training Phase ──
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            with autocast('cuda', enabled=use_amp):
                outputs = model(images)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            train_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

            if (batch_idx + 1) % 200 == 0:
                batch_acc = train_correct / train_total * 100
                print(f"      Epoch {epoch} | Batch {batch_idx+1}/{len(train_loader)} | Loss: {loss.item():.4f} | Acc: {batch_acc:.1f}%", flush=True)

        train_loss /= train_total
        train_acc = train_correct / train_total

        # ── Validation Phase ──
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)

                with autocast('cuda', enabled=use_amp):
                    outputs = model(images)
                    loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_loss /= val_total
        val_acc = val_correct / val_total

        # Update scheduler
        scheduler.step(val_acc)

        # Save history
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)

        epoch_time = time.time() - epoch_start
        lr_current = optimizer.param_groups[0]['lr']

        # Check for improvement
        improved = ''
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            improved = ' ★ BEST'
            # Save best model
            best_model_path = os.path.join(MODEL_DIR, "disease_model.pth")
            torch.save(model.state_dict(), best_model_path)
        else:
            patience_counter += 1

        print(f"   Epoch {epoch:2d}/{EPOCHS} │ "
              f"Loss: {train_loss:.4f}/{val_loss:.4f} │ "
              f"Acc: {train_acc:.4f}/{val_acc:.4f} │ "
              f"LR: {lr_current:.1e} │ "
              f"{epoch_time:.0f}s{improved}")

        # Early stopping
        if patience_counter >= PATIENCE:
            print(f"\n   ⏹ Early stopping at epoch {epoch} "
                  f"(no improvement for {PATIENCE} epochs)")
            break

    print(f"   {'─' * 56}")


    # ═══════════════════════════════════════════════════════════════
    # 7. SAVE TRAINING HISTORY
    # ═══════════════════════════════════════════════════════════════

    print("\n📊 Saving training history plot...")

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        epochs_range = range(1, len(history['train_loss']) + 1)

        ax1.plot(epochs_range, history['train_loss'], 'b-o', label='Train Loss', markersize=4)
        ax1.plot(epochs_range, history['val_loss'], 'r-o', label='Val Loss', markersize=4)
        ax1.set_title('Training & Validation Loss', fontsize=13, fontweight='bold')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(epochs_range, history['train_acc'], 'b-o', label='Train Acc', markersize=4)
        ax2.plot(epochs_range, history['val_acc'], 'r-o', label='Val Acc', markersize=4)
        ax2.set_title('Training & Validation Accuracy', fontsize=13, fontweight='bold')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        history_path = os.path.join(REPORT_DIR, "training_history.png")
        fig.savefig(history_path, dpi=150)
        plt.close(fig)
        print(f"   ✅ Training history plot saved: {history_path}")
    except Exception as e:
        print(f"   ⚠ Could not save plot: {e}")

    # Save history as JSON
    history_json_path = os.path.join(REPORT_DIR, "training_history.json")
    with open(history_json_path, 'w') as f:
        json.dump(history, f, indent=2)


    # ═══════════════════════════════════════════════════════════════
    # 8. SAVE METADATA
    # ═══════════════════════════════════════════════════════════════

    metadata = {
        "model_type": "EfficientNet-B0 (Fine-tuned)",
        "framework": "PyTorch",
        "image_size": IMAGE_SIZE,
        "num_classes": num_classes,
        "classes": class_names,
        "pretrained": "ImageNet V2",
        "best_val_accuracy": round(best_val_acc, 4),
        "epochs_trained": len(history['train_loss']),
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "train_images": train_size,
        "val_images": val_size,
        "total_images": len(full_dataset),
    }

    meta_path = os.path.join(MODEL_DIR, "model_metadata.json")
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✅ Metadata saved: {meta_path}")


    # ═══════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════

    print("\n" + "=" * 60)
    print("  ✅ DISEASE DETECTION MODEL (EfficientNet-B0) — TRAINING COMPLETE")
    print("=" * 60)
    print(f"  Best Val Accuracy:  {best_val_acc:.4f}")
    print(f"  Epochs Trained:     {len(history['train_loss'])}")
    print(f"  Classes:            {num_classes}")
    print(f"  Total Images:       {len(full_dataset):,}")
    print("=" * 60)
    print("  📁 Files saved:")
    print(f"     Model:           {os.path.join(MODEL_DIR, 'disease_model.pth')}")
    print(f"     Class Mapping:   {class_map_path}")
    print(f"     Metadata:        {meta_path}")
    print(f"     History Plot:    {os.path.join(REPORT_DIR, 'training_history.png')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
