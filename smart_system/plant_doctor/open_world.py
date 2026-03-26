"""
Open-World Detection — Unknown Disease Detector
====================================================
Detects when the model encounters a disease it was NOT trained on.

If the maximum prediction confidence falls below a configurable
threshold, the system flags the result as "Unknown Disease"
instead of returning a potentially wrong classification.

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("plant_doctor.open_world")


# ═══════════════════════════════════════════════════════════════
# CONFIGURABLE THRESHOLDS
# ═══════════════════════════════════════════════════════════════

# If top confidence is below this (percentage 0–100), mark as "Unknown"
UNKNOWN_THRESHOLD: float = 60.0

# If the gap between top-1 and top-2 is less than this,
# it signals confusion / ambiguity
AMBIGUITY_GAP: float = 10.0

# Entropy threshold (higher entropy = more uncertain)
ENTROPY_THRESHOLD: float = 2.0


class OpenWorldDetector:
    """
    Flags predictions as 'Known' or 'Unknown' based on
    confidence analysis.

    Parameters
    ----------
    confidence_threshold : float
        Minimum confidence (0–100) for a prediction to be
        considered 'Known'.
    ambiguity_gap : float
        Minimum gap (in %) between top-1 and top-2 confidence.
    """

    def __init__(
        self,
        confidence_threshold: float = UNKNOWN_THRESHOLD,
        ambiguity_gap: float = AMBIGUITY_GAP,
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.ambiguity_gap = ambiguity_gap

    def detect(
        self,
        top_predictions: List[Tuple[str, float]],
    ) -> Dict:
        """
        Analyze the prediction distribution for open-world signals.

        Parameters
        ----------
        top_predictions : list of (class_name, confidence_%)
            The model's top-K predictions with confidence scores.

        Returns
        -------
        dict
            status      : str    — 'Known' or 'Unknown'
            reason      : str    — Human-readable explanation
            max_conf    : float  — Top-1 confidence
            conf_gap    : float  — Confidence gap between top-1 and top-2
            is_ambiguous: bool   — True if predictions are too close
        """
        if not top_predictions:
            return {
                "status": "Unknown",
                "reason": "No predictions available",
                "max_conf": 0.0,
                "conf_gap": 0.0,
                "is_ambiguous": False,
            }

        top_conf = top_predictions[0][1]
        second_conf = top_predictions[1][1] if len(top_predictions) > 1 else 0.0
        conf_gap = top_conf - second_conf

        # ── Decision logic ────────────────────────────────────
        is_ambiguous = conf_gap < self.ambiguity_gap

        if top_conf < self.confidence_threshold:
            status = "Unknown"
            reason = (
                f"Max confidence ({top_conf:.1f}%) is below the threshold "
                f"({self.confidence_threshold:.0f}%). "
                f"This may be an unknown or unseen disease."
            )
            logger.warning(
                f"Open-world detection triggered: conf={top_conf:.1f}%, "
                f"threshold={self.confidence_threshold}%"
            )
        elif is_ambiguous:
            status = "Known"
            reason = (
                f"Prediction is classified, but top-2 predictions are very "
                f"close (gap: {conf_gap:.1f}%). Consider manual verification."
            )
            logger.info(
                f"Ambiguous prediction: top={top_conf:.1f}%, "
                f"gap={conf_gap:.1f}%"
            )
        else:
            status = "Known"
            reason = (
                f"High-confidence prediction ({top_conf:.1f}%) with clear "
                f"separation from alternatives (gap: {conf_gap:.1f}%)."
            )

        return {
            "status": status,
            "reason": reason,
            "max_conf": round(top_conf, 2),
            "conf_gap": round(conf_gap, 2),
            "is_ambiguous": is_ambiguous,
        }
