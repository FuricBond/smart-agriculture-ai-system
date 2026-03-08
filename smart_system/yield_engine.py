"""
Yield Prediction Engine — Smart Agriculture System v2.0
=========================================================
Loads the trained RandomForestRegressor and predicts crop yield.
Handles both new (LabelEncoder) and legacy (get_dummies) formats.

Features
--------
    • Dual model format support (LabelEncoder / get_dummies)
    • Input validation with fuzzy-match suggestions
    • Yield level classification
    • Corrupted model detection
    • Metadata-driven feature engineering
    • Professional error handling and logging

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

from __future__ import annotations

import os
import json
import time
from typing import Dict, List, Optional

from . import config
from . import logger


class YieldEngine:
    """
    Yield Prediction Engine.

    Loads the trained RandomForestRegressor and optional
    LabelEncoders for area/crop encoding.

    Attributes
    ----------
    model : sklearn regressor or None
        The loaded prediction model.
    area_encoder : LabelEncoder or None
        Area name encoder (new format).
    crop_encoder : LabelEncoder or None
        Crop name encoder (new format).
    known_areas : list[str]
        Areas the model was trained on.
    known_crops : list[str]
        Crops the model was trained on.
    _loaded : bool
        Whether the model has been loaded.
    _use_encoders : bool
        True = new LabelEncoder format; False = legacy get_dummies.
    """

    def __init__(self) -> None:
        self.model = None
        self.area_encoder = None
        self.crop_encoder = None
        self.metadata: Dict = {}
        self.features: List[str] = []
        self.known_areas: List[str] = []
        self.known_crops: List[str] = []
        self._loaded: bool = False
        self._use_encoders: bool = True

    def load(self) -> bool:
        """
        Load the yield prediction model and encoders.

        Returns
        -------
        bool
            True if model loaded successfully.
        """
        try:
            import joblib
        except ImportError:
            logger.log_error(
                "YIELD", "Missing dependency: joblib. "
                "Install: pip install joblib")
            return False

        load_start = time.time()

        try:
            # Validate model file
            if not os.path.isfile(config.YIELD_MODEL_PATH):
                logger.log_error(
                    "YIELD",
                    f"Model not found: {config.YIELD_MODEL_PATH}")
                return False

            fsize = os.path.getsize(config.YIELD_MODEL_PATH)
            if fsize < 1024:
                logger.log_error(
                    "YIELD",
                    f"Model file appears corrupted ({fsize} bytes)")
                return False

            self.model = joblib.load(config.YIELD_MODEL_PATH)

            # ── Try to load LabelEncoders (new format) ────────
            if (os.path.isfile(config.YIELD_AREA_ENC_PATH) and
                    os.path.isfile(config.YIELD_CROP_ENC_PATH)):
                self.area_encoder = joblib.load(
                    config.YIELD_AREA_ENC_PATH)
                self.crop_encoder = joblib.load(
                    config.YIELD_CROP_ENC_PATH)
                self._use_encoders = True
                self.known_areas = self.area_encoder.classes_.tolist()
                self.known_crops = self.crop_encoder.classes_.tolist()
                logger.log_info("YIELD", "Loaded with LabelEncoders")
            else:
                self._use_encoders = False
                logger.log_warning(
                    "YIELD",
                    "Encoders not found — using legacy mode")

            # ── Load metadata ─────────────────────────────────
            if os.path.isfile(config.YIELD_META_PATH):
                with open(config.YIELD_META_PATH, 'r') as f:
                    self.metadata = json.load(f)
                self.features = self.metadata.get('features', [])
                if not self.known_areas:
                    self.known_areas = self.metadata.get('areas', [])
                if not self.known_crops:
                    self.known_crops = self.metadata.get('crops', [])

            if not self.features and self._use_encoders:
                self.features = [
                    'Area_encoded', 'Item_encoded', 'Year',
                    'Decade', 'Years_since_2000'
                ]

            self._loaded = True
            elapsed = time.time() - load_start
            logger.log_model_load("YIELD", True, elapsed)
            logger.log_info(
                "YIELD",
                f"Loaded: {len(self.known_areas)} areas, "
                f"{len(self.known_crops)} crops")
            return True

        except Exception as e:
            logger.log_error(
                "YIELD", f"Failed to load model: {str(e)}")
            return False

    def predict(
        self, area: str, crop: str, year: int, season: str = None
    ) -> Dict:
        """
        Predict crop yield for a given area, crop, and year.

        Parameters
        ----------
        area : str
            Geographic area (e.g., 'India').
        crop : str
            Crop name (e.g., 'Rice').
        year : int
            Year for prediction.

        Returns
        -------
        dict
            success         : bool
            predicted_yield : float
            yield_level     : str (LOW/MEDIUM/HIGH)
            area            : str
            crop            : str
            year            : int
            error           : str (only if success is False)
            suggestions     : list[str] (if input not found)
        """
        if not self._loaded:
            return {
                'success': False,
                'error': 'Yield model not loaded. Call load() first.'
            }

        # Normalize area and crop (case-insensitive mapping)
        if area:
            area_lower = str(area).lower().strip()
            for known in self.known_areas:
                if known.lower() == area_lower:
                    area = known
                    break

        if crop:
            crop_lower = str(crop).lower().strip()
            for known in self.known_crops:
                if known.lower() == crop_lower:
                    crop = known
                    break

        try:
            if self._use_encoders:
                return self._predict_with_encoders(area, crop, year, season)
            else:
                return self._predict_legacy(area, crop, year)
        except Exception as e:
            error_msg = f"Prediction failed: {str(e)}"
            logger.log_error("YIELD", error_msg)
            return {'success': False, 'error': error_msg}

    def _predict_with_encoders(
        self, area: str, crop: str, year: int, season: str = None
    ) -> Dict:
        """Predict using LabelEncoder-based model (new format)."""
        import pandas as pd

        # Validate area
        if area not in self.known_areas:
            suggestions = [
                a for a in self.known_areas
                if area.lower() in a.lower()
            ]
            return {
                'success': False,
                'error': f"Area '{area}' not in training data.",
                'suggestions': suggestions[:10]
            }

        # Validate crop
        if crop not in self.known_crops:
            suggestions = [
                c for c in self.known_crops
                if crop.lower() in c.lower()
            ]
            return {
                'success': False,
                'error': f"Crop '{crop}' not in training data.",
                'suggestions': suggestions[:10]
            }

        # Encode
        area_encoded = self.area_encoder.transform([area])[0]
        crop_encoded = self.crop_encoder.transform([crop])[0]

        from smart_system.config import SEASON_MAP
        season_encoded = 0
        if season and season in SEASON_MAP:
            season_encoded = SEASON_MAP[season]

        # Build feature vector
        feature_dict = {
            'Area_encoded':    area_encoded,
            'Item_encoded':    crop_encoded,
            'Year':            year,
            'Decade':          (year // 10) * 10,
            'Years_since_2000': year - 2000,
            'Season_encoded':  season_encoded,
        }

        input_df = pd.DataFrame([feature_dict])

        # Align with model features
        for f in self.features:
            if f not in input_df.columns:
                input_df[f] = 0
        input_df = input_df[self.features]

        # Predict
        predicted_yield = float(self.model.predict(input_df)[0])

        # Y1 — Uncertainty: std of individual tree predictions
        try:
            import numpy as np
            tree_preds = np.array([
                tree.predict(input_df.values)[0]
                for tree in self.model.estimators_
            ])
            yield_uncertainty = round(float(np.std(tree_preds)), 2)
        except Exception:
            yield_uncertainty = None

        yield_level = self._classify_yield(predicted_yield, crop)

        result = {
            'success':           True,
            'predicted_yield':   predicted_yield,
            'yield_uncertainty': yield_uncertainty,   # ± hg/ha
            'yield_unit':        'hg/ha',             # FAO standard
            'yield_level':       yield_level,
            'area':              area,
            'crop':              crop,
            'year':              year,
        }

        logger.log_info(
            "YIELD",
            f"Predicted: {predicted_yield:,.2f} ±{yield_uncertainty} ({yield_level})")
        return result

    def _predict_legacy(
        self, area: str, crop: str, year: int
    ) -> Dict:
        """Predict using pd.get_dummies-based model (legacy)."""
        import pandas as pd
        import numpy as np

        data = pd.DataFrame([{
            'Area': area,
            'Item': crop,
            'Year': year,
        }])

        data = pd.get_dummies(data)

        # Align with model's expected features
        try:
            expected = self.model.feature_names_in_
            for col in expected:
                if col not in data.columns:
                    data[col] = 0
            data = data[expected]
        except AttributeError:
            pass

        predicted_yield = float(self.model.predict(data)[0])

        # Y1 — Uncertainty: std of individual tree predictions (legacy path)
        try:
            tree_preds = np.array([
                tree.predict(data.values)[0]
                for tree in self.model.estimators_
            ])
            yield_uncertainty = round(float(np.std(tree_preds)), 4)
        except Exception:
            yield_uncertainty = None

        yield_level = self._classify_yield(predicted_yield, crop)

        return {
            'success':           True,
            'predicted_yield':   predicted_yield,
            'yield_uncertainty': yield_uncertainty,
            'yield_unit':        'hg/ha',     # FAO standard (hectograms per hectare)
            'yield_level':       yield_level,
            'area':              area,
            'crop':              crop,
            'year':              year,
        }

    @staticmethod
    def _classify_yield(yield_value: float, crop: str = '') -> str:
        """
        Classify yield into LOW / MEDIUM / HIGH using crop-specific
        thresholds where available, falling back to global defaults.

        Parameters
        ----------
        yield_value : float
            Predicted yield value.
        crop : str
            Crop name for crop-specific threshold lookup.

        Returns
        -------
        str
            Yield category.
        """
        thresholds = config.CROP_YIELD_THRESHOLDS
        low_t, high_t = thresholds.get(
            crop, thresholds.get('_default', (config.YIELD_LOW_THRESHOLD, config.YIELD_HIGH_THRESHOLD))
        )
        if yield_value < low_t:
            return 'LOW'
        elif yield_value > high_t:
            return 'HIGH'
        else:
            return 'MEDIUM'
