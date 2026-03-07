"""
Yield Prediction Model — Prediction Script
=============================================
Predicts crop yield for a given area, crop, and year
using the trained RandomForestRegressor.

Project: AI-Based Crop Health and Yield Prediction System
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
import warnings

warnings.filterwarnings('ignore')


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

MODEL_DIR = r"C:\CropProject\yield_model\models"
MODEL_PATH = os.path.join(MODEL_DIR, "yield_model.pkl")
AREA_ENC_PATH = os.path.join(MODEL_DIR, "area_encoder.pkl")
CROP_ENC_PATH = os.path.join(MODEL_DIR, "crop_encoder.pkl")
META_PATH = os.path.join(MODEL_DIR, "model_metadata.json")


# ═══════════════════════════════════════════════════════════════
# LOAD MODEL AND ENCODERS
# ═══════════════════════════════════════════════════════════════

print("=" * 55)
print("  📊 YIELD PREDICTION SYSTEM")
print("=" * 55)

try:
    model = joblib.load(MODEL_PATH)
    area_encoder = joblib.load(AREA_ENC_PATH)
    crop_encoder = joblib.load(CROP_ENC_PATH)
    print("  ✅ Model and encoders loaded successfully")
except FileNotFoundError as e:
    print(f"  ❌ Error: File not found: {e}")
    print("  Run train_yield_model.py first.")
    sys.exit(1)

# Load metadata for feature list and validation
try:
    with open(META_PATH, 'r') as f:
        metadata = json.load(f)
    features = metadata.get('features', [])
    known_areas = metadata.get('areas', [])
    known_crops = metadata.get('crops', [])
    year_range = metadata.get('year_range', [1900, 2030])
except (FileNotFoundError, json.JSONDecodeError):
    print("  ⚠ Metadata not found — using defaults")
    features = ['Area_encoded', 'Item_encoded', 'Year', 'Decade', 'Years_since_2000']
    known_areas = area_encoder.classes_.tolist()
    known_crops = crop_encoder.classes_.tolist()
    year_range = [1900, 2030]


# ═══════════════════════════════════════════════════════════════
# GET USER INPUT
# ═══════════════════════════════════════════════════════════════

print(f"\n  Available Areas: {len(known_areas)} regions")
print(f"  Available Crops: {len(known_crops)} crop types")
print(f"  Year Range:      {year_range[0]} — {year_range[1]}")

print(f"\n📋 Enter prediction parameters:\n")

# Area input
area_input = input("   Area (e.g., India): ").strip()

# Validate area
if area_input not in known_areas:
    print(f"\n  ⚠ Area '{area_input}' not found in training data.")
    # Find close matches
    matches = [a for a in known_areas if area_input.lower() in a.lower()]
    if matches:
        print(f"  Did you mean one of these?")
        for m in matches[:10]:
            print(f"    - {m}")
    else:
        print(f"  Available areas (first 20):")
        for a in sorted(known_areas)[:20]:
            print(f"    - {a}")
    sys.exit(1)

# Crop input
crop_input = input("   Crop (e.g., Rice): ").strip()

# Validate crop
if crop_input not in known_crops:
    print(f"\n  ⚠ Crop '{crop_input}' not found in training data.")
    matches = [c for c in known_crops if crop_input.lower() in c.lower()]
    if matches:
        print(f"  Did you mean one of these?")
        for m in matches[:10]:
            print(f"    - {m}")
    else:
        print(f"  Available crops (first 20):")
        for c in sorted(known_crops)[:20]:
            print(f"    - {c}")
    sys.exit(1)

# Year input
try:
    year_input = int(input("   Year (e.g., 2020): ").strip())
except ValueError:
    print("\n  ❌ Error: Please enter a valid year.")
    sys.exit(1)

if year_input < year_range[0] or year_input > year_range[1] + 10:
    print(f"\n  ⚠ Year {year_input} is outside training range "
          f"({year_range[0]}–{year_range[1]}). Predictions may be less reliable.")


# ═══════════════════════════════════════════════════════════════
# BUILD FEATURE VECTOR
# ═══════════════════════════════════════════════════════════════

area_encoded = area_encoder.transform([area_input])[0]
crop_encoded = crop_encoder.transform([crop_input])[0]

feature_dict = {
    'Area_encoded': area_encoded,
    'Item_encoded': crop_encoded,
    'Year': year_input,
    'Decade': (year_input // 10) * 10,
    'Years_since_2000': year_input - 2000,
}

# Build DataFrame with exactly the features the model expects
input_df = pd.DataFrame([feature_dict])

# Only include features that exist in metadata
available_features = [f for f in features if f in input_df.columns]
if len(available_features) < len(features):
    # Some features (like Rainfall, Temperature) may not be provided
    missing = set(features) - set(available_features)
    for mf in missing:
        input_df[mf] = 0  # Default to 0 for missing optional features
    available_features = features

input_df = input_df[features]


# ═══════════════════════════════════════════════════════════════
# PREDICT
# ═══════════════════════════════════════════════════════════════

predicted_yield = model.predict(input_df)[0]


# ═══════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 55)
print(f"  📊 YIELD PREDICTION RESULTS")
print("=" * 55)
print(f"\n  Area:             {area_input}")
print(f"  Crop:             {crop_input}")
print(f"  Year:             {year_input}")
print(f"\n  ────────────────────────────────────")
print(f"  🌾 Predicted Yield: {predicted_yield:,.2f}")
print(f"  ────────────────────────────────────")

# Model confidence info
if 'test_r2' in metadata:
    print(f"\n  Model Performance:")
    print(f"    R² Score:  {metadata['test_r2']}")
    print(f"    MAE:       {metadata.get('test_mae', 'N/A')}")

print("\n" + "=" * 55)
