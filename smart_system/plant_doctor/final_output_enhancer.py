"""
Final Output Enhancer — User-Centric Polish Layer
=====================================================
Post-processes the raw pipeline result into a fully
user-friendly, frontend-ready, non-technical output.

Features
--------
  1.  Final Advice   — single actionable decision message
  2.  Summary        — one-line plain English overview
  3.  Confidence Label — human-readable confidence tier
  4.  UI Metadata    — colors, icons for frontend rendering
  5.  Visual Output  — alias for the heatmap overlay path
  6.  Similarity %   — distance → readable percentage score
  7.  Warning Polish — clean non-technical warning messages
  8.  Unknown Message — guidance when disease is not recognized
  9.  Language Simplification — replaces technical jargon
  10. Structure Normalization — ensures every expected key exists

Design Principle
----------------
  This module does NOT modify any upstream data.
  It only adds NEW keys and reformats existing values
  in the final result dictionary.

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import re
import math
import logging
from typing import Dict, List

logger = logging.getLogger("plant_doctor.enhancer")


# ═══════════════════════════════════════════════════════════════
# 1. FINAL ADVICE — severity-based decision message
# ═══════════════════════════════════════════════════════════════

ADVICE_MESSAGES = {
    "None (Healthy)": (
        "Your plant looks healthy! No treatment is needed. "
        "Continue regular watering and monitoring."
    ),
    "Low": (
        "A minor infection has been detected. No immediate action is needed, "
        "but monitor the plant over the next few days for any changes."
    ),
    "Moderate": (
        "A moderate infection has been detected. Begin treatment within "
        "2-3 days to prevent it from spreading to other parts of the plant."
    ),
    "Severe": (
        "A severe infection has been detected. Immediate treatment is "
        "required to prevent significant crop damage and potential loss."
    ),
    "Unknown": (
        "The severity could not be determined. Please inspect the plant "
        "closely and consult a local agricultural expert if symptoms persist."
    ),
}


def _generate_advice(severity_level: str, risk_level: str) -> str:
    """Generate a single actionable decision message."""
    # Prefer severity-based advice, fall back to risk
    advice = ADVICE_MESSAGES.get(severity_level)
    if advice:
        return advice

    # Risk-based fallback
    risk_map = {
        "None": ADVICE_MESSAGES["None (Healthy)"],
        "Low": ADVICE_MESSAGES["Low"],
        "Moderate": ADVICE_MESSAGES["Moderate"],
        "High": ADVICE_MESSAGES["Severe"],
    }
    return risk_map.get(risk_level, ADVICE_MESSAGES["Unknown"])


# ═══════════════════════════════════════════════════════════════
# 2. SUMMARY GENERATOR — one-line plain English
# ═══════════════════════════════════════════════════════════════

def _generate_summary(
    plant: str,
    disease: str,
    severity_level: str,
    disease_type: str,
    is_healthy: bool,
) -> str:
    """Generate a non-technical one-line summary."""
    if is_healthy or disease.lower() == "healthy":
        return (
            f"Good news! This {plant.lower()} plant appears healthy "
            f"with no visible signs of disease."
        )

    if disease.lower() in ("unknown", "unknown disease"):
        return (
            f"The system was unable to identify the disease on this "
            f"{plant.lower()} plant. Expert consultation is recommended."
        )

    # Simplify disease type for non-technical users
    type_simple = {
        "Fungal": "fungal",
        "Bacterial": "bacterial",
        "Viral": "viral",
        "Insect pest": "insect-related",
        "Insect/Mite pest": "pest-related",
        "Fungal complex": "fungal",
    }.get(disease_type, "")

    severity_word = {
        "Low": "a mild",
        "Moderate": "a moderate",
        "Severe": "a severe",
        "Unknown": "an",
    }.get(severity_level, "an")

    type_phrase = f" {type_simple}" if type_simple else ""

    # Build the summary
    summary = (
        f"This {plant.lower()} plant is affected by "
        f"{severity_word}{type_phrase} disease ({disease}). "
    )

    if severity_level in ("Low", "Moderate"):
        summary += "Early treatment can prevent further damage."
    elif severity_level == "Severe":
        summary += "Immediate action is strongly recommended."
    else:
        summary += "See treatment recommendations below."

    return summary


# ═══════════════════════════════════════════════════════════════
# 3. CONFIDENCE LABEL
# ═══════════════════════════════════════════════════════════════

def _confidence_label(confidence: float) -> str:
    """Convert confidence percentage to a readable label."""
    if confidence >= 90:
        return "Very High Confidence"
    elif confidence >= 75:
        return "High Confidence"
    elif confidence >= 50:
        return "Moderate Confidence"
    else:
        return "Low Confidence"


# ═══════════════════════════════════════════════════════════════
# 4. UI METADATA — colors and icons for frontend
# ═══════════════════════════════════════════════════════════════

def _generate_ui_metadata(
    severity_level: str,
    risk_level: str,
    confidence: float,
) -> Dict:
    """Generate frontend-ready color and icon mappings."""
    # Severity color
    severity_colors = {
        "None (Healthy)": "green",
        "Low": "green",
        "Moderate": "orange",
        "Severe": "red",
    }

    # Confidence color
    if confidence >= 75:
        conf_color = "green"
    elif confidence >= 50:
        conf_color = "yellow"
    else:
        conf_color = "red"

    # Risk color (already in risk object, but duplicated for UI block)
    risk_colors = {
        "None": "green",
        "Low": "green",
        "Moderate": "orange",
        "High": "red",
    }

    # Severity icons
    severity_icons = {
        "None (Healthy)": "check-circle",
        "Low": "info-circle",
        "Moderate": "alert-triangle",
        "Severe": "alert-octagon",
    }

    # Risk icons
    risk_icons = {
        "None": "shield-check",
        "Low": "shield-check",
        "Moderate": "alert-triangle",
        "High": "alert-octagon",
    }

    return {
        "severity_color": severity_colors.get(severity_level, "gray"),
        "risk_color": risk_colors.get(risk_level, "gray"),
        "confidence_color": conf_color,
        "icons": {
            "severity": severity_icons.get(severity_level, "help-circle"),
            "risk": risk_icons.get(risk_level, "help-circle"),
            "confidence": "check-circle" if confidence >= 75 else (
                "alert-circle" if confidence >= 50 else "x-circle"
            ),
        },
        "badges": {
            "severity": severity_level,
            "risk": risk_level,
            "confidence": _confidence_label(confidence),
        },
    }


# ═══════════════════════════════════════════════════════════════
# 6. SIMILARITY SCORE → PERCENTAGE
# ═══════════════════════════════════════════════════════════════

def _format_similarity_cases(cases: List[Dict]) -> List[Dict]:
    """
    Convert raw L2 distance scores to human-readable percentages.

    L2 distance 0.0 = identical,  2.0 = completely different
    (for L2-normalized vectors, max distance = 2.0)
    """
    formatted = []
    for case in cases:
        raw_score = case.get("score", 0.0)
        # Convert L2 distance to similarity percentage
        # similarity = max(0, (1 - distance/2)) * 100
        sim_pct = max(0.0, (1.0 - raw_score / 2.0)) * 100.0
        sim_pct = round(sim_pct, 1)

        formatted.append({
            "image": case.get("image", ""),
            "disease": case.get("label", case.get("raw_label", "Unknown")),
            "raw_label": case.get("raw_label", ""),
            "similarity_score": f"{sim_pct}%",
            "similarity_value": sim_pct,
        })
    return formatted


# ═══════════════════════════════════════════════════════════════
# 7. WARNING POLISH — clean non-technical messages
# ═══════════════════════════════════════════════════════════════

WARNING_REPLACEMENTS = {
    "laplacian variance": "sharpness analysis",
    "below threshold": "below acceptable quality",
    "image appears blurry": "The image appears blurry. Try taking a clearer photo for more accurate results.",
    "image is too dark": "The image is too dark. Try using better lighting for more accurate results.",
    "image appears overexposed": "The image appears too bright. Try reducing light exposure.",
    "resolution too low": "The image resolution is very low. Use a higher quality camera if possible.",
    "colors appear washed out": "The image colors appear faded. Try adjusting camera settings.",
    "grad-cam heatmap generation failed -- skipping.": "Disease area visualization could not be generated.",
    "prediction is ambiguous": "Multiple diseases show similar patterns. Manual verification recommended.",
}


def _polish_warnings(warnings: List[str]) -> List[str]:
    """Replace technical warning messages with user-friendly versions."""
    polished = []
    for w in warnings:
        cleaned = w
        lower = w.lower().strip()

        # Check for direct matches first
        for tech_phrase, friendly in WARNING_REPLACEMENTS.items():
            if tech_phrase in lower:
                cleaned = friendly
                break

        # Remove technical prefixes
        cleaned = re.sub(r"^model prediction failed:\s*", "Analysis error: ", cleaned, flags=re.IGNORECASE)

        polished.append(cleaned)
    return polished


# ═══════════════════════════════════════════════════════════════
# 8. UNKNOWN CASE MESSAGE
# ═══════════════════════════════════════════════════════════════

UNKNOWN_MESSAGE = (
    "This disease is not recognized by the system. The image may show "
    "an uncommon condition or the photo quality may be insufficient. "
    "Please consult a local agricultural expert for accurate diagnosis."
)


# ═══════════════════════════════════════════════════════════════
# 9. LANGUAGE SIMPLIFICATION — jargon → plain English
# ═══════════════════════════════════════════════════════════════

JARGON_MAP = {
    "inoculum": "source of infection",
    "sporangia": "tiny spore containers",
    "spore germination": "growth of disease spores",
    "sclerotia": "hard survival structures of the fungus",
    "pathogen": "disease-causing organism",
    "susceptible": "vulnerable",
    "alternate host": "another plant that carries the disease",
    "vector": "insect that carries and spreads the disease",
    "systemic insecticide": "insecticide absorbed by the plant",
    "IPM": "integrated pest management",
    "biocontrol": "natural biological control",
    "Bordeaux mixture": "a copper-based protective spray (Bordeaux mixture)",
    "biofungicide": "a natural, biological fungicide",
    "roguing": "removing and destroying infected plants",
    "rogue out": "pull out and destroy",
    "bactericide": "a chemical that kills bacteria",
    "miticide": "a chemical that kills mites",
    "canopy": "the leafy upper area of the plant",
    "foliar": "on the leaves",
    "crop rotation": "planting different crops in alternating seasons",
    "tillering": "production of side shoots in grain crops",
    "conservation tillage": "low-disturbance farming that leaves crop residue on the surface",
    "fungal trunk disease": "a fungal disease that infects the main stem",
    "psyllid": "a tiny jumping insect",
    "parasitoid": "a beneficial insect that naturally controls pests",
}


def _simplify_text(text: str) -> str:
    """Replace technical jargon with plain English equivalents."""
    result = text
    for jargon, simple in JARGON_MAP.items():
        # Case-insensitive replace, preserving surrounding text
        pattern = re.compile(re.escape(jargon), re.IGNORECASE)
        result = pattern.sub(simple, result)
    return result


def _simplify_list(items: List[str]) -> List[str]:
    """Simplify a list of strings."""
    return [_simplify_text(item) for item in items]


# ═══════════════════════════════════════════════════════════════
# MAIN ENHANCER
# ═══════════════════════════════════════════════════════════════

class FinalOutputEnhancer:
    """
    Post-processes the raw pipeline result into a fully
    user-centric, frontend-ready output.

    This is the LAST stage in the pipeline. It only ADDS
    new fields — it never removes or modifies upstream data
    destructively.
    """

    @staticmethod
    def enhance(result: Dict) -> Dict:
        """
        Apply all 10 enhancements to the pipeline result.

        Parameters
        ----------
        result : dict
            Raw output from the pipeline's diagnostic stages.

        Returns
        -------
        dict
            Enhanced, frontend-ready result with all user-facing
            fields populated.
        """
        plant = result.get("plant", "Unknown")
        disease = result.get("disease", "Unknown")
        confidence = result.get("confidence", 0.0)
        status = result.get("status", "Unknown")
        severity = result.get("severity", {})
        severity_level = severity.get("level", "Unknown")
        risk = result.get("risk", {})
        risk_level = risk.get("level", "Unknown")
        explanation = result.get("explanation", {})
        treatment = result.get("treatment", {})
        is_healthy = disease.lower() == "healthy"

        # ── 1. Final Advice ───────────────────────────────────
        result["final_advice"] = _generate_advice(severity_level, risk_level)

        # ── 2. Summary ────────────────────────────────────────
        result["summary"] = _generate_summary(
            plant=plant,
            disease=disease,
            severity_level=severity_level,
            disease_type=explanation.get("type", ""),
            is_healthy=is_healthy,
        )

        # ── 3. Confidence Label ───────────────────────────────
        result["confidence_label"] = _confidence_label(confidence)

        # ── 4. UI Metadata ────────────────────────────────────
        result["ui"] = _generate_ui_metadata(
            severity_level=severity_level,
            risk_level=risk_level,
            confidence=confidence,
        )

        # ── 5. Visual Output ──────────────────────────────────
        result["visual_output"] = result.get("heatmap_path", "")

        # ── 6. Similarity Score Display ───────────────────────
        raw_similar = result.get("similar_cases", [])
        result["similar_cases"] = _format_similarity_cases(raw_similar)

        # ── 7. Warning Polish ─────────────────────────────────
        raw_warnings = result.get("warnings", [])
        result["warnings"] = _polish_warnings(raw_warnings)

        # ── 8. Unknown Case Message ───────────────────────────
        if status == "Unknown":
            result["message"] = UNKNOWN_MESSAGE
        else:
            result["message"] = ""

        # ── 9. Language Simplification ────────────────────────
        # Simplify explanation causes
        if "causes" in explanation:
            result["explanation"]["causes"] = _simplify_list(
                explanation["causes"]
            )
        if "summary" in explanation:
            result["explanation"]["summary"] = _simplify_text(
                explanation["summary"]
            )

        # Simplify treatment steps
        for key in ("immediate", "prevention", "organic"):
            if key in treatment:
                result["treatment"][key] = _simplify_list(treatment[key])
        if "summary" in treatment:
            result["treatment"]["summary"] = _simplify_text(treatment["summary"])

        # ── 10. Structure Normalization ───────────────────────
        # Ensure every expected key exists (with safe defaults)
        defaults = {
            "plant": "Unknown",
            "disease": "Unknown",
            "disease_description": "",
            "confidence": 0.0,
            "confidence_label": "Low Confidence",
            "confidence_info": {},
            "status": "Unknown",
            "severity": {"percentage": 0.0, "level": "Unknown", "risk": "Unknown"},
            "risk": {},
            "summary": "",
            "final_advice": "",
            "explanation": {},
            "treatment": {},
            "top_predictions": [],
            "similar_cases": [],
            "warnings": [],
            "message": "",
            "final_source": "CNN Model",
            "clip_predictions": [],
            "visual_output": "",
            "heatmap_path": "",
            "ui": {},
            "diagnosis_time_ms": 0,
        }
        for key, default in defaults.items():
            if key not in result:
                result[key] = default

        logger.info("Output enhancement complete")
        return result
