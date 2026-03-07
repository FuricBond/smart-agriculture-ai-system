"""
Risk Analysis Engine — Smart Agriculture System v2.0
=======================================================
Professional-grade risk assessment engine computing:

    • Soil Quality Index (SQI)  — 0 to 100 weighted score
    • NPK Balance Ratio        — nutrient harmony metric
    • Disease Severity Level    — based on pathogen database
    • Yield Classification      — contextual yield assessment
    • Overall Farm Health Score — composite risk indicator

Scoring Methodology
-------------------
The Soil Quality Index uses a weighted multi-factor model
grounded in agronomic principles:

    Factor               Weight    Max Points
    ─────────────────    ──────    ──────────
    pH Balance           20%       20
    NPK Nutrients        30%       30
    NPK Balance Ratio    10%       10
    Temperature          12%       12
    Humidity             13%       13
    Water Availability   15%       15

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple, Optional

from . import config


class RiskAnalyzer:
    """
    Comprehensive Farm Risk Analysis Engine.

    This class provides static methods for computing:
    - Soil Quality Index (0–100) with detailed breakdown
    - Disease severity classification
    - Yield level classification
    - Overall farm health assessment
    """

    # ───────────────────────────────────────────────────────────
    # SOIL QUALITY INDEX (SQI)
    # ───────────────────────────────────────────────────────────

    @staticmethod
    def calculate_soil_quality(
        N: float, P: float, K: float,
        ph: float, temperature: float,
        humidity: float, rainfall: float
    ) -> Dict:
        """
        Calculate a comprehensive Soil Quality Index (0–100).

        The score uses a Gaussian-proximity model: each factor
        is scored by how close the value is to its ideal midpoint,
        with penalties that increase smoothly as the value deviates.

        Parameters
        ----------
        N : float
            Nitrogen level (kg/ha)
        P : float
            Phosphorus level (kg/ha)
        K : float
            Potassium level (kg/ha)
        ph : float
            Soil pH value (0–14)
        temperature : float
            Ambient temperature (°C)
        humidity : float
            Relative humidity (%)
        rainfall : float
            Annual/seasonal rainfall (mm)

        Returns
        -------
        dict
            score     : float (0–100)
            level     : str   (POOR / FAIR / GOOD / EXCELLENT)
            breakdown : dict  with per-factor scores and max values
            issues    : list  of identified problems with advice
            npk_ratio : dict  with N:P:K balance information
        """
        issues: List[str] = []

        # ── Helper: Gaussian proximity scoring ────────────────
        def _gaussian_score(
            value: float, ideal_min: float, ideal_max: float,
            max_points: float, sigma_scale: float = 0.4
        ) -> float:
            """
            Score a value based on proximity to ideal range.
            Returns max_points when inside ideal range, and
            decays via Gaussian as value moves outside.
            """
            if ideal_min <= value <= ideal_max:
                return max_points
            if value < ideal_min:
                deviation = ideal_min - value
                sigma = (ideal_max - ideal_min) * sigma_scale + 1
            else:
                deviation = value - ideal_max
                sigma = (ideal_max - ideal_min) * sigma_scale + 1
            return max_points * math.exp(-(deviation ** 2) / (2 * sigma ** 2))

        # ── pH Score (0–20) ──────────────────────────────────
        ph_score = _gaussian_score(ph, config.IDEAL_PH_MIN,
                                   config.IDEAL_PH_MAX, 20.0, 0.5)
        if ph < 5.0:
            issues.append(
                f"Soil is highly acidic (pH {ph:.1f}) — apply agricultural "
                f"lime at 2–4 tons/ha to raise pH")
        elif ph < config.IDEAL_PH_MIN:
            issues.append(
                f"Soil is slightly acidic (pH {ph:.1f}) — light liming "
                f"or organic matter addition recommended")
        elif ph > 8.5:
            issues.append(
                f"Soil is highly alkaline (pH {ph:.1f}) — apply elemental "
                f"sulfur at 200–500 kg/ha")
        elif ph > config.IDEAL_PH_MAX:
            issues.append(
                f"Soil is slightly alkaline (pH {ph:.1f}) — add compost "
                f"or peat to gradually lower pH")

        # ── Nitrogen Score (0–10) ─────────────────────────────
        n_score = _gaussian_score(N, config.IDEAL_N_MIN,
                                  config.IDEAL_N_MAX, 10.0)
        if N < config.IDEAL_N_MIN * 0.5:
            issues.append(
                f"Severely low Nitrogen ({N:.0f} kg/ha) — apply Urea "
                f"at 100–150 kg/ha immediately")
        elif N < config.IDEAL_N_MIN:
            issues.append(
                f"Low Nitrogen ({N:.0f} kg/ha) — apply Urea or "
                f"Ammonium Sulfate at 50–100 kg/ha")
        elif N > config.IDEAL_N_MAX * 1.5:
            issues.append(
                f"Excess Nitrogen ({N:.0f} kg/ha) — risk of leaf burn "
                f"and groundwater contamination")
        elif N > config.IDEAL_N_MAX:
            issues.append(
                f"Slightly high Nitrogen ({N:.0f} kg/ha) — reduce "
                f"fertilizer application rate")

        # ── Phosphorus Score (0–10) ───────────────────────────
        p_score = _gaussian_score(P, config.IDEAL_P_MIN,
                                  config.IDEAL_P_MAX, 10.0)
        if P < config.IDEAL_P_MIN * 0.5:
            issues.append(
                f"Severely low Phosphorus ({P:.0f} kg/ha) — apply DAP "
                f"or TSP at 100–150 kg/ha")
        elif P < config.IDEAL_P_MIN:
            issues.append(
                f"Low Phosphorus ({P:.0f} kg/ha) — apply DAP or Single "
                f"Super Phosphate at 50–80 kg/ha")
        elif P > config.IDEAL_P_MAX:
            issues.append(
                f"Excess Phosphorus ({P:.0f} kg/ha) — may block "
                f"micronutrient uptake (Zn, Fe)")

        # ── Potassium Score (0–10) ────────────────────────────
        k_score = _gaussian_score(K, config.IDEAL_K_MIN,
                                  config.IDEAL_K_MAX, 10.0)
        if K < config.IDEAL_K_MIN * 0.5:
            issues.append(
                f"Severely low Potassium ({K:.0f} kg/ha) — apply MOP "
                f"(Muriate of Potash) at 80–120 kg/ha")
        elif K < config.IDEAL_K_MIN:
            issues.append(
                f"Low Potassium ({K:.0f} kg/ha) — apply Potash "
                f"fertilizer at 40–80 kg/ha")
        elif K > config.IDEAL_K_MAX * 1.5:
            issues.append(
                f"Excess Potassium ({K:.0f} kg/ha) — may interfere "
                f"with Magnesium and Calcium uptake")

        # ── NPK Balance Score (0–10) ──────────────────────────
        # A balanced N:P:K ratio is crucial for crop health.
        # Ideal ratio is roughly 4:2:1 to 2:1:1 depending on crop.
        npk_balance_score = 10.0
        npk_info: Dict[str, str] = {}

        if P > 0 and K > 0:
            np_ratio = N / (P + 1e-5)
            nk_ratio = N / (K + 1e-5)
            pk_ratio = P / (K + 1e-5)

            npk_info['N:P ratio'] = f"{np_ratio:.2f}"
            npk_info['N:K ratio'] = f"{nk_ratio:.2f}"
            npk_info['P:K ratio'] = f"{pk_ratio:.2f}"

            # Penalize imbalanced ratios
            penalties = 0.0
            nk_lo, nk_hi = config.IDEAL_NK_RATIO
            np_lo, np_hi = config.IDEAL_NP_RATIO

            if not (np_lo <= np_ratio <= np_hi):
                deviation = min(abs(np_ratio - np_lo), abs(np_ratio - np_hi))
                penalties += min(5, deviation * 1.5)
                if np_ratio > np_hi:
                    npk_info['note'] = "Nitrogen-heavy vs Phosphorus"
                else:
                    npk_info['note'] = "Phosphorus-heavy vs Nitrogen"

            if not (nk_lo <= nk_ratio <= nk_hi):
                deviation = min(abs(nk_ratio - nk_lo), abs(nk_ratio - nk_hi))
                penalties += min(5, deviation * 1.5)

            npk_balance_score = max(0, 10.0 - penalties)
            if penalties > 3:
                issues.append(
                    f"NPK ratio is imbalanced (N:P:K = {N:.0f}:{P:.0f}:{K:.0f}) "
                    f"— adjust fertilizer proportions")
        else:
            npk_info['note'] = "Cannot compute ratio (P or K is zero)"
            npk_balance_score = 5.0

        npk_total = n_score + p_score + k_score + npk_balance_score

        # ── Temperature Score (0–12) ──────────────────────────
        temp_score = _gaussian_score(temperature, config.IDEAL_TEMP_MIN,
                                     config.IDEAL_TEMP_MAX, 12.0, 0.3)
        if temperature < 5:
            issues.append(
                f"Dangerously low temperature ({temperature:.1f}°C) — "
                f"frost damage likely, use frost covers")
        elif temperature < config.IDEAL_TEMP_MIN:
            issues.append(
                f"Low temperature ({temperature:.1f}°C) — growth may "
                f"slow, consider greenhouse or row covers")
        elif temperature > 42:
            issues.append(
                f"Extreme heat ({temperature:.1f}°C) — severe heat "
                f"stress, use shade nets and increase irrigation")
        elif temperature > config.IDEAL_TEMP_MAX:
            issues.append(
                f"High temperature ({temperature:.1f}°C) — heat stress "
                f"risk, mulching advised")

        # ── Humidity Score (0–13) ─────────────────────────────
        hum_score = _gaussian_score(humidity, config.IDEAL_HUMIDITY_MIN,
                                    config.IDEAL_HUMIDITY_MAX, 13.0, 0.35)
        if humidity < 20:
            issues.append(
                f"Very low humidity ({humidity:.0f}%) — wilting risk, "
                f"increase irrigation frequency")
        elif humidity < config.IDEAL_HUMIDITY_MIN:
            issues.append(
                f"Low humidity ({humidity:.0f}%) — consider misting "
                f"or drip irrigation to raise moisture")
        elif humidity > 95:
            issues.append(
                f"Saturated humidity ({humidity:.0f}%) — high fungal "
                f"disease risk, improve ventilation")
        elif humidity > config.IDEAL_HUMIDITY_MAX:
            issues.append(
                f"High humidity ({humidity:.0f}%) — disease-favorable "
                f"conditions, monitor for fungal infection")

        # ── Water / Rainfall Score (0–15) ─────────────────────
        water_score = _gaussian_score(rainfall, config.IDEAL_RAINFALL_MIN,
                                      config.IDEAL_RAINFALL_MAX, 15.0, 0.5)
        if rainfall < 30:
            issues.append(
                f"Critical water deficit ({rainfall:.0f}mm) — "
                f"drought conditions, urgent irrigation needed")
        elif rainfall < config.IDEAL_RAINFALL_MIN:
            issues.append(
                f"Low rainfall ({rainfall:.0f}mm) — set up supplemental "
                f"drip or sprinkler irrigation")
        elif rainfall > 2000:
            issues.append(
                f"Extreme rainfall ({rainfall:.0f}mm) — severe flooding "
                f"risk, ensure drainage and raised beds")
        elif rainfall > config.IDEAL_RAINFALL_MAX:
            issues.append(
                f"Excess rainfall ({rainfall:.0f}mm) — waterlogging "
                f"risk, improve field drainage")

        # ── Total Score ───────────────────────────────────────
        total_score = min(100.0,
                          ph_score + npk_total + temp_score
                          + hum_score + water_score)

        # Classify level
        if total_score >= 80:
            level = 'EXCELLENT'
        elif total_score >= 60:
            level = 'GOOD'
        elif total_score >= 40:
            level = 'FAIR'
        else:
            level = 'POOR'

        return {
            'score': round(total_score, 1),
            'level': level,
            'breakdown': {
                'pH Balance':        (round(ph_score, 1), 20),
                'Nitrogen':          (round(n_score, 1), 10),
                'Phosphorus':        (round(p_score, 1), 10),
                'Potassium':         (round(k_score, 1), 10),
                'NPK Balance':       (round(npk_balance_score, 1), 10),
                'Temperature':       (round(temp_score, 1), 12),
                'Humidity':          (round(hum_score, 1), 13),
                'Water':             (round(water_score, 1), 15),
            },
            'issues': issues,
            'npk_ratio': npk_info,
        }

    # ───────────────────────────────────────────────────────────
    # DISEASE RISK ASSESSMENT
    # ───────────────────────────────────────────────────────────

    # Pathogen severity database (keyword → severity weight 1–10)
    _DISEASE_SEVERITY: Dict[str, int] = {
        # Critical (9–10)
        'late_blight':      10,  'bacterial_wilt':    10,
        'citrus_greening':  10,  'brown_streak':       9,
        'mosaic_virus':      9,  'mosaic':             9,
        'tungro':            9,  'black_rot':          9,
        # High (7–8)
        'early_blight':      8,  'common_rust':        8,
        'septoria':          8,  'downy_mildew':       8,
        'bacterial_spot':    7,  'powdery_mildew':     7,
        'leaf_scorch':       7,  'anthracnose':        7,
        'blight':            7,  'wilt':               7,
        # Moderate (4–6)
        'leaf_spot':         6,  'target_spot':        6,
        'scab':              6,  'curl':               6,
        'yellow_leaf':       5,  'leaf_mold':          5,
        'rot':               5,  'mite':               4,
        'spider_mite':       4,
        # Low (1–3)
        'deficiency':        3,  'nutrient':           3,
    }

    @staticmethod
    def assess_disease_risk(
        disease_name: str,
        confidence: float
    ) -> Dict:
        """
        Assess disease risk level based on detected disease and
        prediction confidence, using a pathogen severity database.

        The risk level is computed as:
            risk_score = severity_weight × confidence_factor × 10

        Parameters
        ----------
        disease_name : str
            Full disease class name (e.g., 'Tomato___Late_blight')
        confidence : float
            Prediction confidence (0–100 percentage)

        Returns
        -------
        dict
            risk_level   : str   (LOW / MODERATE / HIGH / CRITICAL)
            risk_score   : float (0–100 composite score)
            severity     : int   (1–10 disease severity)
            description  : str   (human-readable explanation)
        """
        name_lower = disease_name.lower()

        # ── Check healthy ─────────────────────────────────────
        if 'healthy' in name_lower or 'normal' in name_lower:
            return {
                'risk_level':  'LOW',
                'risk_score':  5.0,
                'severity':    0,
                'description': 'Plant appears healthy — no disease detected'
            }

        # ── Look up severity ──────────────────────────────────
        severity = 5  # Default moderate severity
        for keyword, sev in RiskAnalyzer._DISEASE_SEVERITY.items():
            if keyword in name_lower:
                severity = max(severity, sev)

        # ── Compute composite risk score ──────────────────────
        # Normalize confidence to [0, 1] factor
        conf_factor = min(confidence, 100.0) / 100.0

        # Risk = severity × confidence, scaled to 0–100
        risk_score = severity * conf_factor * 10.0
        risk_score = min(100.0, risk_score)

        # ── Classify risk level ───────────────────────────────
        if risk_score >= 75:
            risk_level = 'CRITICAL'
            desc = (f"Severe disease (severity {severity}/10) detected "
                    f"with {confidence:.0f}% confidence — immediate "
                    f"action required")
        elif risk_score >= 50:
            risk_level = 'HIGH'
            desc = (f"Significant disease (severity {severity}/10) — "
                    f"treatment and monitoring urgently recommended")
        elif risk_score >= 25:
            risk_level = 'MODERATE'
            desc = (f"Disease detected (severity {severity}/10) — "
                    f"monitoring and preventive treatment advised")
        else:
            risk_level = 'LOW'
            desc = (f"Minor concern (severity {severity}/10) — continue "
                    f"monitoring, no immediate action needed")

        return {
            'risk_level':  risk_level,
            'risk_score':  round(risk_score, 1),
            'severity':    severity,
            'description': desc,
        }

    # ───────────────────────────────────────────────────────────
    # YIELD CLASSIFICATION
    # ───────────────────────────────────────────────────────────

    @staticmethod
    def classify_yield(predicted_yield: float) -> Dict:
        """
        Classify predicted yield into Low / Medium / High
        categories with descriptive assessment.

        Parameters
        ----------
        predicted_yield : float
            Predicted yield value from the model.

        Returns
        -------
        dict
            level       : str   (LOW / MEDIUM / HIGH)
            description : str
            percentile  : str   (descriptive position)
        """
        if predicted_yield < config.YIELD_LOW_THRESHOLD:
            pct = min(100, (predicted_yield / config.YIELD_LOW_THRESHOLD) * 100)
            return {
                'level': 'LOW',
                'description': (
                    f'Predicted yield ({predicted_yield:,.0f}) is below '
                    f'{config.YIELD_LOW_THRESHOLD:,} — '
                    f'improvement strategies needed'
                ),
                'percentile': f'{pct:.0f}% of low threshold'
            }
        elif predicted_yield > config.YIELD_HIGH_THRESHOLD:
            return {
                'level': 'HIGH',
                'description': (
                    f'Predicted yield ({predicted_yield:,.0f}) exceeds '
                    f'{config.YIELD_HIGH_THRESHOLD:,} — '
                    f'excellent agricultural potential'
                ),
                'percentile': 'Above high threshold'
            }
        else:
            span = config.YIELD_HIGH_THRESHOLD - config.YIELD_LOW_THRESHOLD
            pos = predicted_yield - config.YIELD_LOW_THRESHOLD
            pct = (pos / span) * 100
            return {
                'level': 'MEDIUM',
                'description': (
                    f'Predicted yield ({predicted_yield:,.0f}) is in '
                    f'moderate range — optimization opportunities exist'
                ),
                'percentile': f'{pct:.0f}% within medium band'
            }

    # ───────────────────────────────────────────────────────────
    # OVERALL FARM HEALTH ASSESSMENT
    # ───────────────────────────────────────────────────────────

    @staticmethod
    def compute_overall_health(
        soil_quality: Dict,
        disease_risk: Dict,
        yield_classification: Dict
    ) -> Dict:
        """
        Compute an overall farm health score from all analyses.

        Weighting: Soil 40%, Disease 30%, Yield 30%

        Parameters
        ----------
        soil_quality : dict
            Output from calculate_soil_quality()
        disease_risk : dict
            Output from assess_disease_risk()
        yield_classification : dict
            Output from classify_yield()

        Returns
        -------
        dict
            overall_score  : float (0–100)
            overall_grade  : str   (A/B/C/D/F)
            summary        : str
        """
        # Soil component (0–100 already)
        soil_score = soil_quality.get('score', 50.0)

        # Disease component: invert risk to health
        risk_score = disease_risk.get('risk_score', 50.0)
        disease_health = max(0, 100.0 - risk_score)

        # Yield component
        yield_map = {'HIGH': 100.0, 'MEDIUM': 60.0, 'LOW': 25.0}
        yield_level = yield_classification.get('level', 'MEDIUM')
        yield_score = yield_map.get(yield_level, 50.0)

        # Weighted average
        overall = (soil_score * 0.40
                   + disease_health * 0.30
                   + yield_score * 0.30)
        overall = min(100.0, max(0.0, overall))

        # Letter grade
        if overall >= 85:
            grade, summary = 'A', 'Excellent farm conditions overall'
        elif overall >= 70:
            grade, summary = 'B', 'Good conditions with minor improvements possible'
        elif overall >= 55:
            grade, summary = 'C', 'Fair conditions — multiple areas need attention'
        elif overall >= 40:
            grade, summary = 'D', 'Below average — significant improvements needed'
        else:
            grade, summary = 'F', 'Poor farm conditions — urgent intervention required'

        return {
            'overall_score': round(overall, 1),
            'overall_grade': grade,
            'summary':       summary,
            'components': {
                'Soil Quality':  round(soil_score, 1),
                'Disease Health': round(disease_health, 1),
                'Yield Outlook':  round(yield_score, 1),
            }
        }
