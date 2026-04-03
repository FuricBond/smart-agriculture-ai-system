"""
yield_predictor/features.py
============================
Feature engineering for the XGBoost Yield Prediction model.

Model expects these features in EXACT order:
    ['Area_encoded', 'Item_encoded', 'Year', 'Decade',
     'Years_since_2000', 'Season_encoded']

This module encodes inputs and constructs the feature DataFrame.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import pandas as pd

logger = logging.getLogger("agri_api")

# Feature order MUST match model training — sourced from model_metadata.json
MODEL_FEATURE_ORDER: List[str] = [
    "Area_encoded",
    "Item_encoded",
    "Year",
    "Decade",
    "Years_since_2000",
    "Season_encoded",
]

# Season encoding — matches model_metadata.json season_map exactly
SEASON_MAP: Dict[str, int] = {
    "Kharif":     1,
    "Rabi":       2,
    "Whole Year": 3,
    "Autumn":     4,
    "Summer":     5,
    "Winter":     6,
}


def encode_area(area_encoder, state: str) -> Tuple[int, bool, List[str]]:
    """
    Encode state with LabelEncoder.

    Returns
    -------
    (encoded_value, success, suggestions)
    """
    known_areas: List[str] = area_encoder.classes_.tolist()

    # Case-insensitive lookup
    state_lower = state.strip().lower()
    matched = next(
        (a for a in known_areas if a.lower() == state_lower), None
    )

    if matched is None:
        suggestions = [a for a in known_areas if state_lower in a.lower()]
        return 0, False, suggestions[:10]

    encoded = int(area_encoder.transform([matched])[0])
    return encoded, True, []


def encode_crop(crop_encoder, crop: str) -> Tuple[int, bool, List[str]]:
    """
    Encode crop with LabelEncoder.

    Returns
    -------
    (encoded_value, success, suggestions)
    """
    known_crops: List[str] = crop_encoder.classes_.tolist()

    crop_lower = crop.strip().lower()
    matched = next(
        (c for c in known_crops if c.lower() == crop_lower), None
    )

    if matched is None:
        suggestions = [c for c in known_crops if crop_lower in c.lower()]
        return 0, False, suggestions[:10]

    encoded = int(crop_encoder.transform([matched])[0])
    return encoded, True, []


def build_feature_vector(
    area_encoded:  int,
    crop_encoded:  int,
    year:          int,
    season:        str,
) -> pd.DataFrame:
    """
    Build a single-row DataFrame with features in the exact order the
    XGBoost model was trained on.

    Parameters
    ----------
    area_encoded : int
        LabelEncoder output for the state/area.
    crop_encoded : int
        LabelEncoder output for the crop.
    year : int
        Prediction year.
    season : str
        Season string, e.g. 'Kharif'.

    Returns
    -------
    pd.DataFrame
        One row, columns = MODEL_FEATURE_ORDER.
    """
    decade          = (year // 10) * 10
    years_since_2000 = year - 2000
    season_encoded  = SEASON_MAP.get(season, 0)

    feature_dict = {
        "Area_encoded":     area_encoded,
        "Item_encoded":     crop_encoded,
        "Year":             year,
        "Decade":           decade,
        "Years_since_2000": years_since_2000,
        "Season_encoded":   season_encoded,
    }

    df = pd.DataFrame([feature_dict])

    # Ensure all expected columns exist and are in correct order
    for col in MODEL_FEATURE_ORDER:
        if col not in df.columns:
            df[col] = 0

    return df[MODEL_FEATURE_ORDER]
