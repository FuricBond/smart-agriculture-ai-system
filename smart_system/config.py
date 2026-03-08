"""
Configuration — Smart Agriculture System
==========================================
Centralized paths, thresholds, model metadata, and constants
for the integrated intelligent prediction engine.

All system-wide settings are managed here for easy tuning
and maintenance.

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

import os
from typing import Dict, List, Tuple

# ═══════════════════════════════════════════════════════════════
# SYSTEM METADATA
# ═══════════════════════════════════════════════════════════════

SYSTEM_NAME = "AI-Based Crop Health and Yield Prediction System"
SYSTEM_VERSION = "2.0.0"
SYSTEM_SUBTITLE = "with Intelligent Advisory Support"
SYSTEM_AUTHOR = "Smart Agriculture AI Team"


# ═══════════════════════════════════════════════════════════════
# PROJECT ROOT
# ═══════════════════════════════════════════════════════════════

PROJECT_ROOT = r"D:\Project\CropProject"


# ═══════════════════════════════════════════════════════════════
# MODEL PATHS
# ═══════════════════════════════════════════════════════════════

# Disease Detection Model
DISEASE_MODEL_DIR   = os.path.join(PROJECT_ROOT, "disease_model", "models")
DISEASE_MODEL_PATH  = os.path.join(DISEASE_MODEL_DIR, "disease_model.pth")
DISEASE_CLASS_MAP   = os.path.join(DISEASE_MODEL_DIR, "class_names.json")
DISEASE_DATA_DIR    = os.path.join(PROJECT_ROOT, "disease_model", "data", "combined")

# Crop Recommendation Model
CROP_MODEL_DIR      = os.path.join(PROJECT_ROOT, "crop_model", "models")
CROP_MODEL_PATH     = os.path.join(CROP_MODEL_DIR, "improved_crop_model.pkl")
CROP_ENCODER_PATH   = os.path.join(CROP_MODEL_DIR, "label_encoder.pkl")

# Yield Prediction Model
YIELD_MODEL_DIR     = os.path.join(PROJECT_ROOT, "yield_model", "models")
YIELD_MODEL_PATH    = os.path.join(YIELD_MODEL_DIR, "yield_model.pkl")
YIELD_AREA_ENC_PATH = os.path.join(YIELD_MODEL_DIR, "area_encoder.pkl")
YIELD_CROP_ENC_PATH = os.path.join(YIELD_MODEL_DIR, "crop_encoder.pkl")
YIELD_META_PATH     = os.path.join(YIELD_MODEL_DIR, "model_metadata.json")


# ═══════════════════════════════════════════════════════════════
# MODEL INFORMATION (for display and evaluation)
# ═══════════════════════════════════════════════════════════════

MODEL_INFO: Dict[str, dict] = {
    'disease': {
        'name':         'Plant Disease Detector',
        'architecture': 'ResNet50 CNN (Fine-tuned)',
        'framework':    'PyTorch + Torchvision',
        'dataset':      'PlantVillage + PlantDoc + Cassava Leaf Disease',
        'dataset_size': '~115,000 images',
        'classes':      52,
        'input':        '224×224 RGB leaf image',
        'output':       'Disease class + confidence (%)',
        'pretrained':   'ImageNet V2',
    },
    'crop': {
        'name':         'Crop Recommendation Engine',
        'architecture': 'Voting Ensemble (RandomForest + XGBoost + LightGBM)',
        'framework':    'scikit-learn + XGBoost + LightGBM',
        'dataset':      'Combined Crop Recommendation Dataset',
        'dataset_size': '~6,600 samples',
        'classes':      22,
        'input':        '7 soil & weather features → 21 engineered features',
        'output':       'Recommended crop + probability (%)',
        'features':     'N, P, K, Temperature, Humidity, pH, Rainfall',
    },
    'yield': {
        'name':         'Yield Prediction Model',
        'architecture': 'RandomForestRegressor (200 trees)',
        'framework':    'scikit-learn',
        'dataset':      'Global Yield Master Dataset',
        'dataset_size': '~8.7 million records',
        'classes':      'Regression (continuous)',
        'input':        'Area, Crop, Year',
        'output':       'Predicted yield value',
        'features':     'Area_encoded, Item_encoded, Year, Decade, Years_since_2000',
    }
}


# ═══════════════════════════════════════════════════════════════
# OUTPUT PATHS
# ═══════════════════════════════════════════════════════════════

LOG_DIR     = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE    = os.path.join(LOG_DIR, "system_log.txt")
REPORT_DIR  = os.path.join(PROJECT_ROOT, "reports")


# ═══════════════════════════════════════════════════════════════
# IMAGE SETTINGS
# ═══════════════════════════════════════════════════════════════

IMAGE_SIZE:    int            = 224
IMAGENET_MEAN: List[float]    = [0.485, 0.456, 0.406]
IMAGENET_STD:  List[float]    = [0.229, 0.224, 0.225]
VALID_IMAGE_EXTENSIONS        = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}


# ═══════════════════════════════════════════════════════════════
# PREDICTION CONFIDENCE THRESHOLDS
# ═══════════════════════════════════════════════════════════════

# Disease prediction confidence levels
CONFIDENCE_HIGH:     float = 85.0   # ≥ 85 %  → reliable prediction
CONFIDENCE_MODERATE: float = 60.0   # ≥ 60 %  → acceptable, verify
CONFIDENCE_LOW:      float = 40.0   # < 40 %  → unreliable, retake image


# ═══════════════════════════════════════════════════════════════
# YIELD THRESHOLDS
# ═══════════════════════════════════════════════════════════════

YIELD_LOW_THRESHOLD:  float = 1500.0
YIELD_HIGH_THRESHOLD: float = 3000.0

# Crop-specific yield thresholds (LOW, HIGH) in kg/ha
# Keeps classification meaningful across wildly different crops
CROP_YIELD_THRESHOLDS: Dict[str, Tuple[float, float]] = {
    # _default acts as fallback
    '_default':    (1500,  3000),
    # Cereals
    'Rice':         (2000,  5000),
    'Wheat':        (2000,  4500),
    'Maize':        (2500,  6000),
    'Barley':       (1500,  4000),
    'Sorghum':      (1000,  3000),
    'Millet':       (800,   2500),
    # Legumes
    'Soybean':      (1500,  3500),
    'Chickpea':     (800,   2000),
    'Lentil':       (800,   2000),
    'Pigeonpea':    (700,   2000),
    'Groundnut':    (1000,  3000),
    # Cash Crops
    'Sugarcane':    (40000, 80000),
    'Cotton':       (1000,  3000),
    'Jute':         (1500,  3500),
    'Tobacco':      (1200,  3000),
    # Fruits / Vegetables
    'Potato':       (10000, 25000),
    'Tomato':       (15000, 40000),
    'Banana':       (10000, 35000),
    'Mango':        (5000,  15000),
    # Oilseeds
    'Rapeseed':     (1000,  2500),
    'Sunflower':    (1000,  2500),
    'Coconut':      (5000,  12000),
}

# Season mapping for Yield prediction (Y3)
SEASON_MAP: Dict[str, int] = {
    'Kharif':     1,
    'Rabi':       2,
    'Whole Year': 3,
    'Autumn':     4,
    'Summer':     5,
    'Winter':     6,
}


# ═══════════════════════════════════════════════════════════════
# SOIL QUALITY THRESHOLDS
# ═══════════════════════════════════════════════════════════════

# Ideal ranges for soil parameters (based on agronomic literature)
IDEAL_PH_MIN:       float = 6.0
IDEAL_PH_MAX:       float = 7.5
IDEAL_N_MIN:        float = 40.0
IDEAL_N_MAX:        float = 140.0
IDEAL_P_MIN:        float = 20.0
IDEAL_P_MAX:        float = 80.0
IDEAL_K_MIN:        float = 20.0
IDEAL_K_MAX:        float = 80.0
IDEAL_TEMP_MIN:     float = 18.0
IDEAL_TEMP_MAX:     float = 35.0
IDEAL_HUMIDITY_MIN: float = 40.0
IDEAL_HUMIDITY_MAX: float = 85.0
IDEAL_RAINFALL_MIN: float = 100.0
IDEAL_RAINFALL_MAX: float = 1200.0

# NPK Balance Ratios (agronomic ideal ranges)
IDEAL_NK_RATIO: Tuple[float, float] = (0.8, 3.0)    # N:K target range
IDEAL_NP_RATIO: Tuple[float, float] = (1.0, 4.0)    # N:P target range


# ═══════════════════════════════════════════════════════════════
# INPUT VALIDATION RANGES (hard limits)
# ═══════════════════════════════════════════════════════════════

INPUT_RANGES: Dict[str, Tuple[float, float, str]] = {
    'Nitrogen':    (0, 300,  'kg/ha'),
    'Phosphorus':  (0, 200,  'kg/ha'),
    'Potassium':   (0, 300,  'kg/ha'),
    'Temperature': (-10, 60, '°C'),
    'Humidity':    (0, 100,  '%'),
    'pH':          (0, 14,   ''),
    'Rainfall':    (0, 5000, 'mm'),
}


# ═══════════════════════════════════════════════════════════════
# DISPLAY LABELS
# ═══════════════════════════════════════════════════════════════

RISK_LEVELS: Dict[str, str] = {
    'LOW':      '🟢 Low',
    'MODERATE': '🟡 Moderate',
    'HIGH':     '🟠 High',
    'CRITICAL': '🔴 Critical'
}

YIELD_LEVELS: Dict[str, str] = {
    'LOW':    '🔴 Low Yield',
    'MEDIUM': '🟡 Medium Yield',
    'HIGH':   '🟢 High Yield'
}

SOIL_QUALITY_LEVELS: Dict[str, str] = {
    'POOR':      '🔴 Poor',
    'FAIR':      '🟡 Fair',
    'GOOD':      '🟢 Good',
    'EXCELLENT': '🌟 Excellent'
}

CONFIDENCE_LABELS: Dict[str, str] = {
    'HIGH':     '🟢 High Confidence',
    'MODERATE': '🟡 Moderate Confidence',
    'LOW':      '🔴 Low Confidence',
}
