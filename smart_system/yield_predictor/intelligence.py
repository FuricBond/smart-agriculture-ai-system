"""
yield_predictor/intelligence.py
================================
Phase 2 — Intelligence Layer.

Adds Explanation + Recommendation + Risk Assessment on top of the
Phase-1 prediction output.  Zero ML — rule-based logic only.
Phase-1 pipeline is NOT modified.

Public API
----------
    generate_explanation(features, weather)  → dict
    generate_recommendations(crop, weather, yield_level, season)  → dict
    assess_risk(crop, weather, year, yield_level)  → dict
    build_intelligence(phase1_result)  → dict
"""

from __future__ import annotations

from typing import Dict, List, Any


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — AGRONOMIC KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════

# Ideal temperature ranges (°C) per crop — (min_ok, max_ok)
_TEMP_RANGES: Dict[str, tuple] = {
    "Rice":              (22, 35),
    "Wheat":             (12, 25),
    "Maize":             (18, 32),
    "Barley":            (12, 25),
    "Bajra":             (25, 38),
    "Jowar":             (25, 35),
    "Sugarcane":         (24, 38),
    "Cotton(lint)":      (21, 35),
    "Groundnut":         (25, 35),
    "Soyabean":          (20, 32),
    "Sunflower":         (20, 30),
    "Potato":            (15, 25),
    "Onion":             (13, 25),
    "Banana":            (24, 35),
    "Coconut":           (25, 35),
    "Arhar/Tur":         (25, 35),
    "Gram":              (10, 25),
    "Linseed":           (10, 20),
    "Sesamum":           (25, 35),
    "Jute":              (24, 37),
    "Turmeric":          (20, 30),
    "Ginger":            (20, 30),
    "_default":          (20, 35),
}

# Ideal annual rainfall (mm) per crop — (min_ok, max_ok)
_RAIN_RANGES: Dict[str, tuple] = {
    "Rice":              (1200, 2500),
    "Wheat":             (300,  700),
    "Maize":             (500,  1200),
    "Barley":            (300,  600),
    "Bajra":             (200,  600),
    "Jowar":             (300,  900),
    "Sugarcane":         (1500, 3000),
    "Cotton(lint)":      (500,  1200),
    "Groundnut":         (500,  1200),
    "Soyabean":          (700,  1400),
    "Sunflower":         (400,  900),
    "Potato":            (500,  800),
    "Onion":             (400,  800),
    "Banana":            (1500, 3000),
    "Coconut":           (1200, 2500),
    "Arhar/Tur":         (600,  1500),
    "Gram":              (300,  700),
    "Linseed":           (300,  600),
    "Sesamum":           (400,  800),
    "Jute":              (1500, 3000),
    "Turmeric":          (1500, 2500),
    "Ginger":            (1500, 2500),
    "_default":          (500,  1500),
}

# Ideal humidity (%) per crop — (min_ok, max_ok)
_HUMIDITY_RANGES: Dict[str, tuple] = {
    "Rice":         (70, 90),
    "Wheat":        (40, 65),
    "Maize":        (50, 75),
    "Potato":       (60, 80),
    "Sugarcane":    (65, 90),
    "Cotton(lint)": (50, 70),
    "_default":     (50, 80),
}

# Season suitability map: crop → list of suitable seasons
_SEASON_FIT: Dict[str, List[str]] = {
    "Rice":              ["Kharif", "Whole Year"],
    "Wheat":             ["Rabi", "Winter"],
    "Maize":             ["Kharif", "Rabi", "Summer"],
    "Barley":            ["Rabi", "Winter"],
    "Bajra":             ["Kharif"],
    "Jowar":             ["Kharif", "Rabi"],
    "Sugarcane":         ["Whole Year"],
    "Cotton(lint)":      ["Kharif"],
    "Groundnut":         ["Kharif", "Rabi", "Summer"],
    "Soyabean":          ["Kharif"],
    "Sunflower":         ["Rabi", "Kharif", "Summer"],
    "Potato":            ["Rabi", "Autumn", "Winter"],
    "Onion":             ["Rabi", "Kharif"],
    "Banana":            ["Whole Year"],
    "Coconut":           ["Whole Year"],
    "Arhar/Tur":         ["Kharif", "Whole Year"],
    "Gram":              ["Rabi", "Winter"],
    "Turmeric":          ["Kharif", "Whole Year"],
    "Ginger":            ["Kharif"],
    "Jute":              ["Kharif"],
}

