"""
Treatment Recommendation Engine — Actionable Disease Management
==================================================================
Provides specific, practical treatment recommendations for each
detected plant disease.

Coverage
--------
  • Chemical treatments (fungicides, bactericides)
  • Cultural practices (pruning, irrigation management)
  • Biological controls where applicable
  • Preventive measures for future seasons
  • Safety notes and organic alternatives

Author  : Smart Agriculture AI Team
Version : 1.0.0
"""

from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger("plant_doctor.treatment")


# ═══════════════════════════════════════════════════════════════
# TREATMENT DATABASE
# ═══════════════════════════════════════════════════════════════

TREATMENT_DATABASE: Dict[str, Dict] = {

    # ── APPLE ─────────────────────────────────────────────────
    "Apple Scab": {
        "immediate": [
            "Remove and destroy infected fallen leaves",
            "Prune affected branches to improve air circulation",
            "Apply fungicide spray (Captan or Myclobutanil)",
        ],
        "prevention": [
            "Plant scab-resistant apple varieties",
            "Apply protective fungicide sprays in early spring",
            "Maintain good sanitation — rake and remove fallen leaves",
        ],
        "organic": [
            "Apply sulfur-based fungicide during early season",
            "Use neem oil as a preventive spray",
        ],
    },
    "Black Rot": {
        "immediate": [
            "Remove and destroy all infected fruit (mummies)",
            "Prune out dead or cankered wood",
            "Apply Captan or Mancozeb fungicide",
        ],
        "prevention": [
            "Remove all fruit mummies from the tree and ground",
            "Maintain proper pruning for airflow",
            "Avoid wounding fruit during harvest",
        ],
        "organic": [
            "Apply copper-based fungicide in early spring",
            "Practice strict sanitation of orchard floor",
        ],
    },
    "Cedar Apple Rust": {
        "immediate": [
            "Apply Myclobutanil fungicide at pink bud stage",
            "Remove nearby cedar/juniper galls if possible",
        ],
        "prevention": [
            "Plant rust-resistant apple varieties",
            "Remove cedar trees within a 2-mile radius if feasible",
            "Apply preventive fungicide from pink bud through petal fall",
        ],
        "organic": [
            "Use sulfur sprays as preventive measure",
        ],
    },

    # ── CASSAVA ───────────────────────────────────────────────
    "Bacterial Blight": {
        "immediate": [
            "Remove and burn infected plant parts immediately",
            "Avoid working in fields when plants are wet",
            "Apply copper-based bactericide (Bordeaux mixture)",
        ],
        "prevention": [
            "Use certified disease-free planting material",
            "Practice crop rotation (2-3 year cycle)",
            "Plant resistant cassava varieties (e.g., TME 419)",
        ],
        "organic": [
            "Use clean, healthy stem cuttings for planting",
            "Apply compost to improve soil health and plant resistance",
        ],
    },
    "Brown Streak": {
        "immediate": [
            "Uproot and destroy severely infected plants",
            "Do NOT use cuttings from infected plants",
        ],
        "prevention": [
            "Plant tolerant varieties (e.g., Kiroba, Namikonga)",
            "Source clean planting material from certified nurseries",
            "Control whitefly populations with yellow sticky traps",
        ],
        "organic": [
            "Use neem-based sprays to repel whiteflies",
            "Intercrop with whitefly-repelling plants",
        ],
    },
    "Green Mottle": {
        "immediate": [
            "Remove and destroy infected plants to prevent spread",
        ],
        "prevention": [
            "Use virus-free planting material",
            "Control whitefly vectors with integrated pest management",
            "Avoid planting cassava near infected fields",
        ],
        "organic": [
            "Use yellow sticky traps for whitefly monitoring",
        ],
    },
    "Mosaic": {
        "immediate": [
            "Rogue out severely infected plants immediately",
            "Do NOT use cuttings from symptomatic plants",
        ],
        "prevention": [
            "Plant mosaic-resistant varieties (e.g., NASE 14, TME 204)",
            "Control whitefly populations aggressively",
            "Source certified clean planting material",
        ],
        "organic": [
            "Use reflective mulch to deter whiteflies",
            "Apply neem extract spray for whitefly control",
        ],
    },

    # ── CHERRY / SQUASH POWDERY MILDEW ────────────────────────
    "Powdery Mildew": {
        "immediate": [
            "Remove heavily infected leaves and shoots",
            "Apply sulfur-based or potassium bicarbonate fungicide",
            "Improve air circulation by pruning dense canopy",
        ],
        "prevention": [
            "Plant mildew-resistant varieties",
            "Avoid excessive nitrogen fertilization",
            "Space plants adequately for air circulation",
            "Water at base of plants — avoid wetting foliage",
        ],
        "organic": [
            "Spray milk solution (1:9 milk:water ratio)",
            "Apply neem oil or baking soda spray weekly",
            "Use potassium bicarbonate (Kaligreen)",
        ],
    },

    # ── CORN / MAIZE ──────────────────────────────────────────
    "Cercospora Leaf Spot Gray Leaf Spot": {
        "immediate": [
            "Apply foliar fungicide (Azoxystrobin or Pyraclostrobin)",
            "Ensure adequate plant nutrition",
        ],
        "prevention": [
            "Plant resistant corn hybrids",
            "Rotate crops — avoid continuous corn planting",
            "Till under crop residue to reduce inoculum",
        ],
        "organic": [
            "Practice crop rotation with non-host crops",
            "Maintain balanced soil fertility",
        ],
    },
    "Common Rust": {
        "immediate": [
            "Apply fungicide (Azoxystrobin or Propiconazole) if severe",
            "Monitor fields regularly during tassel stage",
        ],
        "prevention": [
            "Plant rust-resistant corn hybrids",
            "Plant early to avoid peak rust conditions",
            "Diversify planting dates to reduce risk",
        ],
        "organic": [
            "Select resistant varieties — best organic strategy",
        ],
    },
    "Northern Leaf Blight": {
        "immediate": [
            "Apply foliar fungicide if lesions appear before tasseling",
            "Ensure plants are not nitrogen-deficient",
        ],
        "prevention": [
            "Use resistant hybrids with Ht genes",
            "Rotate with soybeans or other non-host crops",
            "Bury infected residue through tillage",
        ],
        "organic": [
            "Plant resistant varieties and practice crop rotation",
        ],
    },

    # ── GRAPE ─────────────────────────────────────────────────
    "Black Rot": {
        "immediate": [
            "Remove and destroy all infected berries and leaves",
            "Apply Mancozeb or Myclobutanil fungicide",
        ],
        "prevention": [
            "Maintain open canopy for good air circulation",
            "Remove fruit mummies from vines and ground",
            "Apply protective fungicide sprays from budbreak",
        ],
        "organic": [
            "Use copper-based sprays (Bordeaux mixture)",
            "Practice careful canopy management",
        ],
    },
    "Esca (Black Measles)": {
        "immediate": [
            "Remove and destroy severely infected cordons/trunks",
            "Apply wound protectant paste to large pruning cuts",
        ],
        "prevention": [
            "Prune during dry weather to minimize wound infection",
            "Apply wound sealant immediately after pruning",
            "Avoid large pruning wounds — use smaller renewal cuts",
        ],
        "organic": [
            "Use Trichoderma-based biological agents on pruning wounds",
        ],
    },
    "Leaf Blight (Isariopsis Leaf Spot)": {
        "immediate": [
            "Apply Mancozeb or copper-based fungicide",
            "Remove severely infected leaves",
        ],
        "prevention": [
            "Maintain good canopy management for airflow",
            "Apply preventive fungicide sprays during wet periods",
        ],
        "organic": [
            "Use copper or sulfur-based organic fungicides",
        ],
    },

    # ── ORANGE ────────────────────────────────────────────────
    "Haunglongbing (Citrus Greening)": {
        "immediate": [
            "Remove and destroy infected trees to prevent spread",
            "Control Asian citrus psyllid with insecticide application",
            "Apply enhanced nutritional programs to extend tree life",
        ],
        "prevention": [
            "Plant certified disease-free nursery trees",
            "Implement area-wide psyllid management programs",
            "Use systemic insecticides (Imidacloprid) for psyllid control",
            "Monitor trees regularly with visual inspection and PCR testing",
        ],
        "organic": [
            "Release natural predators (Tamarixia radiata) for psyllid biocontrol",
            "Use kaolin clay sprays to deter psyllid feeding",
        ],
    },

    # ── PEACH / PEPPER ────────────────────────────────────────
    "Bacterial Spot": {
        "immediate": [
            "Apply copper-based bactericide (copper hydroxide)",
            "Remove severely infected leaves and fruit",
            "Avoid overhead irrigation to reduce splash",
        ],
        "prevention": [
            "Plant resistant varieties when available",
            "Use disease-free seeds and transplants",
            "Practice crop rotation (2-3 year minimum)",
            "Stake plants to improve air circulation",
        ],
        "organic": [
            "Apply copper sprays at 7-10 day intervals",
            "Use bacterial biocontrol agents (Bacillus subtilis)",
        ],
    },

    # ── POTATO / TOMATO ───────────────────────────────────────
    "Early Blight": {
        "immediate": [
            "Remove and destroy infected lower leaves",
            "Apply fungicide (Chlorothalonil or Mancozeb)",
            "Avoid overhead watering — use drip irrigation",
        ],
        "prevention": [
            "Practice 2-3 year crop rotation with non-Solanaceous crops",
            "Mulch around plants to prevent soil splash",
            "Ensure adequate potassium and phosphorus nutrition",
            "Space plants for good air circulation",
        ],
        "organic": [
            "Apply copper-based fungicide (Bordeaux mixture)",
            "Use Bacillus subtilis-based biopesticide",
            "Mulch heavily to prevent soil-to-leaf splash",
        ],
    },
    "Late Blight": {
        "immediate": [
            "Remove and destroy ALL infected plant tissue immediately",
            "Apply systemic fungicide (Metalaxyl or Cymoxanil + Mancozeb)",
            "Do NOT compost infected material — burn or deep bury",
        ],
        "prevention": [
            "Plant certified disease-free seed potatoes/transplants",
            "Use resistant varieties (e.g., Defender, Mountain Magic for tomato)",
            "Avoid excessive irrigation — keep foliage dry",
            "Monitor weather — apply protective fungicide before wet periods",
        ],
        "organic": [
            "Apply copper-based sprays preventively before infection",
            "Use resistant varieties — this is the most effective organic strategy",
        ],
    },

    # ── RICE ──────────────────────────────────────────────────
    "Bacterial Leaf Blight": {
        "immediate": [
            "Drain water from heavily infected paddy fields",
            "Apply copper-based bactericide to reduce spread",
        ],
        "prevention": [
            "Plant resistant rice varieties (e.g., IR64, IRBB60)",
            "Avoid excessive nitrogen fertilization",
            "Use balanced fertilization with adequate potassium",
            "Ensure clean irrigation water sources",
        ],
        "organic": [
            "Practice crop rotation with non-rice crops",
            "Apply Pseudomonas fluorescens as biocontrol agent",
        ],
    },
    "Brown Spot": {
        "immediate": [
            "Apply fungicide (Mancozeb or Propiconazole)",
            "Ensure adequate plant nutrition (especially potassium)",
        ],
        "prevention": [
            "Use balanced fertilization — correct potassium deficiency",
            "Treat seeds with fungicide before planting",
            "Plant resistant varieties",
        ],
        "organic": [
            "Improve soil fertility with compost",
            "Use Trichoderma-based seed treatment",
        ],
    },
    "Leaf Blast": {
        "immediate": [
            "Apply fungicide (Tricyclazole or Isoprothiolane) immediately",
            "Reduce nitrogen application if excessive",
        ],
        "prevention": [
            "Plant blast-resistant varieties",
            "Avoid excessive nitrogen — use split applications",
            "Maintain adequate plant spacing",
            "Practice proper water management (avoid drought stress)",
        ],
        "organic": [
            "Apply silicon-based fertilizers to strengthen cell walls",
            "Use Trichoderma harzianum as seed treatment",
        ],
    },
    "Leaf Scald": {
        "immediate": [
            "Apply fungicide (Carbendazim or Propiconazole)",
        ],
        "prevention": [
            "Use resistant varieties",
            "Avoid excessive nitrogen",
            "Practice balanced fertilization",
        ],
        "organic": [
            "Maintain balanced soil nutrition",
        ],
    },
    "Narrow Brown Leaf Spot": {
        "immediate": [
            "Apply Propiconazole or Mancozeb fungicide",
        ],
        "prevention": [
            "Use resistant varieties",
            "Practice crop rotation",
            "Maintain balanced nitrogen levels",
        ],
        "organic": [
            "Use Trichoderma-based biocontrol agents",
        ],
    },
    "Rice Hispa": {
        "immediate": [
            "Clip and destroy leaves with visible mines and grubs",
            "Apply contact insecticide (Chlorpyrifos) if infestation is severe",
        ],
        "prevention": [
            "Avoid excessive nitrogen fertilizer",
            "Remove grassy weeds near paddy fields",
            "Use moderate plant spacing",
        ],
        "organic": [
            "Handpick adult beetles in small fields",
            "Release natural enemies (egg parasitoids)",
            "Apply neem-based insecticide",
        ],
    },
    "Sheath Blight": {
        "immediate": [
            "Apply fungicide (Hexaconazole or Validamycin)",
            "Reduce nitrogen application if growth is excessive",
        ],
        "prevention": [
            "Avoid excessive nitrogen fertilization",
            "Maintain recommended plant spacing",
            "Remove sclerotia from soil through deep plowing",
            "Use partially resistant varieties",
        ],
        "organic": [
            "Apply Trichoderma viride or Pseudomonas fluorescens",
            "Use silicon-rich fertilizers to strengthen stems",
        ],
    },

    # ── STRAWBERRY ────────────────────────────────────────────
    "Leaf Scorch": {
        "immediate": [
            "Remove and destroy infected leaves",
            "Apply Captan or copper-based fungicide",
        ],
        "prevention": [
            "Plant resistant varieties",
            "Avoid overhead irrigation",
            "Ensure proper plant spacing for air circulation",
            "Renovate strawberry beds after harvest",
        ],
        "organic": [
            "Apply copper-based organic fungicide",
            "Mulch to prevent soil splash",
        ],
    },

    # ── TOMATO ────────────────────────────────────────────────
    "Septoria Leaf Spot": {
        "immediate": [
            "Remove and destroy infected lower leaves",
            "Apply fungicide (Chlorothalonil or copper-based spray)",
            "Avoid overhead watering — switch to drip irrigation",
        ],
        "prevention": [
            "Practice 2-3 year crop rotation",
            "Mulch around plants to prevent rain splash from soil",
            "Stake and prune tomato plants for air circulation",
            "Remove plant debris at end of season",
        ],
        "organic": [
            "Apply copper-based fungicide every 7-10 days when wet",
            "Use Bacillus subtilis (Serenade) as biofungicide",
            "Apply thick straw mulch to prevent soil splash",
        ],
    },
    "Leaf Mold": {
        "immediate": [
            "Improve greenhouse ventilation immediately",
            "Remove heavily infected leaves",
            "Apply Chlorothalonil or Mancozeb fungicide",
        ],
        "prevention": [
            "Maintain greenhouse humidity below 85%",
            "Use resistant tomato varieties",
            "Space plants adequately for airflow",
            "Use drip irrigation instead of overhead",
        ],
        "organic": [
            "Improve ventilation — this is the most effective measure",
            "Apply potassium bicarbonate spray",
        ],
    },
    "Spider Mites Two-Spotted Spider Mite": {
        "immediate": [
            "Spray infested leaves with strong water jet to dislodge mites",
            "Apply miticide (Abamectin or Spiromesifen)",
            "Increase humidity around plants to slow mite reproduction",
        ],
        "prevention": [
            "Monitor plants regularly — check leaf undersides",
            "Avoid broad-spectrum insecticides that kill predatory mites",
            "Maintain adequate irrigation to prevent drought stress",
        ],
        "organic": [
            "Release predatory mites (Phytoseiulus persimilis)",
            "Apply neem oil or insecticidal soap spray",
            "Use horticultural oil for heavy infestations",
        ],
    },
    "Target Spot": {
        "immediate": [
            "Remove and destroy infected leaves",
            "Apply Chlorothalonil or Azoxystrobin fungicide",
        ],
        "prevention": [
            "Stake and prune plants for air circulation",
            "Practice crop rotation",
            "Avoid overhead irrigation",
        ],
        "organic": [
            "Apply copper-based fungicide preventively",
            "Mulch to reduce soil splash",
        ],
    },
    "Tomato Yellow Leaf Curl Virus": {
        "immediate": [
            "Remove and destroy infected plants — no cure exists",
            "Control whitefly populations with insecticide (Imidacloprid)",
            "Use yellow sticky traps to monitor and trap whiteflies",
        ],
        "prevention": [
            "Plant TYLCV-resistant tomato varieties",
            "Use reflective mulch to repel whiteflies",
            "Install fine-mesh insect netting over crops",
            "Remove weed hosts around growing areas",
        ],
        "organic": [
            "Use neem oil sprays for whitefly deterrence",
            "Release Encarsia formosa (whitefly parasitoid)",
            "Install insect exclusion netting",
        ],
    },
    "Tomato Mosaic Virus": {
        "immediate": [
            "Remove and destroy infected plants immediately",
            "Disinfect all tools with 10% bleach or milk solution",
            "Wash hands thoroughly before handling other plants",
        ],
        "prevention": [
            "Plant TMV-resistant tomato varieties (Tm-2 gene)",
            "Use certified virus-free seeds",
            "Never smoke or handle tobacco products near tomato plants",
            "Sanitize stakes, cages, and tools between seasons",
        ],
        "organic": [
            "Use milk spray (1:9) as a viral inactivator on tools",
            "Practice strict hygiene — primary organic control method",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# GENERIC FALLBACK TREATMENTS
# ═══════════════════════════════════════════════════════════════

GENERIC_TREATMENTS: Dict[str, Dict] = {
    "fungal": {
        "immediate": [
            "Remove and destroy infected plant parts",
            "Apply a broad-spectrum fungicide (Mancozeb or copper-based)",
            "Improve air circulation around affected plants",
        ],
        "prevention": [
            "Practice crop rotation with non-host crops",
            "Avoid overhead irrigation — use drip systems",
            "Ensure proper plant spacing for good airflow",
        ],
        "organic": [
            "Apply copper or sulfur-based organic fungicides",
            "Use Bacillus-based biofungicides",
        ],
    },
    "bacterial": {
        "immediate": [
            "Remove and destroy severely infected plants",
            "Apply copper-based bactericide",
            "Avoid working with plants when wet",
        ],
        "prevention": [
            "Use disease-free seeds and transplants",
            "Practice crop rotation",
            "Sanitize tools between plants",
        ],
        "organic": [
            "Apply copper hydroxide sprays",
            "Use bacterial biocontrol agents",
        ],
    },
    "viral": {
        "immediate": [
            "Remove and destroy infected plants — no cure for viral diseases",
            "Control insect vectors (aphids, whiteflies) with insecticide",
        ],
        "prevention": [
            "Plant virus-resistant varieties",
            "Control insect vectors through IPM",
            "Use clean planting material from certified sources",
            "Remove weed hosts near growing areas",
        ],
        "organic": [
            "Use insect exclusion netting",
            "Release beneficial insects for vector control",
            "Apply neem-based sprays for insect deterrence",
        ],
    },
    "unknown": {
        "immediate": [
            "Isolate affected plants to prevent potential spread",
            "Take clear photos and consult a local agricultural extension officer",
        ],
        "prevention": [
            "Maintain good crop hygiene and sanitation",
            "Ensure balanced nutrition and adequate irrigation",
        ],
        "organic": [
            "Focus on building soil health with compost and mulch",
        ],
    },
}


class TreatmentEngine:
    """
    Provides actionable treatment recommendations for detected diseases.

    Returns categorized treatments:
      • immediate : What to do NOW
      • prevention : How to prevent recurrence
      • organic : Chemical-free alternatives
    """

    @staticmethod
    def recommend(
        disease_name: str,
        disease_type: str = "unknown",
    ) -> Dict:
        """
        Get treatment recommendations for a disease.

        Parameters
        ----------
        disease_name : str
            Cleaned disease name (e.g. 'Septoria Leaf Spot').
        disease_type : str
            Disease type hint (Fungal, Bacterial, Viral).

        Returns
        -------
        dict
            immediate  : list[str]  — Urgent action steps
            prevention : list[str]  — Future prevention measures
            organic    : list[str]  — Chemical-free alternatives
            summary    : str        — One-line recommendation summary
        """
        if not disease_name or disease_name.lower() in ("healthy", "unknown", "unknown disease"):
            return {
                "immediate": [],
                "prevention": [
                    "Continue regular monitoring of plant health",
                    "Maintain balanced nutrition and proper irrigation",
                ],
                "organic": [],
                "summary": "No treatment needed — maintain good cultural practices."
                if disease_name.lower() == "healthy"
                else "Consult a plant pathologist for accurate diagnosis.",
            }

        # Look up specific disease
        info = TREATMENT_DATABASE.get(disease_name)

        if info:
            return {
                "immediate": info.get("immediate", []),
                "prevention": info.get("prevention", []),
                "organic": info.get("organic", []),
                "summary": f"Treat {disease_name} with targeted intervention — see detailed steps below.",
            }

        # Fallback to generic treatment by disease type
        dtype = disease_type.lower() if disease_type else "unknown"
        for key in ("fungal", "bacterial", "viral"):
            if key in dtype:
                dtype = key
                break
        else:
            dtype = "unknown"

        generic = GENERIC_TREATMENTS.get(dtype, GENERIC_TREATMENTS["unknown"])

        return {
            "immediate": generic.get("immediate", []),
            "prevention": generic.get("prevention", []),
            "organic": generic.get("organic", []),
            "summary": f"Apply general {dtype} disease management practices.",
        }
