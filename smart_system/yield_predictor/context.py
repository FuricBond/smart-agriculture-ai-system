"""
yield_predictor/context.py
===========================
Phase 3 — Context & Product Features.

Adds regional comparison, historical trend analysis, and smart alerts
on top of Phase-1 (prediction) and Phase-2 (intelligence) outputs.
Zero ML. Deterministic logic only. Phase 1 and 2 are NOT modified.

Public API
----------
    get_region_average(crop, state)           → float
    build_comparison(predicted_yield, crop, state) → dict
    get_trend_data(crop, state)               → dict
    analyze_trend(trend_data)                 → dict
    generate_alerts(predicted_yield, comparison, weather, risk) → list
    build_context(phase_full_result)          → dict
"""

from __future__ import annotations

from typing import Dict, List, Any


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — REGIONAL BASELINE KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════

# State-specific regional averages (hg/ha).
# Sourced from FAO / ICAR published averages for Indian states.
# Format: { state_lower: { crop: avg_hg_ha } }
_STATE_BASELINES: Dict[str, Dict[str, float]] = {
    "punjab":            {"Rice": 38000, "Wheat": 45000, "Maize": 30000,
                          "Sugarcane": 750000, "Cotton(lint)": 20000},
    "haryana":           {"Rice": 32000, "Wheat": 42000, "Maize": 27000,
                          "Sugarcane": 700000, "Cotton(lint)": 18000},
    "uttar pradesh":     {"Rice": 28000, "Wheat": 32000, "Maize": 22000,
                          "Sugarcane": 650000, "Cotton(lint)": 15000},
    "madhya pradesh":    {"Rice": 22000, "Wheat": 25000, "Maize": 20000,
                          "Soyabean": 10000,  "Cotton(lint)": 14000},
    "maharashtra":       {"Rice": 20000, "Wheat": 18000, "Maize": 22000,
                          "Sugarcane": 800000, "Cotton(lint)": 17000},
    "karnataka":         {"Rice": 25000, "Maize": 30000, "Ragi": 18000,
                          "Sugarcane": 900000, "Groundnut": 12000},
    "andhra pradesh":    {"Rice": 35000, "Maize": 35000, "Groundnut": 14000,
                          "Sugarcane": 850000, "Cotton(lint)": 16000},
    "telangana":         {"Rice": 34000, "Maize": 33000, "Groundnut": 13000,
                          "Cotton(lint)": 16000},
    "tamil nadu":        {"Rice": 30000, "Maize": 28000, "Sugarcane": 1100000,
                          "Groundnut": 10000, "Banana": 350000},
    "kerala":            {"Rice": 20000, "Coconut": 80000, "Banana": 400000,
                          "Tapioca": 250000},
    "west bengal":       {"Rice": 28000, "Wheat": 25000, "Jute": 25000,
                          "Potato": 240000},
    "bihar":             {"Rice": 22000, "Wheat": 28000, "Maize": 25000,
                          "Sugarcane": 580000},
    "odisha":            {"Rice": 18000, "Maize": 18000, "Groundnut": 9000},
    "rajasthan":         {"Wheat": 28000, "Barley": 18000, "Bajra": 8000,
                          "Maize": 20000, "Mustard": 10000},
    "gujarat":           {"Rice": 18000, "Wheat": 30000, "Cotton(lint)": 22000,
                          "Groundnut": 18000, "Sugarcane": 900000},
    "assam":             {"Rice": 18000, "Jute": 22000, "Tea": 15000},
    "himachal pradesh":  {"Wheat": 28000, "Maize": 22000, "Potato": 200000,
                          "Apple": 80000},
    "jammu and kashmir": {"Wheat": 25000, "Maize": 18000, "Rice": 20000},
}

# National crop baselines (hg/ha) — fallback when state not in table
_NATIONAL_BASELINES: Dict[str, float] = {
    "Rice":            32000,
    "Wheat":           28000,
    "Maize":           25000,
    "Sugarcane":       700000,
    "Cotton(lint)":    20000,
    "Groundnut":       15000,
    "Soyabean":        10000,
    "Sunflower":       9000,
    "Potato":          240000,
    "Onion":           180000,
    "Banana":          300000,
    "Coconut":         90000,
    "Arhar/Tur":       8000,
    "Gram":            10000,
    "Barley":          24000,
    "Jowar":           8000,
    "Bajra":           9000,
    "Jute":            25000,
    "Ragi":            18000,
    "Sesamum":         4000,
    "Linseed":         5000,
    "Turmeric":        50000,
    "Ginger":          120000,
    "_default":        30000,
}