# Fertilizer N-P-K recommendations (kg/ha) per crop: (N, P, K)
_FERTILIZER: Dict[str, tuple] = {
    "Rice":         (120, 60, 60),
    "Wheat":        (120, 60, 40),
    "Maize":        (150, 75, 40),
    "Sugarcane":    (250, 112, 112),
    "Cotton(lint)": (120, 60, 60),
    "Groundnut":    (20,  40, 40),
    "Soyabean":     (20,  80, 40),
    "Potato":       (180, 120, 150),
    "Onion":        (100, 50,  75),
    "Banana":       (200, 60,  300),
    "Arhar/Tur":    (20,  50, 30),
    "Gram":         (20,  60, 20),
    "Barley":       (80,  40, 30),
    "Sunflower":    (90,  60, 30),
    "_default":     (80,  40, 40),
}

# Irrigation need: crop → 'low' | 'medium' | 'high'
_IRRIGATION_NEED: Dict[str, str] = {
    "Rice":         "high",
    "Sugarcane":    "high",
    "Banana":       "high",
    "Potato":       "high",
    "Wheat":        "medium",
    "Maize":        "medium",
    "Onion":        "medium",
    "Soyabean":     "medium",
    "Groundnut":    "medium",
    "Cotton(lint)": "medium",
    "Bajra":        "low",
    "Jowar":        "low",
    "Gram":         "low",
    "Arhar/Tur":    "low",
    "Barley":       "low",
    "Sunflower":    "low",
    "_default":     "medium",
}


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — EXPLANATION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def generate_explanation(
    features: Dict[str, Any],
    weather:  Dict[str, Any],
) -> Dict[str, Any]:
    """
    Explain WHY the model produced its prediction by evaluating each
    input feature against agronomic ideal ranges.

    Parameters
    ----------
    features : dict
        Keys: crop, state, season, year  (from Phase-1 canonical values)
    weather : dict
        Keys: temperature, rainfall, humidity  (from Phase-1 weather fetch)

    Returns
    -------
    dict
        factors   : list[dict]  — per-factor analysis
        summary   : str         — one-sentence plain English summary
        driver    : str         — dominant yield driver
    """
    crop     = features.get("crop", "")
    season   = features.get("season", "")
    year     = features.get("year", 2020)
    temp     = float(weather.get("temperature", 26))
    rain     = float(weather.get("rainfall", 900))
    humidity = float(weather.get("humidity", 68))

    factors: List[Dict] = []

    # ── Factor 1: Temperature ────────────────────────────────────────────
    tmin, tmax = _TEMP_RANGES.get(crop, _TEMP_RANGES["_default"])
    temp_status, temp_impact = _range_check(temp, tmin, tmax, "°C")
    factors.append({
        "factor":  "Temperature",
        "value":   f"{temp:.1f}°C",
        "ideal":   f"{tmin}–{tmax}°C",
        "status":  temp_status,
        "impact":  temp_impact,
        "message": _temp_message(crop, temp, tmin, tmax),
    })

    # ── Factor 2: Rainfall ───────────────────────────────────────────────
    rmin, rmax = _RAIN_RANGES.get(crop, _RAIN_RANGES["_default"])
    rain_status, rain_impact = _range_check(rain, rmin, rmax, "mm")
    factors.append({
        "factor":  "Rainfall",
        "value":   f"{rain:.0f}mm",
        "ideal":   f"{rmin}–{rmax}mm",
        "status":  rain_status,
        "impact":  rain_impact,
        "message": _rain_message(crop, rain, rmin, rmax),
    })

    # ── Factor 3: Humidity ───────────────────────────────────────────────
    hmin, hmax = _HUMIDITY_RANGES.get(crop, _HUMIDITY_RANGES["_default"])
    hum_status, hum_impact = _range_check(humidity, hmin, hmax, "%")
    factors.append({
        "factor":  "Humidity",
        "value":   f"{humidity:.1f}%",
        "ideal":   f"{hmin}–{hmax}%",
        "status":  hum_status,
        "impact":  hum_impact,
        "message": _humidity_message(crop, humidity, hmin, hmax),
    })

    # ── Factor 4: Season suitability ─────────────────────────────────────
    suitable_seasons = _SEASON_FIT.get(crop, [])
    if suitable_seasons:
        is_fit   = season in suitable_seasons
        s_status = "optimal" if is_fit else "suboptimal"
        s_impact = "positive" if is_fit else "negative"
        s_msg    = (
            f"{season} is a suitable season for {crop}."
            if is_fit else
            f"{season} is not ideal for {crop}. "
            f"Preferred seasons: {', '.join(suitable_seasons)}."
        )
    else:
        s_status = "unknown"
        s_impact = "neutral"
        s_msg    = f"No season preference data available for {crop}."

    factors.append({
        "factor":  "Season",
        "value":   season,
        "ideal":   ", ".join(suitable_seasons) if suitable_seasons else "Any",
        "status":  s_status,
        "impact":  s_impact,
        "message": s_msg,
    })

    # ── Factor 5: Temporal trend ─────────────────────────────────────────
    trend_msg, trend_status = _temporal_trend(year)
    factors.append({
        "factor":  "Year Trend",
        "value":   str(year),
        "ideal":   "Recent years preferred (post-2010)",
        "status":  trend_status,
        "impact":  "positive" if trend_status == "optimal" else "neutral",
        "message": trend_msg,
    })

    # ── Identify dominant driver ─────────────────────────────────────────
    # Find the factor with most extreme deviation
    impact_order = {"high_negative": 0, "negative": 1, "neutral": 2,
                    "positive": 3, "high_positive": 4}
    worst = min(factors, key=lambda f: impact_order.get(f["impact"], 2))
    driver = worst["factor"] if worst["impact"] in ("negative", "high_negative") \
             else "Seasonal conditions"

    # ── Build plain-English summary ──────────────────────────────────────
    good_count = sum(1 for f in factors if f["status"] == "optimal")
    bad_count  = sum(1 for f in factors if f["status"] in ("low", "high", "suboptimal"))

    if bad_count == 0:
        summary = (f"Conditions are highly favourable for {crop} in {season}. "
                   f"All key factors are within ideal ranges.")
    elif bad_count >= 3:
        summary = (f"Multiple factors are unfavourable for {crop}. "
                   f"The primary concern is {driver.lower()}.")
    else:
        concerns = [f["factor"] for f in factors
                    if f["status"] in ("low", "high", "suboptimal")]
        summary = (f"Conditions for {crop} are partially favourable. "
                   f"Concern(s): {', '.join(concerns).lower()}.")

    return {
        "factors": factors,
        "summary": summary,
        "driver":  driver,
    }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _range_check(value: float, vmin: float, vmax: float,
                 unit: str = "") -> tuple:
    """Returns (status_str, impact_str) for a value vs [vmin, vmax]."""
    margin = (vmax - vmin) * 0.25  # 25% tolerance band

    if value < vmin - margin:
        return "low", "high_negative"
    elif value < vmin:
        return "low", "negative"
    elif value > vmax + margin:
        return "high", "high_negative"
    elif value > vmax:
        return "high", "negative"
    else:
        return "optimal", "positive"


