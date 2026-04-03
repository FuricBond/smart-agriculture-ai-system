"""
yield_predictor/weather.py
===========================
Weather data fetcher for the Yield Prediction pipeline.

Uses Open-Meteo (free, no API key required) to fetch historical / current
monthly averages for a given Indian state.

Returns
-------
dict with keys:
    temperature   : float  — average temperature (°C)
    rainfall      : float  — total rainfall (mm)
    humidity      : float  — average relative humidity (%)
"""

from __future__ import annotations

import time
import logging
from typing import Dict, Optional, Tuple

import requests

logger = logging.getLogger("agri_api")

# ── Open-Meteo geocoding override for Indian states ───────────────────────────
# Avoids geocoding ambiguity for state-level queries.  (lat, lon)
STATE_COORDINATES: Dict[str, Tuple[float, float]] = {
    "andaman and nicobar islands": (11.7401, 92.6586),
    "andhra pradesh":              (15.9129, 79.7400),
    "arunachal pradesh":           (28.2180, 94.7278),
    "assam":                       (26.2006, 92.9376),
    "bihar":                       (25.0961, 85.3131),
    "chandigarh":                  (30.7333, 76.7794),
    "chhattisgarh":                (21.2787, 81.8661),
    "dadra and nagar haveli":      (20.1809, 73.0169),
    "daman and diu":               (20.3974, 72.8328),
    "delhi":                       (28.6139, 77.2090),
    "goa":                         (15.2993, 74.1240),
    "gujarat":                     (22.2587, 71.1924),
    "haryana":                     (29.0588, 76.0856),
    "himachal pradesh":            (31.1048, 77.1734),
    "jammu and kashmir":           (33.7782, 76.5762),
    "jharkhand":                   (23.6102, 85.2799),
    "karnataka":                   (15.3173, 75.7139),
    "kerala":                      (10.8505, 76.2711),
    "laddakh":                     (34.1526, 77.5770),
    "madhya pradesh":              (22.9734, 78.6569),
    "maharashtra":                 (19.7515, 75.7139),
    "manipur":                     (24.6637, 93.9063),
    "meghalaya":                   (25.4670, 91.3662),
    "mizoram":                     (23.1645, 92.9376),
    "nagaland":                    (26.1584, 94.5624),
    "odisha":                      (20.9517, 85.0985),
    "puducherry":                  (11.9416, 79.8083),
    "punjab":                      (31.1471, 75.3412),
    "rajasthan":                   (27.0238, 74.2179),
    "sikkim":                      (27.5330, 88.5122),
    "tamil nadu":                  (11.1271, 78.6569),
    "telangana":                   (18.1124, 79.0193),
    "tripura":                     (23.9408, 91.9882),
    "uttar pradesh":               (26.8467, 80.9462),
    "uttarakhand":                 (30.0668, 79.0193),
    "west bengal":                 (22.9868, 87.8550),
}

# ── Open-Meteo API endpoint ───────────────────────────────────────────────────
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"

# Timeout for API calls (seconds)
REQUEST_TIMEOUT = 10


def get_state_coordinates(state: str) -> Optional[Tuple[float, float]]:
    """
    Return (lat, lon) for an Indian state, case-insensitive.

    Returns None if the state is not in the lookup table.
    """
    key = state.strip().lower()
    return STATE_COORDINATES.get(key)


