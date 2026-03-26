"""
Image Quality Checker — Pre-processing Module
================================================
Validates input image quality before feeding to the model.

Checks
------
  • Blur detection using Laplacian variance
  • Low brightness detection via mean luminance
  • Image size / resolution validation
  • Returns human-readable warnings

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import os
import logging
from typing import Dict, List, Tuple

import cv2
import numpy as np

logger = logging.getLogger("plant_doctor.image_quality")


# ═══════════════════════════════════════════════════════════════
# CONFIGURABLE THRESHOLDS
# ═══════════════════════════════════════════════════════════════

BLUR_THRESHOLD: float = 100.0        # Laplacian variance < this → blurry
BRIGHTNESS_LOW: float = 40.0         # Mean luminance < this → too dark
BRIGHTNESS_HIGH: float = 240.0       # Mean luminance > this → overexposed
MIN_RESOLUTION: int = 64             # Minimum dimension in pixels
SATURATION_LOW: float = 20.0         # Mean saturation < this → washed out


class ImageQualityChecker:
    """
    Performs pre-inference quality assessment on leaf images.

    Parameters
    ----------
    blur_threshold : float
        Laplacian variance cutoff. Lower = more blur tolerance.
    brightness_low : float
        Mean luminance below this triggers a 'too dark' warning.
    brightness_high : float
        Mean luminance above this triggers an 'overexposed' warning.
    min_resolution : int
        Minimum width/height in pixels.
    """

    def __init__(
        self,
        blur_threshold: float = BLUR_THRESHOLD,
        brightness_low: float = BRIGHTNESS_LOW,
        brightness_high: float = BRIGHTNESS_HIGH,
        min_resolution: int = MIN_RESOLUTION,
    ) -> None:
        self.blur_threshold = blur_threshold
        self.brightness_low = brightness_low
        self.brightness_high = brightness_high
        self.min_resolution = min_resolution

    def check(self, image_path: str) -> Dict:
        """
        Assess image quality.

        Parameters
        ----------
        image_path : str
            Absolute path to the input image.

        Returns
        -------
        dict
            passed   : bool   — True if image passes all checks
            warnings : list   — Human-readable warning messages
            metrics  : dict   — Raw quality metrics
        """
        warnings: List[str] = []
        metrics: Dict = {}

        if not os.path.isfile(image_path):
            return {
                "passed": False,
                "warnings": ["Image file not found"],
                "metrics": {},
            }

        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return {
                "passed": False,
                "warnings": ["Cannot read image — file may be corrupted"],
                "metrics": {},
            }

        h, w = img.shape[:2]
        metrics["width"] = w
        metrics["height"] = h

        # ── Resolution Check ──────────────────────────────────
        if w < self.min_resolution or h < self.min_resolution:
            warnings.append(
                f"Image resolution too low ({w}×{h}). "
                f"Minimum {self.min_resolution}×{self.min_resolution} recommended."
            )

        # ── Blur Detection (Laplacian Variance) ───────────────
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics["blur_score"] = round(float(laplacian_var), 2)

        if laplacian_var < self.blur_threshold:
            warnings.append(
                f"Image appears blurry (sharpness: {laplacian_var:.1f}, "
                f"threshold: {self.blur_threshold}). "
                f"Please retake with a clearer, focused photo."
            )

        # ── Brightness Detection ──────────────────────────────
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mean_brightness = float(hsv[:, :, 2].mean())
        metrics["brightness"] = round(mean_brightness, 2)

        if mean_brightness < self.brightness_low:
            warnings.append(
                f"Image is too dark (brightness: {mean_brightness:.1f}). "
                f"Use better lighting for accurate detection."
            )
        elif mean_brightness > self.brightness_high:
            warnings.append(
                f"Image appears overexposed (brightness: {mean_brightness:.1f}). "
                f"Reduce direct light or flash."
            )

        # ── Saturation Check (washed-out colors) ──────────────
        mean_saturation = float(hsv[:, :, 1].mean())
        metrics["saturation"] = round(mean_saturation, 2)

        if mean_saturation < SATURATION_LOW:
            warnings.append(
                f"Image colors appear washed out (saturation: {mean_saturation:.1f}). "
                f"Ensure the leaf is well-lit with natural colors."
            )

        # ── Overall verdict ───────────────────────────────────
        passed = len(warnings) == 0

        if warnings:
            logger.warning(
                f"Image quality issues detected for {os.path.basename(image_path)}: "
                f"{'; '.join(warnings)}"
            )

        return {
            "passed": passed,
            "warnings": warnings,
            "metrics": metrics,
        }