def _temp_message(crop: str, temp: float, tmin: float, tmax: float) -> str:
    if temp < tmin:
        diff = tmin - temp
        return (f"Temperature is {diff:.1f}°C below the minimum for {crop}. "
                f"Cold stress may reduce yield.")
    elif temp > tmax:
        diff = temp - tmax
        return (f"Temperature is {diff:.1f}°C above the ideal maximum for {crop}. "
                f"Heat stress may reduce grain filling.")
    return f"Temperature is within the optimal range for {crop}."


def _rain_message(crop: str, rain: float, rmin: float, rmax: float) -> str:
    irr = _IRRIGATION_NEED.get(crop, _IRRIGATION_NEED["_default"])
    if rain < rmin:
        if irr == "low":
            return (f"Rainfall ({rain:.0f}mm) is below ideal but {crop} "
                    f"is relatively drought-tolerant.")
        return (f"Rainfall deficit of {rmin - rain:.0f}mm. "
                f"Supplemental irrigation is critical for {crop}.")
    elif rain > rmax:
        return (f"Excess rainfall ({rain:.0f}mm) may cause waterlogging "
                f"and increase disease pressure for {crop}.")
    return f"Rainfall is adequate for {crop} requirements."


def _humidity_message(crop: str, humidity: float, hmin: float, hmax: float) -> str:
    if humidity < hmin:
        return f"Low humidity ({humidity:.0f}%) may cause water stress for {crop}."
    elif humidity > hmax:
        return (f"High humidity ({humidity:.0f}%) increases fungal disease "
                f"risk for {crop}.")
    return f"Humidity is within the acceptable range for {crop}."


