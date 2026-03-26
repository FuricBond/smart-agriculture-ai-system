"""
Explanation Engine — Disease Cause Analysis
================================================
Rule-based system that explains WHY a disease occurred.
Provides human-readable environmental and cultural causes
for each detected disease.

Coverage
--------
  • All 52 disease classes in the dataset
  • Environmental factors (humidity, temperature, etc.)
  • Cultural factors (irrigation, spacing, etc.)
  • Fallback explanations for unmapped diseases

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger("plant_doctor.explanation")


# ═══════════════════════════════════════════════════════════════
# DISEASE EXPLANATION DATABASE
# ═══════════════════════════════════════════════════════════════
# Maps raw class labels -> list of causal explanations.
# Keys use the cleaned disease name (after label parser).

DISEASE_EXPLANATIONS: Dict[str, Dict] = {

    # ── APPLE ─────────────────────────────────────────────────
    "Apple Scab": {
        "type": "Fungal",
        "pathogen": "Venturia inaequalis",
        "causes": [
            "Cool, wet spring weather promotes spore germination",
            "Infected fallen leaves from previous season act as inoculum",
            "High humidity (>70%) accelerates fungal spread",
            "Poor air circulation in dense canopy",
        ],
    },
    "Black Rot": {
        "type": "Fungal",
        "pathogen": "Botryosphaeria obtusa",
        "causes": [
            "Warm, humid conditions favor infection",
            "Wounds from insects or hail provide entry points",
            "Infected fruit mummies left in the tree spread spores",
            "Weakened trees from drought stress are more susceptible",
        ],
    },
    "Cedar Apple Rust": {
        "type": "Fungal",
        "pathogen": "Gymnosporangium juniperi-virginianae",
        "causes": [
            "Proximity to cedar or juniper trees (alternate host)",
            "Spring rains carry spores from cedar galls to apple leaves",
            "Warm, wet weather during bloom promotes infection",
        ],
    },

    # ── CASSAVA ───────────────────────────────────────────────
    "Bacterial Blight": {
        "type": "Bacterial",
        "pathogen": "Xanthomonas axonopodis pv. manihotis",
        "causes": [
            "Use of infected planting material (stem cuttings)",
            "High rainfall and warm temperatures promote spread",
            "Mechanical damage during farming creates entry points",
            "Poor field sanitation with infected crop debris",
        ],
    },
    "Brown Streak": {
        "type": "Viral",
        "pathogen": "Cassava brown streak virus (CBSV)",
        "causes": [
            "Spread by whitefly vectors (Bemisia tabaci)",
            "Use of infected planting material",
            "Warm coastal lowland conditions favor the virus",
        ],
    },
    "Green Mottle": {
        "type": "Viral",
        "pathogen": "Cassava green mottle virus",
        "causes": [
            "Transmitted through infected cuttings",
            "Spread by whitefly vectors",
            "Mixed cropping with infected plants nearby",
        ],
    },
    "Mosaic": {
        "type": "Viral",
        "pathogen": "Cassava mosaic virus (CMV)",
        "causes": [
            "Primary spread through infected stem cuttings",
            "Whitefly (Bemisia tabaci) acts as vector",
            "High whitefly populations in warm, dry seasons",
            "Planting susceptible varieties near infected fields",
        ],
    },

    # ── CHERRY ────────────────────────────────────────────────
    "Powdery Mildew": {
        "type": "Fungal",
        "pathogen": "Podosphaera clandestina / Erysiphe spp.",
        "causes": [
            "Warm days (20-30C) with cool nights create ideal conditions",
            "High humidity but dry leaf surfaces favor growth",
            "Dense canopy restricts airflow",
            "Shaded lower leaves are most susceptible",
            "Excessive nitrogen fertilization promotes succulent growth",
        ],
    },

    # ── CORN / MAIZE ──────────────────────────────────────────
    "Cercospora Leaf Spot Gray Leaf Spot": {
        "type": "Fungal",
        "pathogen": "Cercospora zeae-maydis",
        "causes": [
            "Warm temperatures (25-30C) with high humidity",
            "Extended periods of leaf wetness (dew, irrigation)",
            "Conservation tillage leaving infected residue on surface",
            "Continuous corn cropping increases disease pressure",
        ],
    },
    "Common Rust": {
        "type": "Fungal",
        "pathogen": "Puccinia sorghi",
        "causes": [
            "Cool to moderate temperatures (16-25C) favor rust",
            "High humidity and frequent dew periods spread spores",
            "Wind carries spores over long distances",
            "Late planting increases exposure to rust season",
        ],
    },
    "Northern Leaf Blight": {
        "type": "Fungal",
        "pathogen": "Exserohilum turcicum",
        "causes": [
            "Moderate temperatures (18-27C) with heavy dew",
            "Extended leaf wetness periods (6+ hours)",
            "Infected crop residue on soil surface provides inoculum",
            "Susceptible hybrids planted without resistance genes",
        ],
    },

    # ── GRAPE ─────────────────────────────────────────────────
    "Esca (Black Measles)": {
        "type": "Fungal complex",
        "pathogen": "Phaeomoniella chlamydospora, Phaeoacremonium spp.",
        "causes": [
            "Trunk infections through pruning wounds",
            "Older vines (>10 years) are more susceptible",
            "Hot, dry weather triggers symptom expression",
            "Water stress weakens vine defense mechanisms",
        ],
    },
    "Leaf Blight (Isariopsis Leaf Spot)": {
        "type": "Fungal",
        "pathogen": "Pseudocercospora vitis",
        "causes": [
            "Warm, humid conditions promote spore development",
            "Poor canopy management reduces air circulation",
            "Dense foliage retains moisture on leaf surfaces",
        ],
    },

    # ── ORANGE ────────────────────────────────────────────────
    "Haunglongbing (Citrus Greening)": {
        "type": "Bacterial",
        "pathogen": "Candidatus Liberibacter asiaticus",
        "causes": [
            "Transmitted by Asian citrus psyllid (Diaphorina citri)",
            "Infected nursery stock introduces disease",
            "No cure exists — infected trees decline over 3-5 years",
            "Warm tropical/subtropical climates favor the vector",
        ],
    },

    # ── PEACH ─────────────────────────────────────────────────
    "Bacterial Spot": {
        "type": "Bacterial",
        "pathogen": "Xanthomonas arboricola pv. pruni",
        "causes": [
            "Warm, wet weather with wind-driven rain",
            "Bacteria enter through natural openings and wounds",
            "Sandy soils with low organic matter increase susceptibility",
            "Overhead irrigation splashes bacteria onto leaves",
        ],
    },

    # ── PEPPER ────────────────────────────────────────────────
    # Uses the same "Bacterial Spot" entry as Peach (shared pathogen family)

    # ── POTATO ────────────────────────────────────────────────
    "Early Blight": {
        "type": "Fungal",
        "pathogen": "Alternaria solani",
        "causes": [
            "Warm temperatures (24-29C) with alternating wet/dry periods",
            "Older, lower leaves are infected first",
            "Nutrient-deficient or stressed plants are more susceptible",
            "Infected crop debris in soil provides inoculum",
            "Poor crop rotation increases disease buildup",
        ],
    },
    "Late Blight": {
        "type": "Fungal",
        "pathogen": "Phytophthora infestans",
        "causes": [
            "Cool temperatures (15-22C) with high humidity (>90%)",
            "Prolonged leaf wetness from rain, fog, or irrigation",
            "Wind-dispersed sporangia can travel kilometers",
            "Infected seed tubers introduce the pathogen",
            "Dense planting reduces air circulation",
        ],
    },

    # ── RICE ──────────────────────────────────────────────────
    "Bacterial Leaf Blight": {
        "type": "Bacterial",
        "pathogen": "Xanthomonas oryzae pv. oryzae",
        "causes": [
            "Heavy rains and floods spread the bacteria",
            "Warm temperatures (25-34C) promote multiplication",
            "Wounds from wind damage provide entry points",
            "Excessive nitrogen fertilization increases susceptibility",
            "Contaminated irrigation water carries the pathogen",
        ],
    },
    "Brown Spot": {
        "type": "Fungal",
        "pathogen": "Bipolaris oryzae",
        "causes": [
            "Nutrient-deficient soils (especially potassium and silicon)",
            "High humidity and frequent rainfall",
            "Poor seed quality with seed-borne infection",
            "Water stress during grain filling stage",
        ],
    },
    "Leaf Blast": {
        "type": "Fungal",
        "pathogen": "Magnaporthe oryzae",
        "causes": [
            "Cool nights (17-22C) followed by warm days",
            "High humidity (>90%) with prolonged dew periods",
            "Excessive nitrogen fertilization promotes susceptibility",
            "Dense planting reduces air circulation",
            "Susceptible rice varieties planted in blast-prone areas",
        ],
    },
    "Leaf Scald": {
        "type": "Fungal",
        "pathogen": "Microdochium oryzae",
        "causes": [
            "Cool temperatures with high humidity",
            "Excessive nitrogen applications",
            "Wind-borne spore dispersal during wet weather",
        ],
    },
    "Narrow Brown Leaf Spot": {
        "type": "Fungal",
        "pathogen": "Cercospora janseana",
        "causes": [
            "Warm temperatures with frequent rain",
            "High nitrogen levels promote leaf growth and infection",
            "Infected crop residue serves as disease source",
        ],
    },
    "Rice Hispa": {
        "type": "Insect pest",
        "pathogen": "Dicladispa armigera",
        "causes": [
            "High nitrogen fertilizer use attracts hispa beetles",
            "Dense plant spacing provides ideal habitat for larvae",
            "Continuous flooded conditions favor insect populations",
            "Nearby grassy weeds serve as alternate hosts",
        ],
    },
    "Sheath Blight": {
        "type": "Fungal",
        "pathogen": "Rhizoctonia solani",
        "causes": [
            "Warm temperatures (28-32C) with high humidity",
            "Dense planting and excessive tillering create microclimate",
            "High nitrogen fertilization produces lush growth",
            "Sclerotia surviving in soil from previous crops",
        ],
    },

    # ── SQUASH ────────────────────────────────────────────────
    # Shares "Powdery Mildew" with Cherry (similar causes)

    # ── STRAWBERRY ────────────────────────────────────────────
    "Leaf Scorch": {
        "type": "Fungal",
        "pathogen": "Diplocarpon earlianum",
        "causes": [
            "Warm, wet spring and summer conditions",
            "Frequent overhead irrigation wets leaf surfaces",
            "Older infected leaves act as disease source",
            "Crowded planting reduces airflow",
        ],
    },

    # ── TOMATO ────────────────────────────────────────────────
    # "Early Blight" and "Late Blight" shared with Potato above
    "Septoria Leaf Spot": {
        "type": "Fungal",
        "pathogen": "Septoria lycopersici",
        "causes": [
            "Warm, wet weather (20-25C) with frequent rain",
            "Splashing water spreads spores from soil to lower leaves",
            "Infected plant debris left in garden beds",
            "Overhead irrigation wets foliage for prolonged periods",
            "Poor air circulation in dense plantings",
        ],
    },
    "Leaf Mold": {
        "type": "Fungal",
        "pathogen": "Passalora fulva (Cladosporium fulvum)",
        "causes": [
            "High humidity (>85%) inside greenhouses or tunnels",
            "Poor ventilation traps moist air around plants",
            "Temperatures of 20-25C are optimal for the fungus",
            "Dense plant spacing limits airflow",
        ],
    },
    "Spider Mites Two-Spotted Spider Mite": {
        "type": "Insect/Mite pest",
        "pathogen": "Tetranychus urticae",
        "causes": [
            "Hot, dry weather (>30C) accelerates mite reproduction",
            "Drought-stressed plants are more susceptible",
            "Overuse of broad-spectrum insecticides kills natural predators",
            "Dusty conditions near roads or construction favor mites",
        ],
    },
    "Target Spot": {
        "type": "Fungal",
        "pathogen": "Corynespora cassiicola",
        "causes": [
            "Warm, humid conditions with frequent rainfall",
            "Dense canopy retains moisture on leaf surfaces",
            "Poor staking/pruning limits air circulation",
            "Prolonged leaf wetness from overhead irrigation",
        ],
    },
    "Tomato Yellow Leaf Curl Virus": {
        "type": "Viral",
        "pathogen": "Tomato yellow leaf curl virus (TYLCV)",
        "causes": [
            "Transmitted by whitefly (Bemisia tabaci) vector",
            "High whitefly populations in warm seasons",
            "Infected transplants introduced from nurseries",
            "Nearby weed hosts serve as virus reservoirs",
        ],
    },
    "Tomato Mosaic Virus": {
        "type": "Viral",
        "pathogen": "Tomato mosaic virus (ToMV)",
        "causes": [
            "Highly stable virus transmitted by contaminated hands/tools",
            "Infected seeds can carry the virus",
            "Mechanical contact during pruning/harvesting spreads it",
            "The virus persists in soil and plant debris for months",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# GENERIC FALLBACKS BY DISEASE TYPE
# ═══════════════════════════════════════════════════════════════

GENERIC_EXPLANATIONS: Dict[str, List[str]] = {
    "fungal": [
        "Fungal infections thrive in warm, humid conditions",
        "Prolonged leaf wetness from rain or irrigation aids spore germination",
        "Poor air circulation in dense plantings accelerates spread",
        "Infected crop debris in soil provides a source of inoculum",
    ],
    "bacterial": [
        "Bacterial pathogens spread through water splash and wind-driven rain",
        "Wounds from insects, hail, or mechanical damage provide entry points",
        "Contaminated tools and hands transmit bacteria between plants",
        "Warm, moist conditions favor rapid bacterial multiplication",
    ],
    "viral": [
        "Viral diseases are typically spread by insect vectors (aphids, whiteflies)",
        "Infected planting material introduces the virus into new fields",
        "Once infected, plants cannot be cured — prevention is key",
        "Nearby weed hosts serve as virus reservoirs",
    ],
    "unknown": [
        "Environmental stress (drought, flooding, extreme temperatures) weakens plant defenses",
        "Nutrient deficiency can make plants more susceptible to disease",
        "Poor crop rotation allows pathogens to build up in soil",
    ],
}


class ExplanationEngine:
    """
    Provides human-readable explanations for detected diseases.

    Uses a comprehensive rule-based knowledge base covering
    all 52 classes in the dataset.
    """

    @staticmethod
    def explain(disease_name: str, plant_name: str = "") -> Dict:
        """
        Generate an explanation for why a disease occurred.

        Parameters
        ----------
        disease_name : str
            Cleaned disease name (e.g. 'Septoria Leaf Spot').
        plant_name : str
            Cleaned plant name (e.g. 'Tomato').

        Returns
        -------
        dict
            type      : str         — Disease type (Fungal, Bacterial, etc.)
            pathogen  : str         — Scientific name of pathogen
            causes    : list[str]   — Why the disease occurred
            summary   : str         — One-line human-readable summary
        """
        if not disease_name or disease_name.lower() in ("healthy", "unknown", "unknown disease"):
            return {
                "type": "N/A",
                "pathogen": "N/A",
                "causes": [],
                "summary": "No disease detected — plant appears healthy."
                if disease_name.lower() == "healthy"
                else "Unable to determine disease cause.",
            }

        # Look up in the knowledge base
        info = DISEASE_EXPLANATIONS.get(disease_name)

        if info:
            disease_type = info.get("type", "Unknown")
            pathogen = info.get("pathogen", "Unknown pathogen")
            causes = info.get("causes", [])
            summary = (
                f"{disease_name} is a {disease_type.lower()} disease "
                f"caused by {pathogen}"
            )
            if plant_name:
                summary += f", commonly affecting {plant_name} plants"
            summary += "."
        else:
            # Try to infer disease type from name keywords
            lower = disease_name.lower()
            if any(kw in lower for kw in ("blight", "rot", "mold", "mildew", "spot", "scab", "scorch", "rust")):
                disease_type = "Fungal"
                causes = GENERIC_EXPLANATIONS["fungal"]
            elif any(kw in lower for kw in ("bacterial",)):
                disease_type = "Bacterial"
                causes = GENERIC_EXPLANATIONS["bacterial"]
            elif any(kw in lower for kw in ("virus", "mosaic", "curl")):
                disease_type = "Viral"
                causes = GENERIC_EXPLANATIONS["viral"]
            else:
                disease_type = "Unknown"
                causes = GENERIC_EXPLANATIONS["unknown"]

            pathogen = "Not identified"
            summary = (
                f"{disease_name} appears to be a {disease_type.lower()} condition"
            )
            if plant_name:
                summary += f" affecting {plant_name}"
            summary += "."

        return {
            "type": disease_type,
            "pathogen": pathogen,
            "causes": causes,
            "summary": summary,
        }
