"""
Label Parser — Global Plant + Disease Detection
====================================================
Splits compound disease labels (e.g. "Tomato___Early_Blight")
into structured plant and disease components.

Handles edge cases like:
  - Labels with parentheses: "Cherry_(including_sour)___Powdery_mildew"
  - Labels without separator: "Unknown_disease"
  - Labels with commas: "Pepper,_bell___Bacterial_spot"
  - Healthy plants: "Tomato___healthy"

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import re
import logging
from typing import Dict

logger = logging.getLogger("plant_doctor.label_parser")


class LabelParser:
    """
    Parses raw disease class labels into structured components.

    The standard label format is: ``Plant___Disease``
    where '___' (triple underscore) is the separator.
    """

    # Common format: Plant___Condition
    SEPARATOR = "___"

    @staticmethod
    def parse(label: str) -> Dict[str, str]:
        """
        Parse a disease label into plant and disease names.

        Parameters
        ----------
        label : str
            Raw class label (e.g. 'Tomato___Early_blight').

        Returns
        -------
        dict
            raw_label  : str — Original unmodified label
            plant      : str — Extracted plant name
            disease    : str — Extracted disease/condition name
            is_healthy : bool — True if the plant is healthy
        """
        if not label or not label.strip():
            return {
                "raw_label": label,
                "plant": "Unknown",
                "disease": "Unknown",
                "is_healthy": False,
            }

        raw = label.strip()

        if LabelParser.SEPARATOR in raw:
            parts = raw.split(LabelParser.SEPARATOR, 1)
            plant_raw = parts[0]
            disease_raw = parts[1] if len(parts) > 1 else "Unknown"
        else:
            # No separator — treat entire label as disease
            plant_raw = "Unknown"
            disease_raw = raw

        # Clean up underscores and formatting
        plant = LabelParser._clean_name(plant_raw)
        disease = LabelParser._clean_name(disease_raw)

        # Check if healthy
        is_healthy = disease.lower() in ("healthy", "healthy rice leaf")

        if is_healthy:
            disease = "Healthy"

        return {
            "raw_label": raw,
            "plant": plant,
            "disease": disease,
            "is_healthy": is_healthy,
        }

    @staticmethod
    def _clean_name(name: str) -> str:
        """
        Clean a raw label component:
          - Replace underscores with spaces
          - Clean up extra whitespace
          - Title-case for readability
        """
        # Replace underscores with spaces
        cleaned = name.replace("_", " ").strip()

        # Collapse multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Title case, preserving parenthetical expressions
        if cleaned:
            cleaned = cleaned.title()

        return cleaned

    @staticmethod
    def parse_all(labels: list) -> list:
        """Parse a list of labels at once."""
        return [LabelParser.parse(label) for label in labels]