def _temporal_trend(year: int) -> tuple:
    if year >= 2015:
        return ("Recent year — benefits from modern cultivar adoption "
                "and improved agronomic practices.", "optimal")
    elif year >= 2005:
        return ("Mid-range year — moderate technology adoption expected.", "neutral")
    return ("Older year — lower baseline technology levels in training data.", "neutral")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — RECOMMENDATION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def generate_recommendations(
    crop:        str,
    weather:     Dict[str, Any],
    yield_level: str,
    season:      str,
) -> Dict[str, Any]:
    """
    Generate actionable, agronomic recommendations based on crop,
    weather conditions, and yield prediction outcome.

    Parameters
    ----------
    crop        : str  — canonical crop name
    weather     : dict — temperature, rainfall, humidity
    yield_level : str  — LOW | MEDIUM | HIGH
    season      : str  — e.g. 'Kharif'

    Returns
    -------
    dict
        fertilizer    : dict   — NPK advice
        irrigation    : dict   — water management advice
        pest_disease  : list   — watch list items
        best_practices: list   — top practices for this crop × yield level
        priority      : str    — IMMEDIATE | MODERATE | ROUTINE
    """
    temp     = float(weather.get("temperature", 26))
    rain     = float(weather.get("rainfall", 900))
    humidity = float(weather.get("humidity", 68))

    recs: Dict[str, Any] = {}

    # ── Fertilizer ────────────────────────────────────────────────────────
    n, p, k   = _FERTILIZER.get(crop, _FERTILIZER["_default"])
    fert_note = _fertilizer_note(yield_level, n, p, k)
    recs["fertilizer"] = {
        "N_kg_per_ha":  n,
        "P_kg_per_ha":  p,
        "K_kg_per_ha":  k,
        "timing":       _fertilizer_timing(crop, season),
        "note":         fert_note,
    }

    # ── Irrigation ────────────────────────────────────────────────────────
    irr_need  = _IRRIGATION_NEED.get(crop, _IRRIGATION_NEED["_default"])
    rmin, rmax = _RAIN_RANGES.get(crop, _RAIN_RANGES["_default"])
    irr_status = "deficit" if rain < rmin else "surplus" if rain > rmax else "adequate"
    recs["irrigation"] = {
        "crop_need":  irr_need,
        "status":     irr_status,
        "advice":     _irrigation_advice(crop, irr_need, irr_status, rain, rmin),
    }

    # ── Pest & Disease watch list ─────────────────────────────────────────
    recs["pest_disease"] = _pest_watchlist(crop, temp, humidity, season)

    # ── Best practices ────────────────────────────────────────────────────
    recs["best_practices"] = _best_practices(crop, yield_level, weather)

    # ── Priority level ────────────────────────────────────────────────────
    if yield_level == "LOW":
        recs["priority"] = "IMMEDIATE"
    elif yield_level == "MEDIUM":
        recs["priority"] = "MODERATE"
    else:
        recs["priority"] = "ROUTINE"

    return recs


