"""
Display Formatter — Frontend-Ready Output Converter
======================================================
Transforms technical pipeline output into clean,
human-readable, UI-ready format.

Features
--------
  • Converts raw class names to friendly descriptions
  • Adds user-friendly disease summaries
  • Formats confidence as descriptive text
  • Structures output for direct UI consumption

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger("plant_doctor.formatter")


# ═══════════════════════════════════════════════════════════════
# HUMAN-READABLE DISEASE DESCRIPTIONS
# ═══════════════════════════════════════════════════════════════
# Maps cleaned disease names → plain English descriptions

DISEASE_DESCRIPTIONS: Dict[str, str] = {
    # Apple
    "Apple Scab": "Fungal infection causing dark, scaly lesions on apple leaves and fruit",
    "Black Rot": "Fungal disease causing dark rotting spots on fruit and leaf lesions",
    "Cedar Apple Rust": "Rust disease causing bright orange spots on apple leaves",

    # Cassava
    "Bacterial Blight": "Bacterial infection causing wilting and leaf blight in cassava",
    "Brown Streak": "Viral disease causing brown necrotic streaks on cassava stems and roots",
    "Green Mottle": "Viral disease causing green mottling patterns on cassava leaves",
    "Mosaic": "Viral disease causing distorted, mosaic-patterned leaves in cassava",

    # Cherry / Squash
    "Powdery Mildew": "Fungal disease appearing as white powdery coating on leaf surfaces",

    # Corn
    "Cercospora Leaf Spot Gray Leaf Spot": "Fungal disease causing rectangular gray-brown lesions on corn leaves",
    "Common Rust": "Fungal disease forming reddish-brown pustules on corn leaf surfaces",
    "Northern Leaf Blight": "Fungal disease creating long, cigar-shaped gray-green lesions on corn",

    # Grape
    "Esca (Black Measles)": "Fungal trunk disease causing tiger-striped leaf symptoms in grapevines",
    "Leaf Blight (Isariopsis Leaf Spot)": "Fungal disease causing brown spots and blighting on grape leaves",

    # Orange
    "Haunglongbing (Citrus Greening)": "Devastating bacterial disease causing yellowing and misshapen citrus fruit",

    # Peach / Pepper
    "Bacterial Spot": "Bacterial disease causing small, dark, water-soaked spots on leaves and fruit",

    # Potato / Tomato
    "Early Blight": "Common fungal disease causing dark concentric ring lesions on lower leaves",
    "Late Blight": "Aggressive fungal disease causing rapid wilting and dark, water-soaked patches",

    # Rice
    "Bacterial Leaf Blight": "Bacterial disease causing yellowing and wilting from leaf tips in rice",
    "Brown Spot": "Fungal disease causing oval brown spots on rice leaves, linked to poor nutrition",
    "Leaf Blast": "Destructive fungal disease causing diamond-shaped lesions on rice leaves",
    "Leaf Scald": "Fungal disease causing scalded appearance on rice leaf tips and edges",
    "Narrow Brown Leaf Spot": "Fungal disease causing narrow brown linear spots on rice leaves",
    "Rice Hispa": "Insect pest causing white streaks from larval mining inside rice leaves",
    "Sheath Blight": "Fungal disease causing oval lesions on rice sheaths near the water line",

    # Strawberry
    "Leaf Scorch": "Fungal disease causing purplish spots that dry out and scorch strawberry leaves",

    # Tomato
    "Septoria Leaf Spot": "Fungal disease causing many small circular spots with dark borders on tomato leaves",
    "Leaf Mold": "Fungal disease causing yellow patches on upper leaf surface with olive-green mold beneath",
    "Spider Mites Two-Spotted Spider Mite": "Tiny mite pest causing stippled, yellowed leaves with fine webbing",
    "Target Spot": "Fungal disease causing concentric ringed brown spots on tomato leaves",
    "Tomato Yellow Leaf Curl Virus": "Viral disease causing severe leaf curling, yellowing, and stunted growth",
    "Tomato Mosaic Virus": "Viral disease causing mottled green-yellow patterns and distorted leaves",
}


# ═══════════════════════════════════════════════════════════════
# CONFIDENCE DESCRIPTORS
# ═══════════════════════════════════════════════════════════════

def confidence_descriptor(confidence: float) -> Dict:
    """
    Convert a numeric confidence into a human-readable descriptor.

    Parameters
    ----------
    confidence : float
        Calibrated confidence percentage (0-100).

    Returns
    -------
    dict
        label : str   — 'Very High', 'High', 'Moderate', 'Low'
        color : str   — UI color hint
        description : str — human-readable sentence
    """
    if confidence >= 90:
        return {
            "label": "Very High",
            "color": "green",
            "description": f"The model is highly confident ({confidence:.1f}%) in this diagnosis.",
        }
    elif confidence >= 75:
        return {
            "label": "High",
            "color": "blue",
            "description": f"The model is confident ({confidence:.1f}%) in this diagnosis.",
        }
    elif confidence >= 50:
        return {
            "label": "Moderate",
            "color": "orange",
            "description": f"Moderate confidence ({confidence:.1f}%) — consider verifying with an expert.",
        }
    else:
        return {
            "label": "Low",
            "color": "red",
            "description": f"Low confidence ({confidence:.1f}%) — results may be unreliable.",
        }


class DisplayFormatter:
    """
    Formats the raw pipeline output into clean,
    frontend-ready structured data.
    """

    @staticmethod
    def get_disease_description(disease_name: str) -> str:
        """
        Get a human-readable description for a disease.

        Parameters
        ----------
        disease_name : str
            Cleaned disease name.

        Returns
        -------
        str
            Plain English description of the disease.
        """
        if disease_name.lower() in ("healthy", "unknown", "unknown disease"):
            if disease_name.lower() == "healthy":
                return "The plant appears healthy with no visible signs of disease."
            return "The disease could not be identified with sufficient confidence."

        desc = DISEASE_DESCRIPTIONS.get(disease_name)
        if desc:
            return desc

        # Fallback — generate a basic description
        return f"A plant disease identified as {disease_name}."

    @staticmethod
    def format_output(raw_result: Dict) -> Dict:
        """
        Transform the raw pipeline result into a clean,
        frontend-friendly format.

        Parameters
        ----------
        raw_result : dict
            Output from PlantDoctorPipeline.diagnose().

        Returns
        -------
        dict
            Cleaned, enhanced result ready for UI consumption.
        """
        plant = raw_result.get("plant", "Unknown")
        disease = raw_result.get("disease", "Unknown")
        confidence = raw_result.get("confidence", 0.0)

        # Confidence descriptor
        conf_info = confidence_descriptor(confidence)

        # Disease description
        disease_desc = DisplayFormatter.get_disease_description(disease)

        # Format the result cleanly
        formatted = {
            "plant": plant,
            "disease": disease,
            "disease_description": disease_desc,
            "confidence": confidence,
            "confidence_info": conf_info,
            "status": raw_result.get("status", "Unknown"),
            "severity": raw_result.get("severity", {}),
            "risk": raw_result.get("risk", {}),
            "explanation": raw_result.get("explanation", {}),
            "treatment": raw_result.get("treatment", {}),
            "top_predictions": raw_result.get("top_predictions", []),
            "similar_cases": raw_result.get("similar_cases", []),
            "warnings": raw_result.get("warnings", []),
            "heatmap_path": raw_result.get("heatmap_path", ""),
            "diagnosis_time_ms": raw_result.get("diagnosis_time_ms", 0),
        }

        return formatted
