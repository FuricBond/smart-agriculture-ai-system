"""
Ensemble Predictor — Plant Doctor Integration Module v3.1
==========================================================
Bridges EnsembleEngine (v3.1) with PlantDoctorPipeline Stage 2.

Changes from v3.0
-----------------
  • Surfaces all new EnsembleEngine v3.1 metadata:
      model_confidences, disagreement_detected, entropy,
      unknown_reason, early_exit_triggered
  • top_predictions passed as list-of-dicts AND legacy tuples
  • Confidence tier now also considers disagreement downgrade

Author  : Smart Agriculture AI Team
Version : 3.1.0
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger("plant_doctor.ensemble_predictor")


class EnsemblePredictor:
    """
    predict() adapter: EnsembleEngine → PlantDoctorPipeline Stage 2 format.

    Stage 2 expected output
    -----------------------
    {
        "success":          bool,
        "disease_name":     str,
        "plant":            str,
        "condition":        str,
        "confidence":       float,   # percentage 0–100
        "confidence_level": str,     # HIGH / MODERATE / LOW
        "top_predictions":  list[(name, conf_pct)],  # legacy tuple format
        "image_path":       str,
        "ensemble_meta":    dict,    # all ensemble-specific metadata
    }

    Grad-CAM is always generated from EfficientNet-B0 only (Stage 7).
    This class never touches heatmap generation.
    """

    HIGH_THRESHOLD:     float = 85.0
    MODERATE_THRESHOLD: float = 60.0

    def __init__(self, ensemble_engine) -> None:
        self.ensemble = ensemble_engine

    def predict(self, image_path: str, top_k: int = 5) -> Dict:
        """
        Run ensemble inference and return a pipeline-compatible result.

        Translates EnsembleEngine.predict() output into Stage 2 format,
        including all v3.1 metadata fields for debugging and UI rendering.
        """
        raw = self.ensemble.predict(image_path, top_k=top_k)

        if not raw.get("success"):
            return {
                "success": False,
                "error":   raw.get("error", "Ensemble prediction failed"),
            }

        disease_name = raw["disease_name"]        # raw CNN label (always top class)
        prediction   = raw["prediction"]          # may be "Unknown Disease"
        confidence   = raw["confidence"]          # percentage

        # ── Parse plant / condition from label ────────────────
        plant, condition = self._parse_label(disease_name)

        # ── Confidence tier ───────────────────────────────────
        # Respect downgraded confidence from disagreement detection
        if confidence >= self.HIGH_THRESHOLD:
            confidence_level = "HIGH"
        elif confidence >= self.MODERATE_THRESHOLD:
            confidence_level = "MODERATE"
        else:
            confidence_level = "LOW"

        if raw.get("is_unknown"):
            logger.info(
                f"EnsemblePredictor open-set: prediction='{prediction}' "
                f"label='{disease_name}' conf={confidence:.1f}% "
                f"reason={raw.get('unknown_reason','?')}"
            )

        # ── Pass both list-of-dict and legacy tuple formats ───
        # Pipeline Stage 3 (ConfidenceCalibrator) and Stage 6 (Top-K)
        # still use the legacy tuple format. New UI consumers get dicts.
        top_predictions_tuples = raw.get("top_predictions_tuples") or [
            (d["label"], d["confidence_pct"])
            for d in raw.get("top_predictions", [])
        ]
        top_predictions_dicts = raw.get("top_predictions", [])

        ensemble_meta = {
            # Core flags
            "is_unknown":            raw.get("is_unknown", False),
            "unknown_detected":      raw.get("unknown_detected", False),
            "unknown_reason":        raw.get("unknown_reason", ""),
            "used_ensemble":         raw.get("used_ensemble", False),
            "early_exit_triggered":  raw.get("early_exit_triggered", False),
            # Quality signals
            "disagreement_detected": raw.get("disagreement_detected", False),
            "entropy":               raw.get("entropy", 0.0),
            "confidence_raw":        raw.get("confidence_raw", 0.0),
            # Per-model breakdown
            "model_confidences":     raw.get("model_confidences", {}),
            "ensemble_weights":      raw.get("ensemble_weights", {}),
            # Rich top-K for UI
            "top_predictions_dict":  top_predictions_dicts,
        }

        logger.info(
            f"EnsemblePredictor: '{prediction}' ({confidence:.1f}%, {confidence_level}) "
            f"ensemble={ensemble_meta['used_ensemble']} "
            f"early_exit={ensemble_meta['early_exit_triggered']} "
            f"unknown={ensemble_meta['is_unknown']} "
            f"disagreement={ensemble_meta['disagreement_detected']} "
            f"entropy={ensemble_meta['entropy']:.3f}"
        )

        return {
            "success":          True,
            "disease_name":     disease_name,
            "plant":            plant,
            "condition":        condition,
            "confidence":       confidence,
            "confidence_level": confidence_level,
            "top_predictions":  top_predictions_tuples,   # legacy compat
            "image_path":       image_path,
            "ensemble_meta":    ensemble_meta,
        }

    @staticmethod
    def _parse_label(label: str) -> Tuple[str, str]:
        """
        Parse 'Plant___Condition_Name' → ('Plant', 'Condition Name').
        """
        parts = label.split("___")
        if len(parts) >= 2:
            return parts[0].replace("_", " ").strip(), parts[1].replace("_", " ").strip()
        if len(parts) == 1:
            return "Unknown", parts[0].replace("_", " ").strip()
        return "Unknown", "Unknown"