# ── Recommendation helpers ────────────────────────────────────────────────────

def _fertilizer_note(level: str, n: int, p: int, k: int) -> str:
    if level == "LOW":
        return (f"Increase N to {int(n * 1.15)} kg/ha to compensate for "
                f"predicted low yield. Apply split doses.")
    elif level == "HIGH":
        return (f"Standard N-P-K ({n}-{p}-{k}) is adequate. "
                f"Avoid over-fertilization to prevent lodging.")
    return (f"Apply recommended N-P-K ({n}-{p}-{k} kg/ha) "
            f"in split doses at sowing and top-dressing.")


def _fertilizer_timing(crop: str, season: str) -> str:
    timings = {
        "Rice":         "50% N at basal, 25% at tillering, 25% at panicle initiation.",
        "Wheat":        "50% N + full P + K at sowing; remaining N at first irrigation.",
        "Maize":        "1/3 N at sowing, 1/3 at knee-high stage, 1/3 at tasselling.",
        "Sugarcane":    "1/3 at planting, 1/3 at 60 days, 1/3 at 120 days.",
        "Cotton(lint)": "N in 3 splits — at sowing, squaring, and boll development.",
        "Potato":       "Full P+K and 50% N at planting; remaining N at earthing-up.",
        "Groundnut":    "Full fertilizer as basal dose at sowing.",
        "_default":     "Apply as basal dose with top-dressing at vegetative stage.",
    }
    return timings.get(crop, timings["_default"])


def _irrigation_advice(crop: str, need: str, status: str,
                        rain: float, rmin: float) -> str:
    if status == "deficit":
        shortfall = round(rmin - rain, 0)
        if need == "high":
            return (f"Critical irrigation needed. Rainfall deficit of ~{shortfall:.0f}mm. "
                    f"Irrigate at critical growth stages (tillering, flowering, grain-fill).")
        elif need == "medium":
            return (f"Supplement with ~{shortfall * 0.7:.0f}mm irrigation at "
                    f"key growth stages. Monitor soil moisture.")
        return (f"Rainfall is low but {crop} has moderate drought tolerance. "
                f"One or two life-saving irrigations may be beneficial.")
    elif status == "surplus":
        return ("Excess moisture detected. Ensure proper field drainage to "
                "prevent waterlogging and root diseases.")
    return "Rainfall is adequate. Irrigate only during extended dry spells."