def fetch_historical_weather(
    lat: float,
    lon: float,
    year: int,
) -> Optional[Dict[str, float]]:
    """
    Fetch annual weather averages from Open-Meteo historical archive.

    Requests daily temperature_2m_mean, precipitation_sum, and
    relative_humidity_2m_mean for the given year and aggregates to
    annual averages.

    Parameters
    ----------
    lat, lon : float
        Geographic coordinates.
    year : int
        Target year for historical data.

    Returns
    -------
    dict | None
        {'temperature': float, 'rainfall': float, 'humidity': float}
        or None on failure.
    """
    # Clamp year to available archive range (Open-Meteo: 1940 – yesterday)
    import datetime
    current_year = datetime.datetime.now().year
    data_year = min(year, current_year - 1)  # always fetch at most last year
    data_year = max(data_year, 1940)

    start_date = f"{data_year}-01-01"
    end_date   = f"{data_year}-12-31"

    params = {
        "latitude":        lat,
        "longitude":       lon,
        "start_date":      start_date,
        "end_date":        end_date,
        "daily":           "temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean",
        "timezone":        "Asia/Kolkata",
    }

    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        daily = data.get("daily", {})
        temps      = [v for v in (daily.get("temperature_2m_mean") or []) if v is not None]
        rains      = [v for v in (daily.get("precipitation_sum")   or []) if v is not None]
        humidities = [v for v in (daily.get("relative_humidity_2m_mean") or []) if v is not None]

        if not temps:
            return None

        return {
            "temperature": round(sum(temps) / len(temps), 2),
            "rainfall":    round(sum(rains), 2),          # annual total mm
            "humidity":    round(sum(humidities) / len(humidities), 2) if humidities else 70.0,
        }

    except requests.exceptions.Timeout:
        logger.warning("Open-Meteo request timed out — using fallback weather")
        return None
    except Exception as exc:
        logger.error(f"Weather fetch failed: {exc}")
        return None


# ── Climatological fallback values by state ───────────────────────────────────
# Used when the API is unavailable or the state is not found.
# Values are approximate long-term averages.

FALLBACK_WEATHER: Dict[str, Dict[str, float]] = {
    "andhra pradesh":   {"temperature": 28.5, "rainfall": 930,  "humidity": 73},
    "assam":            {"temperature": 24.0, "rainfall": 2800, "humidity": 82},
    "bihar":            {"temperature": 26.0, "rainfall": 1100, "humidity": 71},
    "gujarat":          {"temperature": 27.0, "rainfall": 700,  "humidity": 61},
    "haryana":          {"temperature": 24.5, "rainfall": 450,  "humidity": 57},
    "karnataka":        {"temperature": 26.0, "rainfall": 1000, "humidity": 72},
    "kerala":           {"temperature": 27.5, "rainfall": 3000, "humidity": 83},
    "madhya pradesh":   {"temperature": 25.0, "rainfall": 1000, "humidity": 65},
    "maharashtra":      {"temperature": 26.5, "rainfall": 1200, "humidity": 68},
    "odisha":           {"temperature": 27.0, "rainfall": 1500, "humidity": 76},
    "punjab":           {"temperature": 23.0, "rainfall": 480,  "humidity": 58},
    "rajasthan":        {"temperature": 26.5, "rainfall": 313,  "humidity": 45},
    "tamil nadu":       {"temperature": 29.0, "rainfall": 1000, "humidity": 76},
    "telangana":        {"temperature": 28.0, "rainfall": 900,  "humidity": 70},
    "uttar pradesh":    {"temperature": 25.0, "rainfall": 850,  "humidity": 66},
    "west bengal":      {"temperature": 26.5, "rainfall": 1750, "humidity": 79},
    "_default":         {"temperature": 26.0, "rainfall": 900,  "humidity": 68},
}


def get_weather(state: str, year: int) -> Dict[str, float]:
    """
    Get weather data for a given Indian state and year.

    Attempts live Open-Meteo API first; falls back to climatological
    defaults on any failure.

    Parameters
    ----------
    state : str
        Indian state name (case-insensitive).
    year : int
        Target year.

    Returns
    -------
    dict
        {'temperature': float, 'rainfall': float, 'humidity': float,
         'source': 'api' | 'fallback'}
    """
    coords = get_state_coordinates(state)

    if coords:
        lat, lon = coords
        weather = fetch_historical_weather(lat, lon, year)
        if weather:
            weather["source"] = "api"
            return weather

    # Fallback
    key = state.strip().lower()
    fallback = FALLBACK_WEATHER.get(key, FALLBACK_WEATHER["_default"])
    result = dict(fallback)
    result["source"] = "fallback"
    logger.warning(f"Using fallback weather for '{state}'")
    return result
