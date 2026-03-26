"""
Risk Assessor — Severity-to-Risk Conversion
================================================
Converts the numerical severity percentage into a
color-coded risk level with human-readable meaning.

Risk Levels
-----------
  •  0–20 %  → LOW     (Monitor only — minor infection)
  • 20–50 %  → MODERATE (Take action — infection spreading)
  • 50 %+    → HIGH    (Urgent — significant crop damage)

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger("plant_doctor.risk")


# ═══════════════════════════════════════════════════════════════
# RISK LEVEL DEFINITIONS
# ═══════════════════════════════════════════════════════════════

RISK_LEVELS = {
    "Low": {
        "range": (0.0, 20.0),
        "color": "green",
        "icon": "shield-check",
        "meaning": "Minor infection detected. Monitor the plant regularly.",
        "urgency": "No immediate action needed, but keep an eye on the condition.",
        "action_priority": 1,
    },
    "Moderate": {
        "range": (20.0, 50.0),
        "color": "orange",
        "icon": "alert-triangle",
        "meaning": "Significant infection present. Treatment recommended.",
        "urgency": "Take action within 1-3 days to prevent further spread.",
        "action_priority": 2,
    },
    "High": {
        "range": (50.0, 100.0),
        "color": "red",
        "icon": "alert-octagon",
        "meaning": "Severe infection detected. Immediate intervention required.",
        "urgency": "Act immediately — significant yield loss is likely if untreated.",
        "action_priority": 3,
    },
}


class RiskAssessor:
    """
    Converts severity metrics into risk assessments.

    Provides structured risk data suitable for frontend
    display (color, icon, urgency level, meaning).
    """

    @staticmethod
    def assess(
        severity_percentage: float,
        is_healthy: bool = False,
    ) -> Dict:
        """
        Calculate risk level from severity percentage.

        Parameters
        ----------
        severity_percentage : float
            Infected area percentage from severity estimation (0-100).
        is_healthy : bool
            True if the plant is classified as healthy.

        Returns
        -------
        dict
            level           : str   — 'Low', 'Moderate', or 'High'
            color           : str   — UI color hint
            icon            : str   — UI icon name
            meaning         : str   — Human-readable description
            urgency         : str   — What to do and when
            action_priority : int   — 1=low, 2=moderate, 3=high
        """
        if is_healthy:
            return {
                "level": "None",
                "color": "green",
                "icon": "check-circle",
                "meaning": "Plant appears healthy. No disease detected.",
                "urgency": "No action needed. Continue regular care.",
                "action_priority": 0,
            }

        # Determine risk level
        for level_name, info in RISK_LEVELS.items():
            low, high = info["range"]
            if low <= severity_percentage < high:
                return {
                    "level": level_name,
                    "color": info["color"],
                    "icon": info["icon"],
                    "meaning": info["meaning"],
                    "urgency": info["urgency"],
                    "action_priority": info["action_priority"],
                }

        # Fallback for >= 100%
        high_risk = RISK_LEVELS["High"]
        return {
            "level": "High",
            "color": high_risk["color"],
            "icon": high_risk["icon"],
            "meaning": high_risk["meaning"],
            "urgency": high_risk["urgency"],
            "action_priority": high_risk["action_priority"],
        }