def _pest_watchlist(crop: str, temp: float, humidity: float,
                    season: str) -> List[Dict]:
    """Return top pest/disease threats based on crop × weather conditions."""
    threats = {
        "Rice":    [
            {"name": "Blast",          "trigger": "High humidity + moderate temp",
             "risk": "high" if humidity > 80 and 20 < temp < 28 else "moderate"},
            {"name": "Brown Planthopper","trigger": "Warm, humid conditions",
             "risk": "high" if humidity > 75 and temp > 26 else "low"},
        ],
        "Wheat":   [
            {"name": "Yellow Rust",    "trigger": "Cool, moist weather",
             "risk": "high" if humidity > 70 and temp < 20 else "low"},
            {"name": "Aphids",         "trigger": "Warm dry conditions",
             "risk": "moderate" if temp > 22 and humidity < 55 else "low"},
        ],
        "Maize":   [
            {"name": "Fall Armyworm",  "trigger": "Warm humid season",
             "risk": "high" if humidity > 65 and temp > 25 else "moderate"},
            {"name": "Stalk Borer",    "trigger": "Temperature > 27°C",
             "risk": "high" if temp > 27 else "low"},
        ],
        "Cotton(lint)": [
            {"name": "Bollworm",       "trigger": "Dry heat stress",
             "risk": "high" if temp > 32 and humidity < 55 else "moderate"},
            {"name": "Whitefly",       "trigger": "Hot dry weather",
             "risk": "high" if temp > 30 else "low"},
        ],
        "Potato":  [
            {"name": "Late Blight",    "trigger": "Cool wet conditions",
             "risk": "high" if humidity > 80 and temp < 20 else "moderate"},
            {"name": "Early Blight",   "trigger": "Warm humid weather",
             "risk": "moderate" if humidity > 70 else "low"},
        ],
        "Sugarcane": [
            {"name": "Red Rot",        "trigger": "Waterlogged soils",
             "risk": "high" if humidity > 85 else "low"},
            {"name": "Shoot Borer",    "trigger": "High temperature",
             "risk": "moderate" if temp > 28 else "low"},
        ],
    }
    base = threats.get(crop, [
        {"name": "Fungal diseases", "trigger": "High humidity",
         "risk": "moderate" if humidity > 75 else "low"},
        {"name": "Sucking pests",   "trigger": "Warm dry weather",
         "risk": "moderate" if temp > 30 else "low"},
    ])
    return base


def _best_practices(crop: str, yield_level: str,
                    weather: Dict[str, Any]) -> List[str]:
    """Return a concise list of the top 4–5 best practices."""
    rain     = float(weather.get("rainfall", 900))
    temp     = float(weather.get("temperature", 26))
    humid    = float(weather.get("humidity", 68))

    general = [
        f"Use certified high-yielding variety seeds for {crop}.",
        "Follow soil-test based fertilizer application.",
        "Maintain field records for input costs and yield benchmarking.",
    ]

    specific: List[str] = []

    if yield_level == "LOW":
        specific += [
            "Conduct soil health assessment — pH, NPK, and micro-nutrients.",
            "Consider intercropping to reduce risk and improve overall returns.",
        ]
    if rain < _RAIN_RANGES.get(crop, _RAIN_RANGES["_default"])[0]:
        specific.append("Adopt micro-irrigation (drip/sprinkler) to improve water use efficiency.")
    if rain > _RAIN_RANGES.get(crop, _RAIN_RANGES["_default"])[1]:
        specific.append("Construct field bunds and drainage channels to prevent waterlogging.")
    if temp > _TEMP_RANGES.get(crop, _TEMP_RANGES["_default"])[1]:
        specific.append("Apply mulching to reduce soil temperature and conserve moisture.")
    if humid > 80:
        specific.append("Improve crop spacing and ventilation to reduce fungal disease pressure.")

    return (specific + general)[:5]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — RISK ASSESSMENT ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# Risk scoring: each risk factor contributes points (0–30) to a total score.
# Final risk score 0–100 → LOW (<30) | MEDIUM (30–60) | HIGH (>60)

