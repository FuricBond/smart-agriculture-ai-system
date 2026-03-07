"""
Crop Recommendation Model — Prediction Script
===============================================
Predicts the best crop based on soil and weather conditions
using the trained ensemble model.

Project: AI-Based Crop Health and Yield Prediction System
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

# Import shared feature engineering
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_utils import engineer_features, FEATURE_COLUMNS, validate_input


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

MODEL_PATH = r"C:\CropProject\crop_model\models\improved_crop_model.pkl"
ENCODER_PATH = r"C:\CropProject\crop_model\models\label_encoder.pkl"
TOP_K = 5


# ═══════════════════════════════════════════════════════════════
# LOAD MODEL
# ═══════════════════════════════════════════════════════════════

print("=" * 50)
print("  🌾 CROP RECOMMENDATION SYSTEM")
print("=" * 50)

try:
    model = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH)
    print("  ✅ Model loaded successfully")
except FileNotFoundError as e:
    print(f"  ❌ Error: Model file not found: {e}")
    print("  Run train_crop_model.py first.")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# GET INPUT
# ═══════════════════════════════════════════════════════════════

print("\n📋 Enter soil and weather conditions:\n")

try:
    N = float(input("   Nitrogen (N):     "))
    P = float(input("   Phosphorus (P):   "))
    K = float(input("   Potassium (K):    "))
    temp = float(input("   Temperature (°C): "))
    humidity = float(input("   Humidity (%):     "))
    ph = float(input("   pH:               "))
    rainfall = float(input("   Rainfall (mm):    "))
except ValueError:
    print("\n  ❌ Error: Please enter valid numeric values.")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# VALIDATE INPUT
# ═══════════════════════════════════════════════════════════════

raw_input = {
    'Nitrogen': N,
    'Phosphorus': P,
    'Potassium': K,
    'Temperature': temp,
    'Humidity': humidity,
    'pH': ph,
    'Rainfall': rainfall
}

input_warnings = validate_input(raw_input)
if input_warnings:
    print("\n⚠ Input Warnings:")
    for w in input_warnings:
        print(f"   {w}")


# ═══════════════════════════════════════════════════════════════
# BUILD FEATURE VECTOR
# ═══════════════════════════════════════════════════════════════

data = pd.DataFrame([raw_input])
data = engineer_features(data)
data = data[FEATURE_COLUMNS]


# ═══════════════════════════════════════════════════════════════
# PREDICT
# ═══════════════════════════════════════════════════════════════

prediction_encoded = model.predict(data)
prediction = le.inverse_transform(prediction_encoded)

probabilities = model.predict_proba(data)[0]
classes = le.classes_

# Top-K predictions
prob_df = pd.DataFrame({
    'Crop': classes,
    'Probability': probabilities
}).sort_values('Probability', ascending=False).head(TOP_K)


# ═══════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 50)
print(f"  🌱 RECOMMENDED CROP: {prediction[0]}")
print(f"  📊 Confidence: {prob_df.iloc[0]['Probability'] * 100:.1f}%")
print("=" * 50)

print(f"\n  Top {TOP_K} Predictions:")
print(f"  {'─' * 40}")

for rank, (_, row) in enumerate(prob_df.iterrows(), 1):
    bar_len = int(row['Probability'] * 30)
    bar = '█' * bar_len + '░' * (30 - bar_len)
    print(f"   {rank}. {row['Crop']:<20} {row['Probability']*100:5.1f}%  {bar}")

print(f"\n  {'─' * 40}")
print(f"  Input Summary: N={N} P={P} K={K} T={temp}°C")
print(f"                 H={humidity}% pH={ph} R={rainfall}mm")
print("=" * 50)