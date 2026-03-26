"""
Build FAISS Index — Offline Utility Script
=============================================
Extracts feature vectors from all disease training images
and builds a FAISS index for similarity search.

Usage
-----
    python build_faiss_index.py

    Or from project root:
    python -m smart_system.plant_doctor.build_faiss_index

This only needs to be run ONCE after training the model.
The resulting index is saved to:
    disease_model/models/faiss_index/

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

import os
import sys
import json

# ── Add project root to path ─────────────────────────────────
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from smart_system.disease_engine import DiseaseEngine
from smart_system.plant_doctor.similarity import DiseaseSimilaritySearch


def main():
    print("=" * 60)
    print("  🔍 FAISS INDEX BUILDER — Disease Similarity Search")
    print("=" * 60)

    # 1. Load the disease engine
    print("\n  Loading disease model...")
    engine = DiseaseEngine()
    if not engine.load():
        print("  ❌ Failed to load disease model. Exiting.")
        sys.exit(1)

    print(f"  ✅ Model loaded: {engine._architecture}")
    print(f"  ✅ Classes: {engine.num_classes}")

    # 2. Find the dataset directory
    from smart_system import config
    data_dir = config.DISEASE_DATA_DIR

    if not os.path.isdir(data_dir):
        print(f"\n  ❌ Dataset directory not found: {data_dir}")
        print("  Please ensure disease training images are available.")
        print("  Expected structure: data_dir/ClassName/image.jpg")
        sys.exit(1)

    # Count images
    total_images = 0
    class_count = 0
    for class_name in os.listdir(data_dir):
        class_dir = os.path.join(data_dir, class_name)
        if os.path.isdir(class_dir):
            class_count += 1
            imgs = [
                f for f in os.listdir(class_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]
            total_images += len(imgs)

    print(f"\n  📁 Dataset: {data_dir}")
    print(f"     Classes: {class_count}")
    print(f"     Images:  {total_images}")

    # 3. Build the index
    output_dir = os.path.join(
        config.DISEASE_MODEL_DIR, "faiss_index"
    )

    print(f"\n  Building FAISS index (max 50 images/class)...")
    print(f"  Output: {output_dir}")
    print(f"  This may take a few minutes...\n")

    success = DiseaseSimilaritySearch.build_index(
        model=engine.model,
        architecture=engine._architecture,
        device=engine.device,
        transform=engine.transform,
        data_dir=data_dir,
        output_dir=output_dir,
        class_names=engine.class_names,
        max_per_class=50,
    )

    if success:
        print("\n  ✅ FAISS index built successfully!")
        print(f"     Index: {os.path.join(output_dir, 'disease_features.index')}")
        print(f"     Meta:  {os.path.join(output_dir, 'disease_metadata.json')}")
    else:
        print("\n  ❌ Failed to build FAISS index.")
        sys.exit(1)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
