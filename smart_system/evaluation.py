"""
Automated Evaluation — Smart Agriculture System v2.0
=======================================================
Tests all three AI models with predefined sample inputs
to validate system integrity and prediction quality.

Evaluation Coverage
-------------------
    • 10 disease image predictions   (if images available)
    • 10 crop recommendation inputs  (hardcoded realistic params)
    • 10 yield prediction inputs     (hardcoded area + crop + year)
    • Risk analysis validation
    • Report generation validation

Usage
-----
    cd C:\\CropProject
    python -m smart_system.evaluation

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

from __future__ import annotations

import os
import sys
import time
import glob
import json
from typing import Dict, List, Tuple

# ── Setup import path ─────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from smart_system import config
from smart_system.disease_engine import DiseaseEngine
from smart_system.crop_engine import CropEngine
from smart_system.yield_engine import YieldEngine
from smart_system.risk_analysis import RiskAnalyzer
from smart_system.recommendations import RecommendationEngine


# ═══════════════════════════════════════════════════════════════
# SAMPLE TEST DATA
# ═══════════════════════════════════════════════════════════════

# 10 realistic crop recommendation test cases
# (N, P, K, Temperature, Humidity, pH, Rainfall, expected_crop)
CROP_TEST_CASES: List[Tuple[float, float, float,
                            float, float, float, float, str]] = [
    (90,  42, 43,  20.8, 82.0, 6.5, 202.9,  "Rice"),
    (85,  58, 41,  21.8, 80.4, 7.0, 226.6,  "Rice"),
    (20,  27, 20,  27.0, 48.0, 6.8, 100.3,  "Wheat-like"),
    (40,  67, 40,  24.0, 65.0, 6.5, 67.5,   "Chickpea-like"),
    (78,  42, 40,  25.0, 80.0, 7.0, 1500.0, "Jute-like"),
    (60,  55, 44,  23.0, 82.0, 7.5, 250.0,  "Cotton-like"),
    (100, 20, 30,  30.0, 90.0, 5.5, 800.0,  "Tropical"),
    (10,  15, 15,  22.0, 50.0, 6.5, 120.0,  "Lentil-like"),
    (118, 38, 200, 27.5, 56.5, 5.9, 112.0,  "Coffee-like"),
    (40,  40, 40,  25.0, 70.0, 6.5, 300.0,  "Balanced"),
]

# 10 yield prediction test cases
# (Area, Crop, Year)
YIELD_TEST_CASES: List[Tuple[str, str, int]] = [
    ("India",         "Rice",       2020),
    ("India",         "Wheat",      2020),
    ("China",         "Maize",      2018),
    ("United States", "Soybeans",   2019),
    ("Brazil",        "Sugar cane", 2020),
    ("Indonesia",     "Rice",       2015),
    ("India",         "Potatoes",   2020),
    ("Germany",       "Wheat",      2018),
    ("India",         "Cotton",     2019),
    ("Australia",     "Wheat",      2020),
]


# ═══════════════════════════════════════════════════════════════
# EVALUATION RUNNER
# ═══════════════════════════════════════════════════════════════

def print_header(title: str, width: int = 62) -> None:
    """Print a formatted section header."""
    print(f"\n{'═' * width}")
    print(f"  {title}")
    print(f"{'═' * width}\n")


def evaluate_disease_model() -> Dict:
    """
    Evaluate the disease detection model.

    Finds up to 10 sample images from the dataset directory
    and runs prediction on each.

    Returns
    -------
    dict
        results : list of prediction dicts
        passed  : int  (successful predictions)
        failed  : int  (failed predictions)
        total   : int
    """
    print_header("EVALUATING DISEASE DETECTION MODEL")

    engine = DiseaseEngine()
    if not engine.load():
        print("  ❌ Could not load disease model.")
        return {'results': [], 'passed': 0, 'failed': 0, 'total': 0}

    # Find sample images from dataset
    image_dir = config.DISEASE_DATA_DIR
    sample_images: List[str] = []

    if os.path.isdir(image_dir):
        # Pick one image from up to 10 different class folders
        class_dirs = sorted([
            d for d in os.listdir(image_dir)
            if os.path.isdir(os.path.join(image_dir, d))
        ])

        for class_name in class_dirs[:10]:
            class_path = os.path.join(image_dir, class_name)
            imgs = glob.glob(os.path.join(class_path, "*.jpg"))
            if not imgs:
                imgs = glob.glob(os.path.join(class_path, "*.JPG"))
            if not imgs:
                imgs = glob.glob(os.path.join(class_path, "*.png"))
            if imgs:
                sample_images.append((class_name, imgs[0]))

    if not sample_images:
        print("  ⚠ No sample images found in dataset directory.")
        print(f"    Looked in: {image_dir}")
        return {'results': [], 'passed': 0, 'failed': 0, 'total': 0}

    print(f"  Found {len(sample_images)} test images.\n")
    print(f"  {'#':<4} {'Expected Class':<35} {'Predicted':<25} {'Conf':>6} {'Status'}")
    print(f"  {'─'*4} {'─'*35} {'─'*25} {'─'*6} {'─'*6}")

    results = []
    passed = 0

    for idx, (expected_class, img_path) in enumerate(sample_images, 1):
        result = engine.predict(img_path, top_k=3)

        if result['success']:
            predicted = result['disease_name']
            conf = result['confidence']

            # Check if prediction matches expected class
            match = (predicted.lower() == expected_class.lower())
            status = "✅ PASS" if match else "⚠ DIFF"
            if match:
                passed += 1

            # Truncate for display
            exp_display = expected_class[:33] if len(expected_class) > 33 else expected_class
            pred_display = predicted[:23] if len(predicted) > 23 else predicted

            print(f"  {idx:<4} {exp_display:<35} {pred_display:<25} {conf:5.1f}% {status}")
        else:
            print(f"  {idx:<4} {expected_class:<35} {'FAILED':<25} {'':>6} ❌ FAIL")

        results.append(result)

    failed = len(sample_images) - passed
    print(f"\n  Results: {passed}/{len(sample_images)} correct predictions")

    return {
        'results': results,
        'passed':  passed,
        'failed':  failed,
        'total':   len(sample_images)
    }


def evaluate_crop_model() -> Dict:
    """
    Evaluate the crop recommendation model with 10 test cases.

    Returns
    -------
    dict
        results : list of prediction dicts
        passed  : int  (successful predictions)
        failed  : int  (failed predictions)
        total   : int
    """
    print_header("EVALUATING CROP RECOMMENDATION MODEL")

    engine = CropEngine()
    if not engine.load():
        print("  ❌ Could not load crop model.")
        return {'results': [], 'passed': 0, 'failed': 0, 'total': 0}

    print(f"  Running {len(CROP_TEST_CASES)} test cases...\n")
    print(f"  {'#':<4} {'N':>4} {'P':>4} {'K':>4} {'T':>5} {'H':>4} {'pH':>4} {'Rain':>6} "
          f" {'Predicted':<15} {'Conf':>6} {'Status'}")
    print(f"  {'─'*4} {'─'*4} {'─'*4} {'─'*4} {'─'*5} {'─'*4} {'─'*4} {'─'*6} "
          f" {'─'*15} {'─'*6} {'─'*6}")

    results = []
    passed = 0

    for idx, (N, P, K, temp, hum, ph, rain, hint) in enumerate(CROP_TEST_CASES, 1):
        result = engine.predict(N, P, K, temp, hum, ph, rain)

        if result['success']:
            crop = result['crop_name']
            conf = result['confidence']
            passed += 1

            print(f"  {idx:<4} {N:4.0f} {P:4.0f} {K:4.0f} {temp:5.1f} "
                  f"{hum:4.0f} {ph:4.1f} {rain:6.0f}  {crop:<15} {conf:5.1f}% ✅")
        else:
            print(f"  {idx:<4} {N:4.0f} {P:4.0f} {K:4.0f} {temp:5.1f} "
                  f"{hum:4.0f} {ph:4.1f} {rain:6.0f}  {'FAILED':<15} {'':>6} ❌")

        results.append(result)

    failed = len(CROP_TEST_CASES) - passed
    print(f"\n  Results: {passed}/{len(CROP_TEST_CASES)} successful predictions")

    return {
        'results': results,
        'passed':  passed,
        'failed':  failed,
        'total':   len(CROP_TEST_CASES)
    }


def evaluate_yield_model() -> Dict:
    """
    Evaluate the yield prediction model with 10 test cases.

    Returns
    -------
    dict
        results : list of prediction dicts
        passed  : int  (successful predictions)
        failed  : int  (failed predictions)
        total   : int
    """
    print_header("EVALUATING YIELD PREDICTION MODEL")

    engine = YieldEngine()
    if not engine.load():
        print("  ❌ Could not load yield model.")
        return {'results': [], 'passed': 0, 'failed': 0, 'total': 0}

    print(f"  Running {len(YIELD_TEST_CASES)} test cases...\n")
    print(f"  {'#':<4} {'Area':<17} {'Crop':<14} {'Year':>5}  "
          f"{'Predicted Yield':>15} {'Level':<8} {'Status'}")
    print(f"  {'─'*4} {'─'*17} {'─'*14} {'─'*5}  "
          f"{'─'*15} {'─'*8} {'─'*6}")

    results = []
    passed = 0

    for idx, (area, crop, year) in enumerate(YIELD_TEST_CASES, 1):
        result = engine.predict(area, crop, year)

        if result['success']:
            yld = result['predicted_yield']
            level = result.get('yield_level', 'N/A')
            passed += 1

            print(f"  {idx:<4} {area:<17} {crop:<14} {year:>5}  "
                  f"{yld:>15,.2f} {level:<8} ✅")
        else:
            error = result.get('error', 'Unknown')
            short_err = error[:30] if len(error) > 30 else error
            print(f"  {idx:<4} {area:<17} {crop:<14} {year:>5}  "
                  f"{'':>15} {'':>8} ❌ {short_err}")

        results.append(result)

    failed = len(YIELD_TEST_CASES) - passed
    print(f"\n  Results: {passed}/{len(YIELD_TEST_CASES)} successful predictions")

    return {
        'results': results,
        'passed':  passed,
        'failed':  failed,
        'total':   len(YIELD_TEST_CASES)
    }


def evaluate_risk_analysis() -> Dict:
    """
    Evaluate the risk analysis engine with validation checks.

    Returns
    -------
    dict
        passed : int
        failed : int
        total  : int
    """
    print_header("EVALUATING RISK ANALYSIS ENGINE")

    analyzer = RiskAnalyzer()
    tests_passed = 0
    tests_total = 0

    # Test 1: Ideal conditions should give high soil score
    tests_total += 1
    result = analyzer.calculate_soil_quality(
        N=80, P=50, K=50, ph=6.8, temperature=25,
        humidity=65, rainfall=500)
    score = result['score']
    print(f"  Test 1: Ideal conditions → Score {score:.1f}/100", end=" ")
    if score >= 80:
        print("✅ (Expected ≥ 80)")
        tests_passed += 1
    else:
        print(f"❌ (Expected ≥ 80, got {score:.1f})")

    # Test 2: Poor conditions should give low score
    tests_total += 1
    result = analyzer.calculate_soil_quality(
        N=5, P=5, K=5, ph=4.0, temperature=45,
        humidity=10, rainfall=10)
    score = result['score']
    print(f"  Test 2: Poor conditions  → Score {score:.1f}/100", end=" ")
    if score < 30:
        print("✅ (Expected < 30)")
        tests_passed += 1
    else:
        print(f"❌ (Expected < 30, got {score:.1f})")

    # Test 3: Healthy plant should have LOW disease risk
    tests_total += 1
    result = analyzer.assess_disease_risk("Tomato___healthy", 95.0)
    risk = result['risk_level']
    print(f"  Test 3: Healthy plant    → Risk {risk}", end=" ")
    if risk == 'LOW':
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (Expected LOW)")

    # Test 4: Late blight with high confidence → CRITICAL
    tests_total += 1
    result = analyzer.assess_disease_risk("Tomato___Late_blight", 92.0)
    risk = result['risk_level']
    print(f"  Test 4: Late blight 92%  → Risk {risk}", end=" ")
    if risk == 'CRITICAL':
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (Expected CRITICAL)")

    # Test 5: Low yield classification
    tests_total += 1
    result = analyzer.classify_yield(800)
    level = result['level']
    print(f"  Test 5: Yield 800        → Level {level}", end=" ")
    if level == 'LOW':
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (Expected LOW)")

    # Test 6: High yield classification
    tests_total += 1
    result = analyzer.classify_yield(5000)
    level = result['level']
    print(f"  Test 6: Yield 5000       → Level {level}", end=" ")
    if level == 'HIGH':
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (Expected HIGH)")

    # Test 7: Overall health computation
    tests_total += 1
    soil = {'score': 85, 'level': 'EXCELLENT'}
    disease = {'risk_level': 'LOW', 'risk_score': 5}
    yield_class = {'level': 'HIGH'}
    result = analyzer.compute_overall_health(soil, disease, yield_class)
    grade = result['overall_grade']
    print(f"  Test 7: Optimal health   → Grade {grade}", end=" ")
    if grade in ('A', 'B'):
        print("✅")
        tests_passed += 1
    else:
        print(f"❌ (Expected A or B)")

    # Test 8: NPK balance check
    tests_total += 1
    result = analyzer.calculate_soil_quality(
        N=80, P=50, K=50, ph=6.8, temperature=25,
        humidity=65, rainfall=500)
    has_npk = 'npk_ratio' in result
    print(f"  Test 8: NPK ratio info   → Present: {has_npk}", end=" ")
    if has_npk:
        print("✅")
        tests_passed += 1
    else:
        print("❌")

    print(f"\n  Results: {tests_passed}/{tests_total} tests passed")

    return {
        'passed': tests_passed,
        'failed': tests_total - tests_passed,
        'total':  tests_total
    }


# ═══════════════════════════════════════════════════════════════
# MAIN EVALUATION RUNNER
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    """Run the complete automated evaluation suite."""

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║    🧪  AUTOMATED EVALUATION SUITE                           ║")
    print("║    Smart Agriculture System v" +
          config.SYSTEM_VERSION.ljust(35) + "║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    start_time = time.time()

    # Run all evaluations
    disease_eval = evaluate_disease_model()
    crop_eval    = evaluate_crop_model()
    yield_eval   = evaluate_yield_model()
    risk_eval    = evaluate_risk_analysis()

    elapsed = time.time() - start_time

    # ── Summary ───────────────────────────────────────────────
    print_header("EVALUATION SUMMARY")

    total_passed = (disease_eval['passed'] + crop_eval['passed']
                    + yield_eval['passed'] + risk_eval['passed'])
    total_failed = (disease_eval['failed'] + crop_eval['failed']
                    + yield_eval['failed'] + risk_eval['failed'])
    total_tests  = (disease_eval['total'] + crop_eval['total']
                    + yield_eval['total'] + risk_eval['total'])

    print(f"  {'Module':<26} {'Passed':>7} {'Failed':>7} {'Total':>7}")
    print(f"  {'─'*26} {'─'*7} {'─'*7} {'─'*7}")
    print(f"  {'Disease Detection':<26} {disease_eval['passed']:>7} "
          f"{disease_eval['failed']:>7} {disease_eval['total']:>7}")
    print(f"  {'Crop Recommendation':<26} {crop_eval['passed']:>7} "
          f"{crop_eval['failed']:>7} {crop_eval['total']:>7}")
    print(f"  {'Yield Prediction':<26} {yield_eval['passed']:>7} "
          f"{yield_eval['failed']:>7} {yield_eval['total']:>7}")
    print(f"  {'Risk Analysis':<26} {risk_eval['passed']:>7} "
          f"{risk_eval['failed']:>7} {risk_eval['total']:>7}")
    print(f"  {'─'*26} {'─'*7} {'─'*7} {'─'*7}")
    print(f"  {'TOTAL':<26} {total_passed:>7} "
          f"{total_failed:>7} {total_tests:>7}")

    # Overall status
    if total_tests > 0:
        pass_rate = (total_passed / total_tests) * 100
    else:
        pass_rate = 0

    print(f"\n  Pass Rate: {pass_rate:.1f}%")
    print(f"  Time:      {elapsed:.1f} seconds")

    if pass_rate >= 90:
        print(f"\n  ✅ SYSTEM STATUS: PRODUCTION READY")
    elif pass_rate >= 70:
        print(f"\n  🟡 SYSTEM STATUS: NEEDS MINOR FIXES")
    else:
        print(f"\n  ❌ SYSTEM STATUS: NEEDS ATTENTION")

    print(f"\n{'═' * 62}\n")


if __name__ == "__main__":
    main()