# 5-year historical yield series (hg/ha) per crop × state.
# Used by the trend engine as a compact embedded dataset.
# Format: { state_lower: { crop: [y2018, y2019, y2020, y2021, y2022] } }
_TREND_DATA: Dict[str, Dict[str, List[float]]] = {
    "punjab": {
        "Rice":    [36000, 37000, 38000, 38500, 39000],
        "Wheat":   [42000, 43000, 44000, 45000, 45500],
    },
    "haryana": {
        "Rice":    [30000, 31000, 32000, 32500, 33000],
        "Wheat":   [40000, 40500, 41000, 42000, 42500],
        "Cotton(lint)": [17000, 17500, 18000, 17000, 18500],
    },
    "uttar pradesh": {
        "Rice":    [26000, 27000, 28000, 27500, 29000],
        "Wheat":   [30000, 31000, 32000, 32500, 33000],
        "Sugarcane": [600000, 620000, 640000, 650000, 660000],
    },
    "maharashtra": {
        "Sugarcane": [750000, 780000, 800000, 820000, 850000],
        "Cotton(lint)": [15000, 16000, 17000, 16500, 17500],
        "Soyabean": [9000, 9500, 10000, 9500, 10500],
    },
    "andhra pradesh": {
        "Rice":  [32000, 33000, 34000, 35000, 36000],
        "Maize": [32000, 33000, 34000, 35000, 36000],
        "Groundnut": [12000, 13000, 14000, 13500, 14500],
    },
    "karnataka": {
        "Maize":     [27000, 28000, 29000, 30000, 31000],
        "Sugarcane": [850000, 870000, 890000, 900000, 920000],
        "Groundnut": [10000, 11000, 12000, 11500, 12500],
    },
    "tamil nadu": {
        "Rice":     [28000, 29000, 30000, 29500, 31000],
        "Sugarcane": [1000000, 1050000, 1100000, 1080000, 1120000],
    },
    "west bengal": {
        "Rice":   [26000, 27000, 28000, 28500, 29000],
        "Potato": [220000, 230000, 240000, 235000, 245000],
        "Jute":   [23000, 24000, 25000, 24500, 25500],
    },
    "rajasthan": {
        "Wheat":  [25000, 26000, 27000, 28000, 28500],
        "Barley": [16000, 17000, 18000, 18500, 19000],
        "Bajra":  [7000,  7500,  8000,  8500,  9000],
    },
}

# National fallback trend (% growth per year from base)
_NATIONAL_TREND_GROWTH: Dict[str, float] = {
    "Rice":         0.015,
    "Wheat":        0.018,
    "Maize":        0.020,
    "Sugarcane":    0.010,
    "Cotton(lint)": 0.012,
    "_default":     0.015,
}

_TREND_BASE_YEAR = 2018
_TREND_YEARS = [2018, 2019, 2020, 2021, 2022]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — REGION COMPARISON ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def get_region_average(crop: str, state: str) -> float:
    """
    Return the regional average yield (hg/ha) for a crop in a given state.

    Looks up a state-specific table first; falls back to national average.

    Parameters
    ----------
    crop  : str — canonical crop name
    state : str — canonical state/area name

    Returns
    -------
    float — average yield in hg/ha
    """
    state_key = state.strip().lower()
    state_table = _STATE_BASELINES.get(state_key, {})
    if crop in state_table:
        return float(state_table[crop])
    return float(_NATIONAL_BASELINES.get(crop, _NATIONAL_BASELINES["_default"]))


