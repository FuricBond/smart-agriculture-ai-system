"""
Feature Engineering Utilities for Crop Recommendation Model
============================================================
Shared module ensuring consistent feature engineering between
training and prediction pipelines.

Project: AI-Based Crop Health and Yield Prediction System
"""

import numpy as np
import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering transformations to input data.
    
    This function is used by BOTH the training script and the prediction
    script to guarantee identical feature transformations.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: Nitrogen, Phosphorus, Potassium,
        Temperature, Humidity, pH, Rainfall
    
    Returns
    -------
    pd.DataFrame
        DataFrame with all original + engineered features.
    """
    df = df.copy()
    
    # ── Nutrient Ratios ──────────────────────────────────────
    df['N_P_ratio'] = df['Nitrogen'] / (df['Phosphorus'] + 1e-5)
    df['N_K_ratio'] = df['Nitrogen'] / (df['Potassium'] + 1e-5)
    df['P_K_ratio'] = df['Phosphorus'] / (df['Potassium'] + 1e-5)
    
    # ── Log Transforms ───────────────────────────────────────
    df['log_rainfall'] = np.log1p(df['Rainfall'])
    df['log_humidity'] = np.log1p(df['Humidity'])
    
    # ── Interaction Features ─────────────────────────────────
    df['temp_humidity'] = df['Temperature'] * df['Humidity']
    df['temp_rainfall'] = df['Temperature'] * df['Rainfall']
    df['humidity_rainfall'] = df['Humidity'] * df['Rainfall']
    
    # ── Composite Soil Index ─────────────────────────────────
    df['soil_index'] = (
        df['Nitrogen'] * df['Phosphorus'] * df['Potassium']
    ) / 1000.0
    
    # ── Stress Indicators ────────────────────────────────────
    df['heat_stress'] = (df['Temperature'] > 32).astype(int)
    df['drought_stress'] = (df['Rainfall'] < 80).astype(int)
    
    # ── Soil pH Categories ───────────────────────────────────
    df['acidic_soil'] = (df['pH'] < 6).astype(int)
    df['neutral_soil'] = ((df['pH'] >= 6) & (df['pH'] <= 7.5)).astype(int)
    df['alkaline_soil'] = (df['pH'] > 7.5).astype(int)
    
    return df


# Feature column order (for consistency)
FEATURE_COLUMNS = [
    'Nitrogen', 'Phosphorus', 'Potassium',
    'Temperature', 'Humidity', 'pH', 'Rainfall',
    'N_P_ratio', 'N_K_ratio', 'P_K_ratio',
    'log_rainfall', 'log_humidity',
    'temp_humidity', 'temp_rainfall', 'humidity_rainfall',
    'soil_index',
    'heat_stress', 'drought_stress',
    'acidic_soil', 'neutral_soil', 'alkaline_soil'
]

RAW_FEATURE_COLUMNS = [
    'Nitrogen', 'Phosphorus', 'Potassium',
    'Temperature', 'Humidity', 'pH', 'Rainfall'
]


def validate_input(data: dict) -> list:
    """
    Validate raw input values and return a list of warnings.
    
    Parameters
    ----------
    data : dict
        Dictionary with keys matching RAW_FEATURE_COLUMNS.
    
    Returns
    -------
    list of str
        List of warning messages (empty if all inputs are valid).
    """
    warnings = []
    
    ranges = {
        'Nitrogen':    (0, 300,  'kg/ha'),
        'Phosphorus':  (0, 200,  'kg/ha'),
        'Potassium':   (0, 300,  'kg/ha'),
        'Temperature': (0, 55,   '°C'),
        'Humidity':    (0, 100,  '%'),
        'pH':          (0, 14,   ''),
        'Rainfall':    (0, 3000, 'mm'),
    }
    
    for feature, (low, high, unit) in ranges.items():
        val = data.get(feature)
        if val is None:
            warnings.append(f"⚠ Missing value for {feature}")
        elif val < low or val > high:
            unit_str = f" {unit}" if unit else ""
            warnings.append(
                f"⚠ {feature}={val} is outside typical range "
                f"[{low}–{high}{unit_str}]"
            )
    
    return warnings
