"""
Severity Estimator — Disease Severity Module
================================================
Uses the Grad-CAM heatmap to estimate what percentage of the
leaf area is infected, then categorizes the severity level.

Severity Levels
---------------
  •  0–20 %  → Low
  • 20–50 %  → Moderate
  • 50 %+    → Severe

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import numpy as np

logger = logging.getLogger("plant_doctor.severity")


# ═══════════════════════════════════════════════════════════════
# CONFIGURABLE THRESHOLDS
# ═══════════════════════════════════════════════════════════════

# Heatmap activation above this value is considered "infected"
ACTIVATION_THRESHOLD: float = 0.4

# Severity level boundaries (in percentage of infected area)
SEVERITY_LOW_MAX: float = 20.0
SEVERITY_MODERATE_MAX: float = 50.0

SEVERITY_LEVELS: Dict[str, Tuple[float, float]] = {
    "Low":      (0.0,  SEVERITY_LOW_MAX),
    "Moderate": (SEVERITY_LOW_MAX, SEVERITY_MODERATE_MAX),
    "Severe":   (SEVERITY_MODERATE_MAX, 100.0),
}


class SeverityEstimator:
    """
    Estimates disease severity from a Grad-CAM heatmap.

    The heatmap highlights the regions the model considers most
    relevant for its prediction. High-activation areas are treated
    as infected regions.

    Parameters
    ----------
    activation_threshold : float
        Pixel activation value (0–1) above which a region is
        considered infected.
    """

    def __init__(
        self,
        activation_threshold: float = ACTIVATION_THRESHOLD,
    ) -> None:
        self.activation_threshold = activation_threshold

    def estimate(self, heatmap: np.ndarray) -> Dict:
        """
        Calculate infected area percentage and severity level.

        Parameters
        ----------
        heatmap : np.ndarray
            Normalized Grad-CAM heatmap (H, W) with values in [0, 1].

        Returns
        -------
        dict
            percentage : float  — Infected area as % of total
            level      : str    — 'Low', 'Moderate', or 'Severe'
            pixel_stats : dict  — Detailed pixel-level statistics
        """
        if heatmap is None or heatmap.size == 0:
            logger.warning("Empty heatmap received for severity estimation")
            return {
                "percentage": 0.0,
                "level": "Unknown",
                "pixel_stats": {},
            }

        total_pixels = heatmap.size
        infected_mask = heatmap >= self.activation_threshold
        infected_pixels = int(np.sum(infected_mask))
        infected_percentage = round(
            (infected_pixels / total_pixels) * 100, 1
        )

        # Determine severity level
        level = "Unknown"
        for level_name, (low, high) in SEVERITY_LEVELS.items():
            if low <= infected_percentage < high:
                level = level_name
                break
        if infected_percentage >= SEVERITY_MODERATE_MAX:
            level = "Severe"

        # Detailed pixel statistics
        pixel_stats = {
            "total_pixels": total_pixels,
            "infected_pixels": infected_pixels,
            "mean_activation": round(float(np.mean(heatmap)), 4),
            "max_activation": round(float(np.max(heatmap)), 4),
            "infected_mean_intensity": round(
                float(np.mean(heatmap[infected_mask])) if infected_pixels > 0 else 0.0,
                4,
            ),
        }

        logger.info(
            f"Severity: {infected_percentage}% infected → {level} "
            f"(threshold={self.activation_threshold})"
        )

        return {
            "percentage": infected_percentage,
            "level": level,
            "pixel_stats": pixel_stats,
        }