def build_comparison(
    predicted_yield: float,
    crop: str,
    state: str,
) -> Dict[str, Any]:
    """
    Compare the predicted yield against the regional average.

    Returns
    -------
    dict
        region_average      : float — hg/ha baseline
        difference          : float — predicted - average
        difference_percent  : float — % above/below average
        status              : str   — ABOVE_AVERAGE | AVERAGE | BELOW_AVERAGE
        label               : str   — human-readable summary
    """
    avg  = get_region_average(crop, state)
    diff = predicted_yield - avg
    pct  = (diff / avg) * 100 if avg else 0.0

    if pct > 5:
        status = "ABOVE_AVERAGE"
        label  = f"Predicted yield is {abs(pct):.1f}% above the regional average."
    elif pct < -5:
        status = "BELOW_AVERAGE"
        label  = f"Predicted yield is {abs(pct):.1f}% below the regional average."
    else:
        status = "AVERAGE"
        label  = "Predicted yield is in line with the regional average."

    return {
        "region_average":     round(avg, 2),
        "difference":         round(diff, 2),
        "difference_percent": round(pct, 2),
        "status":             status,
        "label":              label,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — TREND ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def get_trend_data(crop: str, state: str) -> Dict[str, Any]:
    """
    Return a 5-year historical yield series for a crop in a state.

    Uses the embedded _TREND_DATA table; synthesises a national trend
    series when state-specific data is unavailable.

    Returns
    -------
    dict
        years  : list[int]
        yields : list[float]
        source : 'state' | 'national'
    """
    state_key = state.strip().lower()
    state_trends = _TREND_DATA.get(state_key, {})

    if crop in state_trends:
        return {
            "years":  _TREND_YEARS,
            "yields": state_trends[crop],
            "source": "state",
        }

    # Synthesise from national baseline using historical growth rate
    base  = _NATIONAL_BASELINES.get(crop, _NATIONAL_BASELINES["_default"])
    rate  = _NATIONAL_TREND_GROWTH.get(crop, _NATIONAL_TREND_GROWTH["_default"])
    years = _TREND_YEARS
    yields = [
        round(base * ((1 + rate) ** (y - _TREND_BASE_YEAR)), 0)
        for y in years
    ]
    return {
        "years":  years,
        "yields": yields,
        "source": "national",
    }


def analyze_trend(trend_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify whether yields are improving, declining, or stable.

    Uses first vs last value and also checks the last-2-year direction
    to catch recent reversals.

    Returns
    -------
    dict
        data         : the raw trend_data passed in
        insight      : IMPROVING | DECLINING | STABLE | VOLATILE
        change_abs   : float — last year minus first year (hg/ha)
        change_pct   : float — % change first → last
        recent_trend : IMPROVING | DECLINING | STABLE — based on last 2 years
        note         : str   — human-readable interpretation
    """
    yields = trend_data["yields"]
    years  = trend_data["years"]

    first, last = float(yields[0]), float(yields[-1])
    change_abs = round(last - first, 2)
    change_pct = round(((last - first) / first) * 100, 2) if first else 0.0

    # Overall trend
    if change_pct > 3:
        insight = "IMPROVING"
    elif change_pct < -3:
        insight = "DECLINING"
    else:
        insight = "STABLE"

    # Recent 2-year direction (last 2 values)
    if len(yields) >= 2:
        recent_delta = yields[-1] - yields[-2]
        if recent_delta > 0:
            recent_trend = "IMPROVING"
        elif recent_delta < 0:
            recent_trend = "DECLINING"
        else:
            recent_trend = "STABLE"
    else:
        recent_trend = insight

    # Volatility check — high std dev relative to mean
    mean_y = sum(yields) / len(yields)
    std_y  = (sum((y - mean_y) ** 2 for y in yields) / len(yields)) ** 0.5
    cv     = (std_y / mean_y) * 100 if mean_y else 0
    if cv > 10:
        insight = "VOLATILE"

    note = _trend_note(insight, recent_trend, change_pct,
                       years[-1], change_abs)

    return {
        "data":         trend_data,
        "insight":      insight,
        "change_abs":   change_abs,
        "change_pct":   change_pct,
        "recent_trend": recent_trend,
        "note":         note,
    }


def _trend_note(insight: str, recent: str, pct: float,
                last_year: int, abs_change: float) -> str:
    direction = "increased" if abs_change > 0 else "decreased"
    mapping = {
        "IMPROVING": (f"Yields have {direction} by {abs(pct):.1f}% "
                      f"over the past 5 years. Recent trend is {recent.lower()}."),
        "DECLINING": (f"Yields have {direction} by {abs(pct):.1f}% "
                      f"over the past 5 years. Intervention may be needed."),
        "STABLE":    (f"Yields have remained broadly stable "
                      f"(±{abs(pct):.1f}% over 5 years)."),
        "VOLATILE":  (f"High yield variability detected over the past "
                      f"5 years. Consistency improvements are recommended."),
    }
    return mapping.get(insight, "Trend data available.")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ALERT ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# Severity levels for alerts
_SEVERITY_CRITICAL = "CRITICAL"
_SEVERITY_WARNING  = "WARNING"
_SEVERITY_INFO     = "INFO"


def generate_alerts(
    predicted_yield: float,
    comparison:      Dict[str, Any],
    weather:         Dict[str, Any],
    risk:            str,
) -> List[Dict[str, str]]:
    """
    Generate a prioritised list of smart alerts from prediction context.

    Each alert is a dict with:
        severity : CRITICAL | WARNING | INFO
        code     : machine-readable identifier
        message  : human-readable description

    Parameters
    ----------
    predicted_yield : float
    comparison      : dict from build_comparison()
    weather         : dict with temperature, rainfall, humidity
    risk            : str — 'HIGH' | 'MEDIUM' | 'LOW'

    Returns
    -------
    list[dict]
    """
    alerts: List[Dict[str, str]] = []

    temperature = float(weather.get("temperature", 26))
    rainfall    = float(weather.get("rainfall", 900))
    humidity    = float(weather.get("humidity", 68))

    # ── Critical ──────────────────────────────────────────────────────────
    if risk == "HIGH":
        alerts.append({
            "severity": _SEVERITY_CRITICAL,
            "code":     "HIGH_PRODUCTION_RISK",
            "message":  "High overall risk detected. Immediate intervention required "
                        "to prevent significant yield loss.",
        })

    if rainfall < 400:
        alerts.append({
            "severity": _SEVERITY_CRITICAL,
            "code":     "SEVERE_DROUGHT_RISK",
            "message":  f"Critically low rainfall ({rainfall:.0f}mm). "
                        "Crop failure risk without emergency irrigation.",
        })

    if temperature > 40:
        alerts.append({
            "severity": _SEVERITY_CRITICAL,
            "code":     "EXTREME_HEAT",
            "message":  f"Extreme temperature ({temperature:.1f}°C). "
                        "Severe heat stress will impact pollination and yield.",
        })

    # ── Warnings ──────────────────────────────────────────────────────────
    if 400 <= rainfall < 600:
        alerts.append({
            "severity": _SEVERITY_WARNING,
            "code":     "LOW_RAINFALL",
            "message":  f"Low rainfall detected ({rainfall:.0f}mm). "
                        "Supplemental irrigation is strongly advised.",
        })

    if 35 < temperature <= 40:
        alerts.append({
            "severity": _SEVERITY_WARNING,
            "code":     "HIGH_TEMPERATURE_STRESS",
            "message":  f"High temperature ({temperature:.1f}°C) may reduce "
                        "grain filling and overall yield.",
        })

    if comparison["status"] == "BELOW_AVERAGE":
        alerts.append({
            "severity": _SEVERITY_WARNING,
            "code":     "YIELD_BELOW_REGIONAL_AVERAGE",
            "message":  f"Predicted yield is {abs(comparison['difference_percent']):.1f}% "
                        "below the regional average. Review crop management practices.",
        })

    if humidity > 85:
        alerts.append({
            "severity": _SEVERITY_WARNING,
            "code":     "HIGH_DISEASE_PRESSURE",
            "message":  f"High relative humidity ({humidity:.0f}%) increases risk "
                        "of fungal diseases. Apply preventive fungicide.",
        })

    if risk == "MEDIUM":
        alerts.append({
            "severity": _SEVERITY_WARNING,
            "code":     "MEDIUM_PRODUCTION_RISK",
            "message":  "Moderate risk level detected. Monitor crop closely "
                        "and act promptly on any stress signs.",
        })

    # ── Informational ─────────────────────────────────────────────────────
    if comparison["status"] == "ABOVE_AVERAGE":
        alerts.append({
            "severity": _SEVERITY_INFO,
            "code":     "YIELD_ABOVE_REGIONAL_AVERAGE",
            "message":  f"Predicted yield is {comparison['difference_percent']:.1f}% "
                        "above the regional average. Good agronomic conditions.",
        })

    if comparison["status"] == "AVERAGE":
        alerts.append({
            "severity": _SEVERITY_INFO,
            "code":     "YIELD_ON_TARGET",
            "message":  "Predicted yield aligns with regional average. "
                        "Maintain current practices.",
        })

    if rainfall > 2000:
        alerts.append({
            "severity": _SEVERITY_INFO,
            "code":     "HIGH_RAINFALL_NOTE",
            "message":  f"Above-average rainfall ({rainfall:.0f}mm). "
                        "Ensure field drainage to prevent waterlogging.",
        })

    # Sort: CRITICAL first, then WARNING, then INFO
    _order = {_SEVERITY_CRITICAL: 0, _SEVERITY_WARNING: 1, _SEVERITY_INFO: 2}
    alerts.sort(key=lambda a: _order.get(a["severity"], 3))

    return alerts


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — PUBLIC ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def build_context(full_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 3 entry point.  Accepts the merged Phase 1 + Phase 2 result dict
    and returns the context block.

    Parameters
    ----------
    full_result : dict
        Output of YieldPipeline.predict_full() with success=True.
        Must contain: predicted_yield, crop, area, weather, intelligence.

    Returns
    -------
    dict
        comparison : dict  — regional benchmark comparison
        trend      : dict  — 5-year trend analysis
        alerts     : list  — prioritised smart alerts
    """
    predicted_yield = full_result["predicted_yield"]
    crop            = full_result["crop"]
    state           = full_result["area"]
    weather         = full_result["weather"]

    # Extract overall_risk from Phase-2 intelligence block
    intel = full_result.get("intelligence", {})
    risk_block = intel.get("risk", {})
    overall_risk = (
        risk_block.get("overall_risk", "LOW")
        if isinstance(risk_block, dict)
        else str(risk_block)
    )

    comparison = build_comparison(predicted_yield, crop, state)
    trend_data = get_trend_data(crop, state)
    trend      = analyze_trend(trend_data)
    alerts     = generate_alerts(predicted_yield, comparison, weather, overall_risk)

    return {
        "comparison": comparison,
        "trend":      trend,
        "alerts":     alerts,
    }