def assess_risk(
    crop:        str,
    weather:     Dict[str, Any],
    year:        int,
    yield_level: str,
) -> Dict[str, Any]:
    """
    Assess production risk from multiple independent dimensions.

    Parameters
    ----------
    crop        : str
    weather     : dict  — temperature, rainfall, humidity
    year        : int
    yield_level : str   — LOW | MEDIUM | HIGH (from Phase-1)

    Returns
    -------
    dict
        overall_risk  : str     — LOW | MEDIUM | HIGH
        risk_score    : int     — 0–100
        risk_factors  : list    — scored breakdown per risk dimension
        mitigation    : list    — top mitigation actions
    """
    temp     = float(weather.get("temperature", 26))
    rain     = float(weather.get("rainfall", 900))
    humidity = float(weather.get("humidity", 68))

    scored_risks: List[Dict] = []
    total_score = 0

    # ── Risk 1: Drought ───────────────────────────────────────────────────
    rmin = _RAIN_RANGES.get(crop, _RAIN_RANGES["_default"])[0]
    if rain < rmin * 0.5:
        score, severity = 30, "HIGH"
        desc = f"Severe rainfall deficit ({rain:.0f}mm vs {rmin:.0f}mm minimum)."
    elif rain < rmin * 0.75:
        score, severity = 20, "MEDIUM"
        desc = f"Moderate rainfall deficit. Some irrigation needed."
    else:
        score, severity = 0, "LOW"
        desc = "Rainfall is adequate — drought risk is low."
    scored_risks.append({"risk": "Drought", "severity": severity,
                          "score": score, "description": desc})
    total_score += score

    # ── Risk 2: Heat Stress ───────────────────────────────────────────────
    tmax = _TEMP_RANGES.get(crop, _TEMP_RANGES["_default"])[1]
    if temp > tmax + 5:
        score, severity = 25, "HIGH"
        desc = f"Extreme heat ({temp:.1f}°C). Severe impact on pollination and grain filling."
    elif temp > tmax:
        score, severity = 15, "MEDIUM"
        desc = f"Temperature above optimum ({temp:.1f}°C). Moderate yield reduction expected."
    else:
        score, severity = 0, "LOW"
        desc = "Temperature within safe range."
    scored_risks.append({"risk": "Heat Stress", "severity": severity,
                          "score": score, "description": desc})
    total_score += score

    # ── Risk 3: Cold Stress ───────────────────────────────────────────────
    tmin = _TEMP_RANGES.get(crop, _TEMP_RANGES["_default"])[0]
    if temp < tmin - 5:
        score, severity = 25, "HIGH"
        desc = f"Cold stress ({temp:.1f}°C). Frost/chilling injury likely."
    elif temp < tmin:
        score, severity = 12, "MEDIUM"
        desc = f"Temperature below ideal minimum. Growth may be slow."
    else:
        score, severity = 0, "LOW"
        desc = "No cold stress risk."
    scored_risks.append({"risk": "Cold Stress", "severity": severity,
                          "score": score, "description": desc})
    total_score += score

    # ── Risk 4: Disease Pressure (humidity-driven) ────────────────────────
    hmax = _HUMIDITY_RANGES.get(crop, _HUMIDITY_RANGES["_default"])[1]
    if humidity > hmax + 10:
        score, severity = 20, "HIGH"
        desc = f"Very high humidity ({humidity:.0f}%). High risk of fungal diseases."
    elif humidity > hmax:
        score, severity = 10, "MEDIUM"
        desc = f"Elevated humidity ({humidity:.0f}%). Monitor for early disease signs."
    else:
        score, severity = 0, "LOW"
        desc = "Humidity within safe range. Disease pressure is low."
    scored_risks.append({"risk": "Disease Pressure", "severity": severity,
                          "score": score, "description": desc})
    total_score += score

    # ── Risk 5: Waterlogging ──────────────────────────────────────────────
    rmax = _RAIN_RANGES.get(crop, _RAIN_RANGES["_default"])[1]
    irr  = _IRRIGATION_NEED.get(crop, "medium")
    if rain > rmax * 1.3 and irr != "high":
        score, severity = 15, "HIGH"
        desc = f"Excess rainfall ({rain:.0f}mm). Waterlogging risk is high."
    elif rain > rmax:
        score, severity = 8, "MEDIUM"
        desc = f"Rainfall above ideal maximum. Drainage management is recommended."
    else:
        score, severity = 0, "LOW"
        desc = "No waterlogging risk."
    scored_risks.append({"risk": "Waterlogging", "severity": severity,
                          "score": score, "description": desc})
    total_score += score

    # ── Risk 6: Yield outcome risk ────────────────────────────────────────
    if yield_level == "LOW":
        score, severity = 15, "HIGH"
        desc = "Model predicts low yield — economic risk to farmer is elevated."
    elif yield_level == "MEDIUM":
        score, severity = 5, "MEDIUM"
        desc = "Moderate yield expected — some market risk remains."
    else:
        score, severity = 0, "LOW"
        desc = "High yield predicted — economic risk is low."
    scored_risks.append({"risk": "Economic / Yield Risk", "severity": severity,
                          "score": score, "description": desc})
    total_score += score

    # ── Overall risk classification ───────────────────────────────────────
    total_score = min(total_score, 100)
    if total_score >= 60:
        overall = "HIGH"
    elif total_score >= 30:
        overall = "MEDIUM"
    else:
        overall = "LOW"

    # ── Mitigation actions ────────────────────────────────────────────────
    mitigation = _build_mitigation(scored_risks, crop)

    return {
        "overall_risk":  overall,
        "risk_score":    total_score,
        "risk_factors":  scored_risks,
        "mitigation":    mitigation,
    }


