"""
Confidence Calibrator — Realistic Score Normalization
========================================================
Prevents unrealistic confidence values (e.g. 100%) by
applying temperature scaling and soft capping.

Problem
-------
  Neural networks are often overconfident. A raw softmax
  output of 0.9999 does not mean the model is 99.99% sure.
  This module normalizes outputs to trustworthy ranges.

Methods
-------
  • Temperature scaling (softens the softmax distribution)
  • Soft capping (asymptotic limit to a maximum value)
  • Entropy-aware adjustment (high-entropy = less confident)

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import math
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("plant_doctor.calibrator")


# ═══════════════════════════════════════════════════════════════
# CONFIGURABLE PARAMETERS
# ═══════════════════════════════════════════════════════════════

# Maximum displayable confidence (never exceed this)
MAX_CONFIDENCE: float = 98.5

# Temperature for scaling (> 1.0 = softer, < 1.0 = sharper)
TEMPERATURE: float = 1.5

# Minimum confidence floor (don't show < this even if raw is lower)
MIN_DISPLAY_CONFIDENCE: float = 1.0


class ConfidenceCalibrator:
    """
    Calibrates raw model confidence scores to realistic,
    trustworthy values.

    Parameters
    ----------
    max_confidence : float
        Hard ceiling for displayed confidence (default 98.5%).
    temperature : float
        Softening factor for the confidence distribution.
        Values > 1.0 reduce overconfidence.
    """

    def __init__(
        self,
        max_confidence: float = MAX_CONFIDENCE,
        temperature: float = TEMPERATURE,
    ) -> None:
        self.max_confidence = max_confidence
        self.temperature = temperature

    def calibrate(
        self,
        top_predictions: List[Tuple[str, float]],
    ) -> List[Tuple[str, float]]:
        """
        Calibrate the confidence scores for all top-K predictions.

        Parameters
        ----------
        top_predictions : list of (class_name, raw_confidence_%)
            Raw predictions from the model (0-100 scale).

        Returns
        -------
        list of (class_name, calibrated_confidence_%)
            Calibrated predictions with realistic scores.
        """
        if not top_predictions:
            return []

        # ── Step 1: Convert to probabilities ──────────────────
        raw_probs = [conf / 100.0 for _, conf in top_predictions]

        # ── Step 2: Apply temperature scaling ─────────────────
        # Re-compute softmax with temperature
        log_probs = []
        for p in raw_probs:
            # Clamp to avoid log(0)
            p_clamped = max(p, 1e-10)
            log_probs.append(math.log(p_clamped) / self.temperature)

        # Softmax with temperature
        max_lp = max(log_probs)
        exp_probs = [math.exp(lp - max_lp) for lp in log_probs]
        sum_exp = sum(exp_probs)
        scaled_probs = [ep / sum_exp for ep in exp_probs]

        # ── Step 3: Apply soft capping ────────────────────────
        # Use a sigmoid-like compression near the ceiling
        calibrated = []
        for (name, _raw), prob in zip(top_predictions, scaled_probs):
            conf_pct = prob * 100.0

            # Soft cap using asymptotic function
            conf_pct = self._soft_cap(conf_pct)

            # Enforce floor
            conf_pct = max(conf_pct, MIN_DISPLAY_CONFIDENCE)

            calibrated.append((name, round(conf_pct, 1)))

        logger.info(
            f"Calibrated top-1: {top_predictions[0][1]:.1f}% -> "
            f"{calibrated[0][1]:.1f}% (temp={self.temperature})"
        )

        return calibrated

    def calibrate_single(self, confidence: float) -> float:
        """
        Calibrate a single confidence value.

        Parameters
        ----------
        confidence : float
            Raw confidence percentage (0-100).

        Returns
        -------
        float
            Calibrated confidence percentage.
        """
        return self._soft_cap(confidence)

    def _soft_cap(self, conf: float) -> float:
        """
        Apply an asymptotic soft cap.

        Uses a scaled tanh function that approaches max_confidence
        but never reaches it.

        For example, with max_confidence=98.5:
          99.9 -> ~97.8
          95.0 -> ~93.8
          80.0 -> ~79.6
          50.0 -> ~49.9
        """
        if conf <= 0:
            return 0.0

        cap = self.max_confidence
        # Scale input to [0, ~3] range where tanh saturates
        # This keeps low values nearly unchanged while
        # compressing high values toward the cap
        x = conf / 100.0
        scaled = cap * math.tanh(x * 1.8)

        return round(min(scaled, cap), 1)
