"""
Smart Recommendations Engine — Smart Agriculture System v2.0
================================================================
Generates intelligent, context-aware farming recommendations by
combining insights from all three prediction models:

    • Disease Detection  → targeted treatment plans
    • Crop Recommendation → growing advice & soil amendments
    • Yield Prediction    → productivity improvement strategies
    • Cross-Module Logic  → combined disease+crop+yield advisory

The engine produces actionable advice grounded in agronomic
best practices rather than generic suggestions.

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

from __future__ import annotations

from typing import Dict, List, Optional


class RecommendationEngine:
    """
    Generates intelligent farming recommendations based on
    combined prediction results from all system modules.
    """

    # ───────────────────────────────────────────────────────────
    # DISEASE TREATMENTS
    # ───────────────────────────────────────────────────────────

    @staticmethod
    def get_disease_treatment(
        disease_name: str,
        plant: str,
        condition: str
    ) -> List[str]:
        """
        Generate disease-specific treatment recommendations.

        Uses a keyword-matching approach against a knowledge base
        of plant pathology treatments.

        Parameters
        ----------
        disease_name : str
            Full disease class name (e.g. 'Tomato___Late_blight')
        plant : str
            Plant name extracted from class
        condition : str
            Disease condition extracted from class

        Returns
        -------
        list[str]
            Ordered list of treatment recommendations.
        """
        name_lower = disease_name.lower()

        # Healthy plant
        if 'healthy' in name_lower or 'normal' in name_lower:
            return [
                f"Your {plant} plant appears healthy — no treatment needed",
                "Continue regular monitoring every 5–7 days",
                "Maintain balanced fertilizer schedule",
                "Ensure adequate but not excessive watering",
                "Practice preventive fungicide spraying during wet seasons",
            ]

        # ── Bacterial Diseases ────────────────────────────────
        if 'bacterial' in name_lower:
            return [
                f"Apply copper-based bactericide (Bordeaux mixture) to {plant}",
                "Remove and destroy all severely infected plant parts",
                "Avoid overhead watering — use drip irrigation instead",
                "Disinfect tools with 70% isopropyl alcohol after each use",
                "Improve air circulation by proper plant spacing",
                "Apply streptomycin sulfate spray if available and legal",
                "Do not work with plants when foliage is wet",
            ]

        # ── Late Blight ───────────────────────────────────────
        if 'late_blight' in name_lower or 'late blight' in name_lower:
            return [
                f"URGENT: Apply Metalaxyl + Mancozeb combination immediately",
                f"Remove ALL infected {plant} leaves and burn/discard them",
                "Switch to drip irrigation — avoid wetting foliage",
                "Apply fungicide every 7 days during wet/humid weather",
                "Plant blight-resistant varieties in next planting cycle",
                "Maintain proper spacing (60–90 cm) for air circulation",
                "Monitor neighbouring plants — blight spreads rapidly",
            ]

        # ── Early Blight ──────────────────────────────────────
        if 'early_blight' in name_lower or 'early blight' in name_lower:
            return [
                "Apply Chlorothalonil or Copper hydroxide fungicide",
                f"Remove lower infected leaves from {plant} plants",
                "Mulch (5–8 cm) around base to prevent soil splashing",
                "Ensure balanced nitrogen — avoid excess N fertilization",
                "Rotate crops every 2–3 years (avoid Solanaceae rotation)",
                "Water at the base of plants early in the morning",
            ]

        # ── General Blight ────────────────────────────────────
        if 'blight' in name_lower:
            return [
                "Apply broad-spectrum fungicide (Mancozeb or Copper)",
                f"Remove infected {plant} tissue and destroy it",
                "Improve drainage and air circulation in the field",
                "Rotate with non-related crops next season",
                "Avoid excessive nitrogen fertilization",
            ]

        # ── Powdery Mildew ────────────────────────────────────
        if 'powdery_mildew' in name_lower or 'powdery mildew' in name_lower:
            return [
                "Apply sulfur-based fungicide or Neem oil spray",
                "Spray potassium bicarbonate solution (1 tbsp/gallon)",
                "Improve air circulation — prune crowded branches",
                "Avoid overhead watering (ironically, mildew favours dry leaves)",
                "Remove severely affected leaves and discard",
                "Organic option: milk spray (40% milk : 60% water)",
            ]

        # ── Downy Mildew ──────────────────────────────────────
        if 'downy_mildew' in name_lower or 'downy mildew' in name_lower:
            return [
                "Apply Metalaxyl or Copper oxychloride fungicide",
                "Remove and destroy infected foliage",
                "Avoid overhead irrigation — keep leaves dry",
                "Ensure adequate spacing between plants",
                "Plant resistant varieties when available",
            ]

        # ── Rust Diseases ─────────────────────────────────────
        if 'rust' in name_lower:
            return [
                "Apply Propiconazole or Triadimefon fungicide",
                f"Remove rust-affected {plant} leaves immediately",
                "Apply sulfur dust as preventive measure",
                "Avoid wetting leaves during irrigation",
                "Plant rust-resistant cultivars",
                "Destroy all crop residue after harvest",
            ]

        # ── Leaf Spot / Target Spot / Septoria ────────────────
        if ('spot' in name_lower or 'septoria' in name_lower):
            return [
                "Apply Chlorothalonil or Copper-based fungicide",
                f"Remove spotted {plant} leaves to prevent spread",
                "Improve air circulation between plants",
                "Avoid working with plants when foliage is wet",
                "Practice 2–3 year crop rotation",
                "Apply mulch to reduce soil splash onto leaves",
            ]

        # ── Mosaic / Viral Diseases ───────────────────────────
        if ('mosaic' in name_lower or 'virus' in name_lower
                or 'curl' in name_lower or 'streak' in name_lower):
            return [
                f"IMPORTANT: Remove and destroy infected {plant} plants entirely",
                "Viral diseases have NO chemical cure — prevention only",
                "Control insect vectors (aphids, whiteflies, thrips) immediately",
                "Apply Imidacloprid or Neem-based insecticide for vectors",
                "Use insect-proof mesh netting on nursery seedlings",
                "Plant certified virus-free seed/transplants",
                "Disinfect all tools between handling plants",
                "Use reflective mulch to deter flying insect vectors",
            ]

        # ── Rot Diseases ──────────────────────────────────────
        if 'rot' in name_lower:
            return [
                f"Remove and destroy all rotting {plant} tissue",
                "Improve drainage — avoid waterlogging at all costs",
                "Apply Copper hydroxide or Trichoderma bio-fungicide",
                "Reduce watering frequency and volume",
                "Ensure good air flow around plant base",
                "Avoid planting too deep or mounding soil against stems",
            ]

        # ── Scab Diseases ─────────────────────────────────────
        if 'scab' in name_lower:
            return [
                "Apply Captan or Myclobutanil fungicide",
                "Remove fallen leaves to reduce overwintering spores",
                "Prune trees/plants to improve air circulation",
                "Apply lime sulfur during dormant season (perennials)",
                "Plant scab-resistant varieties",
            ]

        # ── Leaf Mold ─────────────────────────────────────────
        if 'mold' in name_lower:
            return [
                "Increase ventilation — open greenhouse vents/sides",
                "Reduce humidity to below 85% if possible",
                "Apply Chlorothalonil or Mancozeb fungicide",
                "Remove heavily infected lower leaves",
                "Avoid overhead watering",
            ]

        # ── General Fallback ──────────────────────────────────
        return [
            f"Inspect {plant} plant closely for disease spread pattern",
            "Apply broad-spectrum fungicide as a precautionary measure",
            "Remove and safely destroy affected plant parts",
            "Improve air circulation in the field/greenhouse",
            "Consult a local agricultural extension officer for diagnosis",
            "Practice crop rotation to break disease cycles",
        ]

    # ───────────────────────────────────────────────────────────
    # CROP GROWING ADVICE
    # ───────────────────────────────────────────────────────────

    @staticmethod
    def get_crop_advice(
        crop_name: str,
        N: float, P: float, K: float,
        temperature: float, humidity: float,
        ph: float, rainfall: float
    ) -> List[str]:
        """
        Generate crop-specific growing advice based on soil
        conditions and environmental parameters.

        Returns
        -------
        list[str]
            Ordered list of crop growing recommendations.
        """
        recommendations: List[str] = []
        crop_lower = crop_name.lower()

        # ── Season Recommendations ────────────────────────────
        kharif = ['rice', 'cotton', 'maize', 'jute', 'mango', 'papaya',
                  'watermelon', 'muskmelon', 'pigeonpeas', 'mothbeans',
                  'mungbean', 'blackgram', 'sugarcane', 'soybean']
        rabi   = ['wheat', 'barley', 'lentil', 'chickpea', 'peas',
                  'apple', 'grapes', 'mustard', 'gram']
        zaid   = ['cucumber', 'pumpkin', 'bitter gourd', 'watermelon']

        if any(c in crop_lower for c in kharif):
            recommendations.append(
                f"Plant {crop_name} during Kharif season (June–October) "
                f"for optimal monsoon utilization")
        elif any(c in crop_lower for c in rabi):
            recommendations.append(
                f"Plant {crop_name} during Rabi season (November–March) "
                f"for cooler weather advantages")
        elif any(c in crop_lower for c in zaid):
            recommendations.append(
                f"Plant {crop_name} during Zaid season (March–June) "
                f"with adequate irrigation")
        else:
            recommendations.append(
                f"Consult local agricultural calendar for optimal "
                f"{crop_name} planting window")

        # ── NPK-Based Fertilizer Recommendations ─────────────
        if N < 40:
            recommendations.append(
                f"Nitrogen is low ({N:.0f} kg/ha) — apply Urea at "
                f"100–150 kg/ha in split doses")
        elif N > 140:
            recommendations.append(
                f"Nitrogen is high ({N:.0f} kg/ha) — reduce N "
                f"fertilizer to avoid toxicity and lodging")

        if P < 20:
            recommendations.append(
                f"Phosphorus is low ({P:.0f} kg/ha) — apply DAP or "
                f"SSP at 80–120 kg/ha at planting time")
        elif P > 80:
            recommendations.append(
                f"Phosphorus is adequate ({P:.0f} kg/ha) — skip "
                f"additional P fertilizer this season")

        if K < 20:
            recommendations.append(
                f"Potassium is low ({K:.0f} kg/ha) — apply MOP at "
                f"60–100 kg/ha for disease resistance")
        elif K > 80:
            recommendations.append(
                f"Potassium is adequate ({K:.0f} kg/ha) — maintain "
                f"current K levels")

        # ── pH Adjustments ────────────────────────────────────
        if ph < 5.5:
            recommendations.append(
                f"Soil pH ({ph:.1f}) is too acidic for {crop_name} — "
                f"apply agricultural lime at 2–4 tons/ha")
        elif ph < 6.0:
            recommendations.append(
                f"Soil pH ({ph:.1f}) is slightly acidic — apply "
                f"dolomite lime at 1–2 tons/ha before planting")
        elif ph > 8.0:
            recommendations.append(
                f"Soil pH ({ph:.1f}) is alkaline — apply elemental "
                f"sulfur at 200–400 kg/ha to acidify")
        elif ph > 7.5:
            recommendations.append(
                f"Soil pH ({ph:.1f}) is slightly alkaline — add "
                f"compost and organic matter to buffer pH")
        else:
            recommendations.append(
                f"Soil pH ({ph:.1f}) is ideal for most crops")

        # ── Water Management ──────────────────────────────────
        if rainfall < 50:
            recommendations.append(
                "Set up drip irrigation immediately — critical water deficit")
        elif rainfall < 100:
            recommendations.append(
                "Install supplemental irrigation (drip or sprinkler)")
        elif rainfall > 1500:
            recommendations.append(
                "Ensure proper field drainage — consider raised beds")
        elif rainfall > 1200:
            recommendations.append(
                "Monitor for waterlogging — maintain drainage channels")

        # ── Temperature Management ────────────────────────────
        if temperature > 40:
            recommendations.append(
                "Use 50% shade nets and increase watering to 2× daily")
        elif temperature > 35:
            recommendations.append(
                "Apply straw mulch (5–8 cm) to reduce soil temperature")
        elif temperature < 10:
            recommendations.append(
                "Use row covers or low tunnel greenhouse for frost protection")
        elif temperature < 15:
            recommendations.append(
                "Consider using plastic mulch to warm soil")

        # ── General Best Practices ────────────────────────────
        recommendations.append(
            f"Apply organic compost (2–3 tons/ha) for {crop_name} "
            f"soil structure improvement")
        recommendations.append(
            "Rotate crops every 2–3 seasons to maintain soil health")

        return recommendations

    # ───────────────────────────────────────────────────────────
    # YIELD IMPROVEMENT ADVICE
    # ───────────────────────────────────────────────────────────

    @staticmethod
    def get_yield_advice(
        yield_level: str,
        predicted_yield: float,
        crop: str
    ) -> List[str]:
        """
        Generate yield improvement recommendations based on
        predicted yield classification.

        Parameters
        ----------
        yield_level : str
            'LOW', 'MEDIUM', or 'HIGH'
        predicted_yield : float
            Predicted yield value
        crop : str
            Crop name for context

        Returns
        -------
        list[str]
        """
        if yield_level == 'LOW':
            return [
                f"Predicted {crop} yield is low ({predicted_yield:,.0f})",
                "Conduct comprehensive soil test for macro & micro nutrients",
                "Switch to high-yield certified seed varieties (HYV)",
                "Implement integrated pest management (IPM) programme",
                "Install drip/sprinkler irrigation for water efficiency",
                "Apply balanced NPK + micronutrients (Zn, B, Fe) based on soil test",
                "Use green manuring or cover crops before next planting",
                "Consider intercropping to optimize land and nutrient use",
                "Seek guidance from your district agricultural extension office",
            ]
        elif yield_level == 'MEDIUM':
            return [
                f"Predicted {crop} yield is moderate ({predicted_yield:,.0f}) — room to improve",
                "Optimize fertilizer timing: split N into 3 doses across growth stages",
                "Consider precision agriculture tools (soil sensors, variable rate tech)",
                "Add micronutrient supplements (Zinc Sulfate, Borax) if deficient",
                "Improve irrigation scheduling based on crop evapotranspiration",
                "Monitor crop health weekly for early disease/pest detection",
                "Use treated seed for better germination and seedling vigour",
            ]
        else:  # HIGH
            return [
                f"Predicted {crop} yield is excellent ({predicted_yield:,.0f})",
                "Current practices are effective — maintain and document them",
                "Focus on quality improvement (grain size, protein, colour)",
                "Consider expanding cultivated area or crop diversification",
                "Invest in post-harvest storage and value-added processing",
                "Share best practices with neighbouring farmers",
            ]

    # ───────────────────────────────────────────────────────────
    # CROSS-MODULE COMBINED ADVISORY
    # ───────────────────────────────────────────────────────────

    @staticmethod
    def get_combined_advisory(
        disease_result: Optional[Dict],
        crop_result: Optional[Dict],
        yield_result: Optional[Dict],
        soil_quality: Optional[Dict],
        disease_risk: Optional[Dict],
    ) -> List[str]:
        """
        Generate cross-module intelligent recommendations that
        consider relationships between disease, crop, yield,
        and soil conditions simultaneously.

        This is the "smart" layer that no individual engine can
        provide on its own.

        Parameters
        ----------
        disease_result : dict or None
            Disease prediction result
        crop_result : dict or None
            Crop recommendation result
        yield_result : dict or None
            Yield prediction result
        soil_quality : dict or None
            Soil quality analysis
        disease_risk : dict or None
            Disease risk assessment

        Returns
        -------
        list[str]
            Cross-module advisory recommendations
        """
        advisories: List[str] = []

        has_disease = disease_result and disease_result.get('success', False)
        has_crop    = crop_result and crop_result.get('success', False)
        has_yield   = yield_result and yield_result.get('success', False)
        has_soil    = soil_quality and soil_quality.get('score', 0) > 0

        # ── Disease + Soil interaction ────────────────────────
        if has_disease and has_soil:
            disease_name = disease_result.get('disease_name', '').lower()
            soil_score = soil_quality.get('score', 50)
            issues = soil_quality.get('issues', [])

            is_diseased = ('healthy' not in disease_name
                           and 'normal' not in disease_name)

            # High humidity + disease → fungal nexus warning
            humid_issues = [i for i in issues if 'humidity' in i.lower()
                            and 'high' in i.lower()]
            if is_diseased and humid_issues:
                advisories.append(
                    "⚡ HIGH ALERT: Disease detected in high-humidity "
                    "conditions — fungal spread risk is elevated. "
                    "Improve ventilation and apply fungicide immediately")

            # Poor soil + disease → compounded stress
            if is_diseased and soil_score < 40:
                advisories.append(
                    "⚡ Plant is under dual stress (disease + poor soil). "
                    "Prioritize disease treatment first, then soil "
                    "amendments after recovery")

            # Good soil + healthy → positive reinforcement
            if not is_diseased and soil_score >= 70:
                advisories.append(
                    "✅ Healthy plant with good soil conditions — "
                    "excellent baseline for strong crop performance")

        # ── Disease + Yield interaction ───────────────────────
        if has_disease and has_yield:
            disease_name = disease_result.get('disease_name', '').lower()
            is_diseased = ('healthy' not in disease_name
                           and 'normal' not in disease_name)
            y_level = yield_result.get('yield_level', 'MEDIUM')

            if is_diseased and y_level == 'LOW':
                advisories.append(
                    "⚡ Disease + low yield indicate systemic crop "
                    "stress. Consider replacing current crop variety "
                    "with disease-resistant, high-yield alternatives")

            if is_diseased and y_level == 'HIGH':
                advisories.append(
                    "⚠ Despite high yield potential, untreated disease "
                    "could reduce actual harvest by 20–60%. "
                    "Treat disease NOW to protect yield")

        # ── Crop + Soil interaction ───────────────────────────
        if has_crop and has_soil:
            crop_name = crop_result.get('crop_name', '').lower()
            soil_level = soil_quality.get('level', 'FAIR')
            soil_issues = soil_quality.get('issues', [])

            # Water-intensive crop + low rainfall
            water_crops = ['rice', 'sugarcane', 'jute', 'banana']
            low_water = any('water deficit' in i.lower()
                            or 'low rainfall' in i.lower()
                            for i in soil_issues)

            if any(c in crop_name for c in water_crops) and low_water:
                advisories.append(
                    f"⚠ {crop_result.get('crop_name', '')} requires high "
                    f"water but rainfall is low. Set up reliable irrigation "
                    f"before planting, or consider a drought-tolerant "
                    f"alternative (Millet, Sorghum, Chickpea)")

            # Acidic soil + specific crops
            acidic = any('acidic' in i.lower() for i in soil_issues)
            if acidic and any(c in crop_name for c in ['rice', 'tea', 'coffee']):
                advisories.append(
                    f"ℹ {crop_result.get('crop_name', '')} tolerates "
                    f"slightly acidic soil — minor pH correction may "
                    f"still be beneficial but not critical")

        # ── Yield + Soil interaction ──────────────────────────
        if has_yield and has_soil:
            y_level = yield_result.get('yield_level', 'MEDIUM')
            soil_score = soil_quality.get('score', 50)

            if y_level == 'LOW' and soil_score < 50:
                advisories.append(
                    "⚡ Low yield + poor soil quality — this is likely "
                    "a soil-driven problem. Invest in soil rehabilitation: "
                    "organic matter, balanced NPK, pH correction")

            if y_level == 'HIGH' and soil_score >= 75:
                advisories.append(
                    "✅ High yield potential with excellent soil — "
                    "conditions are optimal for premium crop production")

        # ── Fallback if no cross-module insights ──────────────
        if not advisories:
            advisories.append(
                "ℹ Complete data from all modules is needed for "
                "cross-module analysis. Ensure all steps are run "
                "for comprehensive advisory")

        return advisories