def _build_mitigation(risks: List[Dict], crop: str) -> List[str]:
    """Return targeted mitigation actions for the highest-scoring risks."""
    actions: List[str] = []
    action_map = {
        "Drought": (
            "Schedule supplemental irrigation at critical crop growth stages. "
            "Mulching and contour bunding will improve water retention."
        ),
        "Heat Stress": (
            "Apply foliar spray of potassium nitrate (1%) at flowering. "
            "Consider heat-tolerant variety if replanting."
        ),
        "Cold Stress": (
            "Use plastic mulch to raise soil temperature. "
            "Apply light irrigation before expected frost nights."
        ),
        "Disease Pressure": (
            "Apply preventive fungicide at early vegetative stage. "
            "Improve field drainage and increase plant spacing."
        ),
        "Waterlogging": (
            "Create raised beds and deep furrows for drainage. "
            "Avoid tillage on waterlogged soil to prevent compaction."
        ),
        "Economic / Yield Risk": (
            "Diversify with intercropping to hedge against total crop failure. "
            "Explore crop insurance schemes before the season."
        ),
    }
    for r in sorted(risks, key=lambda x: x["score"], reverse=True):
        if r["severity"] in ("HIGH", "MEDIUM") and r["risk"] in action_map:
            actions.append(action_map[r["risk"]])
    return actions[:4] if actions else [
        f"Follow standard good agricultural practices for {crop}.",
        "Monitor crop regularly and act early on any stress signs.",
    ]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — PUBLIC ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def build_intelligence(phase1_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for Phase 2.  Accepts the Phase-1 result dict (unchanged)
    and returns a fully populated intelligence block.

    Parameters
    ----------
    phase1_result : dict
        Direct output of YieldPipeline.predict() with success=True.

    Returns
    -------
    dict
        explanation     : dict  — WHY (factors, summary, driver)
        recommendations : dict  — WHAT TO DO (fertilizer, irrigation, ...)
        risk            : dict  — RISK ASSESSMENT (overall, score, factors)
    """
    crop        = phase1_result["crop"]
    season      = phase1_result["season"]
    year        = phase1_result["year"]
    yield_level = phase1_result["yield_level"]
    weather     = phase1_result["weather"]

    features = {
        "crop":   crop,
        "state":  phase1_result["area"],
        "season": season,
        "year":   year,
    }

    return {
        "explanation":     generate_explanation(features, weather),
        "recommendations": generate_recommendations(crop, weather,
                                                    yield_level, season),
        "risk":            assess_risk(crop, weather, year, yield_level),
    }
