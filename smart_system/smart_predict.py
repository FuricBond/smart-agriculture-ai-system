"""
Smart Predict — Intelligent Agriculture Decision Engine v2.0
================================================================
Main entry point for the Smart Agriculture System.

Integrates all three AI models (Disease Detection, Crop
Recommendation, Yield Prediction) into a single unified
prediction pipeline with:
    • Model information display
    • Risk analysis engine
    • Cross-module smart advisory
    • Overall farm health grading
    • Professional report generation
    • Session logging

Usage
-----
    cd C:\\CropProject
    python -m smart_system

    or:  python smart_system/smart_predict.py

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

from __future__ import annotations

import os
import sys
import time
import datetime
from typing import Optional, Dict

# ── Setup import path ─────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from smart_system import config
from smart_system import logger as log
from smart_system.disease_engine import DiseaseEngine
from smart_system.crop_engine import CropEngine
from smart_system.yield_engine import YieldEngine
from smart_system.risk_analysis import RiskAnalyzer
from smart_system.recommendations import RecommendationEngine
from smart_system.report import ReportGenerator


# ═══════════════════════════════════════════════════════════════
# UI HELPERS
# ═══════════════════════════════════════════════════════════════

def print_banner() -> None:
    """Display the system startup banner with version info."""
    W = 62
    print()
    print("╔" + "═" * W + "╗")
    print("║" + "".center(W) + "║")
    print("║" + "🌾  SMART AGRICULTURE PREDICTION SYSTEM  🌾".center(W) + "║")
    print("║" + f"Version {config.SYSTEM_VERSION}".center(W) + "║")
    print("║" + "".center(W) + "║")
    print("║" + config.SYSTEM_NAME.center(W) + "║")
    print("║" + config.SYSTEM_SUBTITLE.center(W) + "║")
    print("║" + "".center(W) + "║")
    print("╚" + "═" * W + "╝")
    print()


def print_model_info() -> None:
    """Display detailed model information table."""
    W = 62
    print("┌" + "─" * W + "┐")
    print("│" + "  📋 MODEL INFORMATION".ljust(W) + "│")
    print("├" + "─" * W + "┤")

    for key in ['disease', 'crop', 'yield']:
        info = config.MODEL_INFO[key]
        print("│" + f"  {info['name']}".ljust(W) + "│")
        print("│" + f"    Architecture:  {info['architecture']}".ljust(W) + "│")
        print("│" + f"    Framework:     {info['framework']}".ljust(W) + "│")
        print("│" + f"    Dataset:       {info['dataset']}".ljust(W) + "│")
        print("│" + f"    Dataset Size:  {info['dataset_size']}".ljust(W) + "│")
        print("│" + f"    Classes:       {info['classes']}".ljust(W) + "│")
        print("│" + f"    Input:         {info['input']}".ljust(W) + "│")
        print("│" + f"    Output:        {info['output']}".ljust(W) + "│")
        if key != 'yield':
            print("│" + "".ljust(W) + "│")

    print("└" + "─" * W + "┘")
    print()


def print_step(step_num: int, total: int, title: str) -> None:
    """Print a formatted step header."""
    print(f"\n{'━' * 62}")
    print(f"  STEP {step_num}/{total}  │  {title}")
    print(f"{'━' * 62}\n")


def get_float_input(
    prompt: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> float:
    """
    Get a validated float input from the user with retry logic.

    Parameters
    ----------
    prompt : str
        Display prompt.
    min_val : float, optional
        Minimum acceptable value (inclusive).
    max_val : float, optional
        Maximum acceptable value (inclusive).

    Returns
    -------
    float
        Validated numeric input.
    """
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value < min_val:
                print(f"    ⚠ Value must be ≥ {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"    ⚠ Value must be ≤ {max_val}")
                continue
            return value
        except ValueError:
            print("    ❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\n  System interrupted by user.")
            sys.exit(0)


def get_string_input(prompt: str) -> str:
    """Get a non-empty string input with retry logic."""
    while True:
        try:
            value = input(prompt).strip()
            if value:
                return value
            print("    ❌ Please enter a non-empty value.")
        except KeyboardInterrupt:
            print("\n\n  System interrupted by user.")
            sys.exit(0)


def get_int_input(
    prompt: str,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None
) -> int:
    """Get a validated integer input with retry logic."""
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"    ⚠ Value must be ≥ {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"    ⚠ Value must be ≤ {max_val}")
                continue
            return value
        except ValueError:
            print("    ❌ Please enter a valid integer.")
        except KeyboardInterrupt:
            print("\n\n  System interrupted by user.")
            sys.exit(0)


# ═══════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    """
    Execute the complete Smart Agriculture prediction pipeline.

    Pipeline Steps
    ----------
    1. Display banner and model information
    2. Load all three AI models
    3. Disease Detection (leaf image → disease)
    4. Crop Recommendation (soil params → crop)
    5. Yield Prediction (area + crop + year → yield)
    6. Risk analysis, recommendations, overall health grading
    7. Generate and save report + log session
    """
    start_time = time.time()

    print_banner()
    log.log_info("SYSTEM",
                 f"Smart Agriculture System v{config.SYSTEM_VERSION} started")

    # ── Display Model Information ─────────────────────────────
    print_model_info()

    # ── Initialize & Load Engines ─────────────────────────────
    print("  🔧 Initializing AI Engines...\n")

    disease_engine = DiseaseEngine()
    crop_engine    = CropEngine()
    yield_engine   = YieldEngine()

    engines = [
        ("Disease Detection Model",   disease_engine),
        ("Crop Recommendation Model", crop_engine),
        ("Yield Prediction Model",    yield_engine),
    ]

    for name, engine in engines:
        print(f"  Loading {name}...", end=" ", flush=True)
        load_start = time.time()
        if engine.load():
            elapsed = time.time() - load_start
            print(f"✅  ({elapsed:.1f}s)")
        else:
            print("❌  (will skip)")

    loaded_count = sum(1 for _, e in engines if e._loaded)
    print(f"\n  ✅ {loaded_count}/3 engines ready.\n")

    # ══════════════════════════════════════════════════════════
    # STEP 1/4: DISEASE DETECTION
    # ══════════════════════════════════════════════════════════

    print_step(1, 4, "DISEASE DETECTION")

    disease_result: Dict = {'success': False, 'error': 'Skipped'}

    if disease_engine._loaded:
        print("  📷 Provide a leaf image for disease analysis.\n")
        image_path = get_string_input(
            "  Enter image path: ").strip('"').strip("'")

        if not os.path.isfile(image_path):
            print(f"\n  ❌ File not found: {image_path}")
            log.log_error("INPUT", f"Invalid image path: {image_path}")
            disease_result = {
                'success': False,
                'error': f'Image file not found: {image_path}'
            }
        else:
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in config.VALID_IMAGE_EXTENSIONS:
                print(f"  ⚠ Warning: '{ext}' is not a standard image format")

            print(f"\n  🔬 Analyzing: {os.path.basename(image_path)}...")
            disease_result = disease_engine.predict(image_path)

            if disease_result['success']:
                conf = disease_result['confidence']
                print(f"  ✅ Detected: {disease_result['plant']} — "
                      f"{disease_result['condition']} ({conf:.1f}%)")
                if conf < config.CONFIDENCE_MODERATE:
                    print(f"  ⚠ Low confidence — consider retaking "
                          f"the image with better lighting")
            else:
                print(f"  ❌ {disease_result.get('error', 'Failed')}")
    else:
        print("  ⚠ Disease model not available — skipping.")

    # ══════════════════════════════════════════════════════════
    # STEP 2/4: CROP RECOMMENDATION
    # ══════════════════════════════════════════════════════════

    print_step(2, 4, "CROP RECOMMENDATION")

    crop_result: Dict = {'success': False, 'error': 'Skipped'}
    soil_params: Dict = {}

    if crop_engine._loaded:
        print("  📋 Enter soil and weather parameters:\n")

        N        = get_float_input("  Nitrogen (N, kg/ha):     ", 0, 300)
        P        = get_float_input("  Phosphorus (P, kg/ha):   ", 0, 200)
        K        = get_float_input("  Potassium (K, kg/ha):    ", 0, 300)
        temp     = get_float_input("  Temperature (°C):        ", -10, 60)
        humidity = get_float_input("  Humidity (%):            ", 0, 100)
        ph       = get_float_input("  pH:                      ", 0, 14)
        rainfall = get_float_input("  Rainfall (mm):           ", 0, 5000)

        soil_params = {
            'N': N, 'P': P, 'K': K,
            'Temperature': temp, 'Humidity': humidity,
            'pH': ph, 'Rainfall': rainfall,
        }

        print(f"\n  🌱 Analyzing soil conditions...")
        crop_result = crop_engine.predict(
            N, P, K, temp, humidity, ph, rainfall)

        if crop_result['success']:
            print(f"  ✅ Recommended: {crop_result['crop_name']} "
                  f"({crop_result['confidence']:.1f}%)")
        else:
            print(f"  ❌ {crop_result.get('error', 'Failed')}")
    else:
        print("  ⚠ Crop model not available — skipping.")

    # ══════════════════════════════════════════════════════════
    # STEP 3/4: YIELD PREDICTION
    # ══════════════════════════════════════════════════════════

    print_step(3, 4, "YIELD PREDICTION")

    yield_result: Dict = {'success': False, 'error': 'Skipped'}

    if yield_engine._loaded:
        print("  📊 Enter yield prediction parameters:\n")

        if yield_engine.known_areas:
            print(f"  Available regions: {len(yield_engine.known_areas)}")
        if yield_engine.known_crops:
            print(f"  Available crops:   {len(yield_engine.known_crops)}")
        print()

        area = get_string_input("  Area (e.g., India):   ")
        crop = get_string_input("  Crop (e.g., Rice):    ")
        year = get_int_input("  Year (e.g., 2024):    ", 1900, 2100)

        print(f"\n  📊 Predicting yield for {crop} in {area} ({year})...")
        yield_result = yield_engine.predict(area, crop, year)

        if yield_result['success']:
            print(f"  ✅ Predicted Yield: "
                  f"{yield_result['predicted_yield']:,.2f}")
        else:
            print(f"  ❌ {yield_result.get('error', 'Failed')}")
            if yield_result.get('suggestions'):
                print("  💡 Did you mean?")
                for s in yield_result['suggestions'][:5]:
                    print(f"     → {s}")
    else:
        print("  ⚠ Yield model not available — skipping.")

    # ══════════════════════════════════════════════════════════
    # STEP 4/4: ANALYSIS & REPORT GENERATION
    # ══════════════════════════════════════════════════════════

    print_step(4, 4, "ANALYSIS & REPORT GENERATION")

    risk_analyzer = RiskAnalyzer()
    recommender   = RecommendationEngine()

    # ── Risk Analysis ─────────────────────────────────────────
    print("  🧠 Running risk analysis...", end=" ", flush=True)

    # Disease Risk
    if disease_result.get('success'):
        disease_risk = risk_analyzer.assess_disease_risk(
            disease_result['disease_name'],
            disease_result['confidence'])
    else:
        disease_risk = {
            'risk_level': 'MODERATE', 'risk_score': 50.0,
            'severity': 0,
            'description': 'Disease analysis not available'}

    # Soil Quality
    if soil_params:
        soil_quality = risk_analyzer.calculate_soil_quality(
            soil_params['N'], soil_params['P'], soil_params['K'],
            soil_params['pH'], soil_params['Temperature'],
            soil_params['Humidity'], soil_params['Rainfall'])
    else:
        soil_quality = {
            'score': 0, 'level': 'FAIR',
            'breakdown': {}, 'issues': ['Soil data not provided'],
            'npk_ratio': {}}

    # Yield Classification
    if yield_result.get('success'):
        yield_classification = risk_analyzer.classify_yield(
            yield_result['predicted_yield'])
    else:
        yield_classification = {
            'level': 'MEDIUM',
            'description': 'Yield prediction not available'}

    # Overall Farm Health
    overall_health = risk_analyzer.compute_overall_health(
        soil_quality, disease_risk, yield_classification)

    print("✅")

    # ── Recommendations ───────────────────────────────────────
    print("  💡 Generating smart recommendations...", end=" ", flush=True)

    # Disease treatment
    if disease_result.get('success'):
        disease_treatments = recommender.get_disease_treatment(
            disease_result['disease_name'],
            disease_result['plant'],
            disease_result['condition'])
    else:
        disease_treatments = [
            "Provide a leaf image to receive disease-specific treatment",
            "Regular plant health monitoring is always recommended"]

    # Crop advice
    if crop_result.get('success') and soil_params:
        crop_advice = recommender.get_crop_advice(
            crop_result['crop_name'],
            soil_params['N'], soil_params['P'], soil_params['K'],
            soil_params['Temperature'], soil_params['Humidity'],
            soil_params['pH'], soil_params['Rainfall'])
    else:
        crop_advice = [
            "Enter soil parameters for crop-specific recommendations",
            "Conduct professional soil testing for best results"]

    # Yield advice
    if yield_result.get('success'):
        yield_advice = recommender.get_yield_advice(
            yield_classification['level'],
            yield_result['predicted_yield'],
            yield_result.get('crop', 'the crop'))
    else:
        yield_advice = [
            "Enter area, crop, and year for yield improvement advice",
            "Historical data improves prediction reliability"]

    # Cross-module combined advisory (NEW in v2.0)
    combined_advisory = recommender.get_combined_advisory(
        disease_result, crop_result, yield_result,
        soil_quality, disease_risk)

    print("✅")

    # ── Generate Report ───────────────────────────────────────
    print("  📄 Generating Smart Farm Report...", end=" ", flush=True)

    report_gen = ReportGenerator()

    report = report_gen.generate(
        disease_result=disease_result,
        crop_result=crop_result,
        yield_result=yield_result,
        soil_quality=soil_quality,
        disease_risk=disease_risk,
        yield_classification=yield_classification,
        disease_treatments=disease_treatments,
        crop_advice=crop_advice,
        yield_advice=yield_advice,
        overall_health=overall_health,
        combined_advisory=combined_advisory,
    )

    print("✅")

    # Display report
    print(report)

    # Save report
    report_path = report_gen.save_to_file(report)
    print(f"  📁 Report saved:   {report_path}")

    # ── Log Session ───────────────────────────────────────────
    session_data: Dict = {}

    if disease_result.get('success'):
        session_data['disease'] = disease_result

    if crop_result.get('success'):
        session_data['crop'] = {
            **crop_result.get('input_data', {}),
            'crop_name':  crop_result['crop_name'],
            'confidence': crop_result['confidence'],
        }

    if yield_result.get('success'):
        session_data['yield'] = yield_result

    session_data['risk'] = {
        'disease_risk': disease_risk.get('risk_level', 'N/A'),
        'soil_quality': soil_quality.get('level', 'N/A'),
        'soil_score':   soil_quality.get('score', 0),
        'yield_level':  yield_classification.get('level', 'N/A'),
        'overall_grade': overall_health.get('overall_grade', 'N/A'),
        'overall_score': overall_health.get('overall_score', 0),
    }

    log.log_prediction_session(session_data)
    print(f"  📝 Session logged: {config.LOG_FILE}")

    # ── Summary Footer ────────────────────────────────────────
    elapsed = time.time() - start_time
    print(f"\n{'━' * 62}")
    print(f"  ✅ SMART FARM ANALYSIS COMPLETE")
    print(f"  ⏱  Total time: {elapsed:.1f} seconds")
    print(f"  📊 Farm Grade: {overall_health.get('overall_grade', '?')} "
          f"({overall_health.get('overall_score', 0):.0f}/100)")
    print(f"{'━' * 62}\n")


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  System interrupted by user.")
        log.log_info("SYSTEM", "System interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n  ❌ System Error: {e}")
        log.log_error("SYSTEM", f"Unhandled exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
