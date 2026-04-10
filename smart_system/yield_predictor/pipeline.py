"""
yield_predictor/pipeline.py
============================
Core Yield Prediction Pipeline — Phase 1.

Flow:
    YieldInput → Weather Fetch → Feature Engineering → XGBoost → Result

Usage
-----
    from smart_system.yield_predictor.pipeline import YieldPipeline

    pipeline = YieldPipeline()
    pipeline.load(model, area_encoder, crop_encoder)
    result = pipeline.predict(yield_input)
"""

from __future__ import annotations

import logging
from typing import Dict

from .schema  import YieldInput
from .weather import get_weather
from .features import encode_area, encode_crop, build_feature_vector

logger = logging.getLogger("agri_api")


class YieldPipeline:
    """
    Stateless yield prediction pipeline backed by a pre-loaded XGBoost model.

    The object holds references to the model and encoders that were loaded
    at API startup via YieldEngine — no additional I/O at prediction time.
    """

    def __init__(self) -> None:
        self._model        = None
        self._area_encoder = None
        self._crop_encoder = None
        self._loaded       = False

    # ──────────────────────────────────────────────────────────────────
    # Initialisation
    # ──────────────────────────────────────────────────────────────────

    def load(self, model, area_encoder, crop_encoder) -> None:
        """
        Bind the already-loaded XGBoost model and LabelEncoders.

        Called once at API startup after YieldEngine.load() succeeds.
        """
        self._model        = model
        self._area_encoder = area_encoder
        self._crop_encoder = crop_encoder
        self._loaded       = True
        logger.info("YieldPipeline loaded [OK]")

    # ──────────────────────────────────────────────────────────────────
    # Prediction
    # ──────────────────────────────────────────────────────────────────

    def predict(self, payload: YieldInput) -> Dict:
        """
        Run the full Phase-1 pipeline.

        Parameters
        ----------
        payload : YieldInput
            Validated Pydantic input (crop, state, season, year).

        Returns
        -------
        dict
            success         : bool
            predicted_yield : float   (hg/ha, FAO standard)
            yield_unit      : str
            yield_level     : str     (LOW / MEDIUM / HIGH)
            weather         : dict    (temperature, rainfall, humidity, source)
            area            : str     (resolved canonical area name)
            crop            : str     (resolved canonical crop name)
            season          : str
            year            : int
            error           : str     (only on failure)
            suggestions     : list    (only when area/crop not found)
        """
        if not self._loaded:
            return {"success": False, "error": "YieldPipeline not loaded."}

        crop   = payload.crop
        state  = payload.state
        season = payload.season
        year   = payload.year

        # ── Step 1: Encode area ───────────────────────────────────────
        area_encoded, area_ok, area_suggestions = encode_area(
            self._area_encoder, state
        )
        if not area_ok:
            return {
                "success":     False,
                "error":       f"State '{state}' not found in training data.",
                "suggestions": area_suggestions,
            }

        # Resolve canonical area name from encoder
        canonical_area = self._area_encoder.inverse_transform([area_encoded])[0]

        # ── Step 2: Encode crop ───────────────────────────────────────
        crop_encoded, crop_ok, crop_suggestions = encode_crop(
            self._crop_encoder, crop
        )
        if not crop_ok:
            return {
                "success":     False,
                "error":       f"Crop '{crop}' not found in training data.",
                "suggestions": crop_suggestions,
            }

        canonical_crop = self._crop_encoder.inverse_transform([crop_encoded])[0]

        # ── Step 3: Fetch weather ─────────────────────────────────────
        weather = get_weather(state, year)

        # ── Step 4: Build feature vector ──────────────────────────────
        input_df = build_feature_vector(
            area_encoded  = area_encoded,
            crop_encoded  = crop_encoded,
            year          = year,
            season        = season,
        )

        # ── Step 5: Model prediction ──────────────────────────────────
        predicted_yield = float(self._model.predict(input_df)[0])

        # ── Step 6: Classify yield level ──────────────────────────────
        yield_level = _classify_yield(predicted_yield, canonical_crop)

        logger.info(
            f"YieldPipeline | {canonical_area} | {canonical_crop} | "
            f"{year} | {season} → {predicted_yield:,.2f} hg/ha ({yield_level})"
        )

        return {
            "success":         True,
            "predicted_yield": round(predicted_yield, 2),
            "yield_unit":      "hg/ha",
            "yield_level":     yield_level,
            "weather":         weather,
            "area":            canonical_area,
            "crop":            canonical_crop,
            "season":          season,
            "year":            year,
        }

    # ──────────────────────────────────────────────────────────────────
    # Phase 2 — Prediction + Intelligence (non-destructive extension)
    # ──────────────────────────────────────────────────────────────────

    def predict_full(self, payload: YieldInput) -> Dict:
        """
        Run Phase 1 → Phase 2 → Phase 3 pipeline (fully additive).

        Phase 1 (predict)          — XGBoost yield prediction
        Phase 2 (build_intelligence) — explanation, recommendations, risk
        Phase 3 (build_context)    — comparison, trend, alerts

        Each phase is isolated; failures are caught and logged without
        breaking earlier phases.

        Returns
        -------
        dict
            All Phase-1 fields PLUS:
            intelligence : dict  — explanation, recommendations, risk
            comparison   : dict  — vs regional average
            trend        : dict  — 5-year historical trend + insight
            alerts       : list  — severity-ranked smart alerts
        """
        # ── Phase 1 (untouched) ───────────────────────────────────────
        phase1 = self.predict(payload)

        if not phase1.get("success"):
            return phase1          # propagate Phase-1 errors as-is

        # ── Phase 2 — Intelligence (additive only) ────────────────────
        try:
            from .intelligence import build_intelligence
            intel = build_intelligence(phase1)
        except Exception as exc:
            logger.error(f"Intelligence layer failed: {exc}")
            intel = {"error": str(exc)}

        # Assemble Phase 1 + 2 result (Phase 3 needs both)
        p1_p2 = {**phase1, "intelligence": intel}

        # ── Phase 3 — Context (additive only) ────────────────────────
        try:
            from .context import build_context
            ctx = build_context(p1_p2)
        except Exception as exc:
            logger.error(f"Context layer failed: {exc}")
            ctx = {"error": str(exc)}

        return {
            **p1_p2,
            "comparison": ctx.get("comparison", {}),
            "trend":      ctx.get("trend", {}),
            "alerts":     ctx.get("alerts", []),
        }


# ── Yield Level Classification ────────────────────────────────────────────────

# Thresholds in hg/ha (FAO standard unit used by the model)
_CROP_THRESHOLDS: Dict[str, tuple] = {
    "_default":    (15000, 30000),
    "Rice":        (20000, 50000),
    "Wheat":       (20000, 45000),
    "Maize":       (25000, 60000),
    "Barley":      (15000, 40000),
    "Sugarcane":   (400000, 800000),
    "Cotton(lint)":(10000, 30000),
    "Potato":      (100000, 250000),
    "Banana":      (100000, 350000),
    "Groundnut":   (10000, 30000),
    "Soyabean":    (10000, 25000),
    "Sunflower":   (8000,  20000),
    "Coconut":     (50000, 120000),
}


def _classify_yield(yield_value: float, crop: str = "") -> str:
    """Return LOW / MEDIUM / HIGH based on crop-specific thresholds."""
    low_t, high_t = _CROP_THRESHOLDS.get(crop, _CROP_THRESHOLDS["_default"])
    if yield_value < low_t:
        return "LOW"
    elif yield_value > high_t:
        return "HIGH"
    return "MEDIUM"
