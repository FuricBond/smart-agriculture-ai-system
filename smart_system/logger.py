"""
Professional Logger — Smart Agriculture System v2.0
======================================================
Handles all logging for the smart prediction system.

Logs predictions, inputs, timestamps, system events,
overall health grades, and cross-module analysis results
to a structured, auditable log file.

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

from __future__ import annotations

import os
import datetime
from typing import Dict, Optional

from . import config


def _ensure_log_dir() -> None:
    """Create log directory if it doesn't exist."""
    os.makedirs(config.LOG_DIR, exist_ok=True)


def log_event(event_type: str, message: str) -> None:
    """
    Log a system event to the log file.

    Parameters
    ----------
    event_type : str
        Type of event (INFO, WARNING, ERROR, PREDICTION, SESSION)
    message : str
        Event message to log.
    """
    _ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{event_type:<8}] {message}\n"

    try:
        with open(config.LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except OSError:
        pass  # Fail silently if log file is inaccessible


def log_prediction_session(session_data: Dict) -> None:
    """
    Log a complete prediction session with all inputs, outputs,
    risk analysis results, and overall farm health grade.

    Parameters
    ----------
    session_data : dict
        Dictionary containing all prediction inputs and results.
        Expected keys: 'disease', 'crop', 'yield', 'risk'.
    """
    _ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sep = "─" * 56

    lines = [
        f"\n{'═' * 60}",
        f"  PREDICTION SESSION — {timestamp}",
        f"  System Version: {config.SYSTEM_VERSION}",
        f"{'═' * 60}",
    ]

    # ── Disease Results ───────────────────────────────────────
    if 'disease' in session_data:
        d = session_data['disease']
        lines.append(f"\n  🔬 DISEASE DETECTION:")
        lines.append(f"  {sep}")
        lines.append(f"  Image Path:    {d.get('image_path', 'N/A')}")
        lines.append(f"  Detected:      {d.get('disease_name', 'N/A')}")
        lines.append(f"  Confidence:    {d.get('confidence', 0):.1f}%")
        lines.append(f"  Plant:         {d.get('plant', 'N/A')}")
        lines.append(f"  Condition:     {d.get('condition', 'N/A')}")

    # ── Crop Results ──────────────────────────────────────────
    if 'crop' in session_data:
        c = session_data['crop']
        lines.append(f"\n  🌱 CROP RECOMMENDATION:")
        lines.append(f"  {sep}")
        lines.append(
            f"  Input:         N={c.get('N',0)} "
            f"P={c.get('P',0)} K={c.get('K',0)}")
        lines.append(
            f"                 T={c.get('Temperature',0)}°C "
            f"H={c.get('Humidity',0)}% "
            f"pH={c.get('pH',0)} "
            f"Rain={c.get('Rainfall',0)}mm")
        lines.append(f"  Recommended:   {c.get('crop_name', 'N/A')}")
        lines.append(f"  Confidence:    {c.get('confidence', 0):.1f}%")

    # ── Yield Results ─────────────────────────────────────────
    if 'yield' in session_data:
        y = session_data['yield']
        lines.append(f"\n  📊 YIELD PREDICTION:")
        lines.append(f"  {sep}")
        lines.append(f"  Area:          {y.get('area', 'N/A')}")
        lines.append(f"  Crop:          {y.get('crop', 'N/A')}")
        lines.append(f"  Year:          {y.get('year', 'N/A')}")
        lines.append(f"  Predicted:     {y.get('predicted_yield', 0):,.2f}")
        lines.append(f"  Yield Level:   {y.get('yield_level', 'N/A')}")

    # ── Risk Analysis ─────────────────────────────────────────
    if 'risk' in session_data:
        r = session_data['risk']
        lines.append(f"\n  ⚠ RISK ANALYSIS:")
        lines.append(f"  {sep}")
        lines.append(f"  Disease Risk:  {r.get('disease_risk', 'N/A')}")
        lines.append(
            f"  Soil Quality:  {r.get('soil_quality', 'N/A')} "
            f"(Score: {r.get('soil_score', 0):.0f}/100)")
        lines.append(f"  Yield Level:   {r.get('yield_level', 'N/A')}")
        lines.append(
            f"  Farm Grade:    {r.get('overall_grade', 'N/A')} "
            f"({r.get('overall_score', 0):.0f}/100)")

    lines.append(f"\n{'═' * 60}\n")

    try:
        with open(config.LOG_FILE, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
    except OSError:
        pass

    log_event("SESSION", "Prediction session completed and logged")


def log_error(module: str, error: str) -> None:
    """Log an error event."""
    log_event("ERROR", f"[{module}] {error}")


def log_warning(module: str, message: str) -> None:
    """Log a warning event."""
    log_event("WARNING", f"[{module}] {message}")


def log_info(module: str, message: str) -> None:
    """Log an informational event."""
    log_event("INFO", f"[{module}] {message}")


def log_model_load(
    model_name: str,
    success: bool,
    load_time: Optional[float] = None
) -> None:
    """
    Log a model loading event.

    Parameters
    ----------
    model_name : str
        Name of the model being loaded.
    success : bool
        Whether loading succeeded.
    load_time : float, optional
        Time taken to load the model (seconds).
    """
    if success:
        time_str = f" ({load_time:.1f}s)" if load_time else ""
        log_event("MODEL", f"[{model_name}] Loaded successfully{time_str}")
    else:
        log_event("ERROR", f"[{model_name}] Failed to load")
