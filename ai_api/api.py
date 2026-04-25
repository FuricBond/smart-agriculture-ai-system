"""
Smart Agriculture AI API — Production Grade
=============================================
Author  : Smart Agriculture AI Team
Version : 3.0.0

Features
--------
  • Safe model loading with per-model fallback
  • Startup diagnostics banner
  • Structured input validation (all endpoints)
  • Comprehensive try/except error handling
  • File-based rotating API logger
  • Singleton model globals (load once, reuse always)
  • /health endpoint
  • CORS enabled for all origins
"""

import warnings
warnings.filterwarnings("ignore")

import os
import sys
import shutil
import logging
import platform
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ── Add project root to sys.path ──────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
import uvicorn

from smart_system.recommendations import RecommendationEngine
from smart_system.farm_ai_assistant import generate_farming_response

# ══════════════════════════════════════════════════════════════
# PART 6 — LOGGING SYSTEM
# ══════════════════════════════════════════════════════════════

LOG_DIR  = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "api_log.txt")
os.makedirs(LOG_DIR, exist_ok=True)

# Create a dual logger — writes to file AND console
logger = logging.getLogger("agri_api")
logger.setLevel(logging.DEBUG)

# File handler
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

fmt = logging.Formatter("[%(levelname)s] %(asctime)s — %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
fh.setFormatter(fmt)
ch.setFormatter(fmt)

if not logger.handlers:
    logger.addHandler(fh)
    logger.addHandler(ch)


def log_info(msg: str):
    logger.info(msg)

def log_error(msg: str):
    logger.error(msg)

def log_request(endpoint: str, payload: dict = None):
    logger.info(f"REQUEST  {endpoint} — {payload or ''}")

def log_prediction(model: str, result: str):
    logger.info(f"PREDICT  [{model}] → {result}")


# ══════════════════════════════════════════════════════════════
# PART 7 — SINGLETON MODEL GLOBALS (load once, reuse always)
# ══════════════════════════════════════════════════════════════

disease_engine = None
crop_engine    = None
yield_engine   = None
plant_doctor_pipeline = None
yield_pipeline = None          # Phase-1 Yield Prediction Pipeline
ensemble_engine = None         # Ensemble: EfficientNet-B0 + ResNet-50 + EfficientNet-B1

_disease_loaded   = False
_crop_loaded      = False
_yield_loaded     = False
_ensemble_loaded  = False      # True when secondary ensemble models are ready
yield_trends_df = None


# ══════════════════════════════════════════════════════════════
# FASTAPI APP
# ══════════════════════════════════════════════════════════════

app = FastAPI(
    title="Smart Agriculture AI API",
    version="3.0.0",
    description="Production-grade AI inference API for plant disease, crop recommendation, and yield prediction."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Part 3.5: Serve Heatmap Outputs to Frontend ──────────────
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "tmp", "plant_doctor_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

def cleanup_outputs(max_files: int = 20):
    """Keep only the latest N images in the output directory."""
    try:
        files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.endswith('.jpg')]
        if len(files) <= max_files:
            return
        # Sort by modification time
        files.sort(key=os.path.getmtime)
        # Delete oldest
        for f in files[:-max_files]:
            try:
                os.remove(f)
            except Exception:
                pass
        log_info(f"Cleaned up {len(files) - max_files} old heatmap images.")
    except Exception as e:
        log_error(f"Cleanup failed: {e}")


# ══════════════════════════════════════════════════════════════
# PART 2 + 3 — SAFE STARTUP MODEL LOADING + DIAGNOSTICS BANNER
# ══════════════════════════════════════════════════════════════

@app.on_event("startup")
def startup():
    global disease_engine, crop_engine, yield_engine, yield_pipeline
    global _disease_loaded, _crop_loaded, _yield_loaded
    global ensemble_engine, _ensemble_loaded

    # ── Version probing ───────────────────────────────────────
    py_ver    = platform.python_version()
    np_ver    = _safe_import_version("numpy")
    torch_ver = _safe_import_version("torch")

    # ── Fix Joblib unpickling for models saved with 'config' ──
    import smart_system.config
    sys.modules['config'] = smart_system.config

    # ── Load models safely ────────────────────────────────────
    disease_status = _load_disease()
    crop_status    = _load_crop()
    yield_status   = _load_yield()

    # ── Load Yield Trends ─────────────────────────────────────
    global yield_trends_df
    try:
        import pandas as pd
        from smart_system.config import YIELD_MODEL_DIR
        trends_path = os.path.join(YIELD_MODEL_DIR, "yield_trends.csv")
        if os.path.exists(trends_path):
            yield_trends_df = pd.read_csv(trends_path)
            log_info(f"Loaded Yield Trends: {len(yield_trends_df)} rows")
    except Exception as e:
        log_error(f"Failed to load Yield Trends: {e}")

    # ── Initialize Ensemble Engine ───────────────────────
    # Load ResNet-50 + EfficientNet-B1 as secondary ensemble models.
    # If this fails, the system falls back to EfficientNet-B0 only.
    if disease_status and disease_engine is not None:
        try:
            from smart_system.ensemble_engine import EnsembleEngine
            ensemble_engine = EnsembleEngine(
                disease_engine=disease_engine,
                num_classes=len(disease_engine.class_names),
                enable_early_exit=True,
            )
            ok = ensemble_engine.load_secondary_models()
            if ok:
                _ensemble_loaded = True
                log_info("Ensemble Engine (ResNet-50 + EfficientNet-B1) loaded [OK]")
            else:
                log_error("Ensemble secondary model load returned False ⚠️")
                ensemble_engine = None
        except Exception as e:
            log_error(f"Ensemble Engine init failed: {e}")
            ensemble_engine = None

    # ── Initialize Plant Doctor Pipeline (now with Ensemble) ───
    global plant_doctor_pipeline
    if disease_status and disease_engine is not None:
        try:
            from smart_system.plant_doctor import PlantDoctorPipeline
            plant_doctor_pipeline = PlantDoctorPipeline(
                disease_engine=disease_engine,
                output_dir=os.path.join(PROJECT_ROOT, "tmp", "plant_doctor_output"),
                enable_gradcam=True,
                enable_similarity=True,
                unknown_threshold=60.0,
                ensemble_engine=ensemble_engine,   # Pass ensemble (None if not loaded)
            )
            log_info("Plant Doctor Pipeline initialized [OK]")
        except Exception as e:
            log_error(f"Plant Doctor Pipeline init failed: {e}")

    # ── Initialize Phase-1 Yield Prediction Pipeline ──────────
    if yield_status and yield_engine is not None and yield_engine._use_encoders:
        try:
            from smart_system.yield_predictor.pipeline import YieldPipeline
            yield_pipeline = YieldPipeline()
            yield_pipeline.load(
                model         = yield_engine.model,
                area_encoder  = yield_engine.area_encoder,
                crop_encoder  = yield_engine.crop_encoder,
            )
            log_info("Yield Prediction Pipeline (Phase-1) initialized [OK]")
        except Exception as e:
            log_error(f"Yield Pipeline init failed: {e}")

    disease_icon  = "[OK]" if disease_status       else "[MISSING]"
    crop_icon     = "[OK]" if crop_status           else "[MISSING]"
    yield_icon    = "[OK]" if yield_status          else "[MISSING]"
    doctor_icon   = "[OK]" if plant_doctor_pipeline else "[MISSING]"
    ensemble_icon = "[OK]" if _ensemble_loaded       else "[NOT TRAINED]"

    banner = f"""
================================
  SMART AGRICULTURE AI API
================================
  Python  : {py_ver}
  NumPy   : {np_ver}
  Torch   : {torch_ver}
  Port    : 8000
  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
--------------------------------
  Models Status:
    Disease Model    {disease_icon}
    Crop Model       {crop_icon}
    Yield Model      {yield_icon}
    Plant Doctor AI  {doctor_icon}
    Ensemble Models  {ensemble_icon}
================================
"""
    print(banner)
    log_info(f"Server started | disease={disease_status} | crop={crop_status} | yield={yield_status} | plant_doctor={'OK' if plant_doctor_pipeline else 'FAIL'}")


def _safe_import_version(pkg: str) -> str:
    try:
        import importlib.metadata
        return importlib.metadata.version(pkg)
    except Exception:
        return "unknown"


def _load_disease() -> bool:
    global disease_engine, _disease_loaded
    try:
        from smart_system.disease_engine import DiseaseEngine
        engine = DiseaseEngine()
        ok = engine.load()
        if ok:
            disease_engine = engine
            _disease_loaded = True
            log_info("Disease Model Loaded [OK]")
        else:
            log_error("Disease Model load() returned False ⚠️")
        return ok
    except Exception as e:
        log_error(f"Disease Model load exception: {e}")
        return False


def _load_crop() -> bool:
    global crop_engine, _crop_loaded
    try:
        from smart_system.crop_engine import CropEngine
        engine = CropEngine()
        ok = engine.load()
        if ok:
            crop_engine = engine
            _crop_loaded = True
            log_info("Crop Model Loaded [OK]")
        else:
            log_error("Crop Model load() returned False ⚠️")
        return ok
    except Exception as e:
        log_error(f"Crop Model load exception: {e}")
        return False


def _load_yield() -> bool:
    global yield_engine, _yield_loaded
    try:
        from smart_system.yield_engine import YieldEngine
        engine = YieldEngine()
        ok = engine.load()
        if ok:
            yield_engine = engine
            _yield_loaded = True
            log_info("Yield Model Loaded [OK]")
        else:
            log_error("Yield Model load() returned False ⚠️")
        return ok
    except Exception as e:
        log_error(f"Yield Model load exception: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# PART 4 — INPUT VALIDATION MODELS
# ══════════════════════════════════════════════════════════════

VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp", ".gif"}

class CropRequest(BaseModel):
    Nitrogen:    float
    Phosphorus:  float
    Potassium:   float
    Temperature: float
    Humidity:    float
    pH:          float
    Rainfall:    float

    @validator("Nitrogen")
    def val_nitrogen(cls, v):
        if not (0 <= v <= 300):
            raise ValueError("Nitrogen must be 0–300 kg/ha")
        return v

    @validator("Phosphorus")
    def val_phosphorus(cls, v):
        if not (0 <= v <= 200):
            raise ValueError("Phosphorus must be 0–200 kg/ha")
        return v

    @validator("Potassium")
    def val_potassium(cls, v):
        if not (0 <= v <= 300):
            raise ValueError("Potassium must be 0–300 kg/ha")
        return v

    @validator("Temperature")
    def val_temperature(cls, v):
        if not (-10 <= v <= 60):
            raise ValueError("Temperature must be -10–60 °C")
        return v

    @validator("Humidity")
    def val_humidity(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Humidity must be 0–100 %")
        return v

    @validator("pH")
    def val_ph(cls, v):
        if not (0 <= v <= 14):
            raise ValueError("pH must be 0–14")
        return v

    @validator("Rainfall")
    def val_rainfall(cls, v):
        if not (0 <= v <= 5000):
            raise ValueError("Rainfall must be 0–5000 mm")
        return v


class YieldRequest(BaseModel):
    Area: str
    Crop: str
    Year: int
    Season: str = None

    @validator("Area")
    def val_area(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Area cannot be empty")
        return v

    @validator("Crop")
    def val_crop(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Crop cannot be empty")
        return v

    @validator("Year")
    def val_year(cls, v):
        if not (1990 <= v <= 2035):
            raise ValueError("Year must be between 1990 and 2035")
        return v


class YieldTrendRequest(BaseModel):
    Area: str
    Crop: str

class FarmAssistantRequest(BaseModel):
    question: str


# ══════════════════════════════════════════════════════════════
# PART 5 — STRUCTURED ERROR RESPONSE HELPER
# ══════════════════════════════════════════════════════════════

def error_response(message: str, status_code: int = 500):
    log_error(message)
    raise HTTPException(
        status_code=status_code,
        detail={"status": "error", "message": message}
    )


# ══════════════════════════════════════════════════════════════
# PART 8 — HEALTH CHECK ENDPOINT
# ══════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    return {
        "status":          "running",
        "disease_model":   _disease_loaded,
        "ensemble_models": _ensemble_loaded,
        "crop_model":      _crop_loaded,
        "yield_model":     _yield_loaded,
        "timestamp":       datetime.now().isoformat()
    }


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.post("/predict-disease")
async def predict_disease(file: UploadFile = File(...)):
    log_request("/predict-disease", {"filename": file.filename})
    try:
        if not _disease_loaded or disease_engine is None:
            error_response("Disease model is not loaded", 503)

        # ── PART 4: Validate image extension ──────────────────
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in VALID_IMAGE_EXTENSIONS:
            log_error(f"Invalid file type: {ext}")
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": "Invalid image file. Supported: jpg, jpeg, png, bmp, tiff, webp"}
            )

        # Save temp file
        temp_dir  = os.path.join(PROJECT_ROOT, "tmp")
        os.makedirs(temp_dir, exist_ok=True)
        safe_name = f"upload_{datetime.now().strftime('%H%M%S%f')}{ext}"
        file_path = os.path.join(temp_dir, safe_name)

        try:
            with open(file_path, "wb") as buf:
                shutil.copyfileobj(file.file, buf)

            result = disease_engine.predict(file_path)

            if result.get("success"):
                disease_name = result["disease_name"]
                confidence   = result["confidence"]
                log_prediction("DISEASE", f"{disease_name} ({confidence:.1f}%)")

                # D3 — Guard for LOW confidence predictions
                if confidence < 40.0:
                    return {
                        "status":           "uncertain",
                        "message":          "Confidence too low. Please retake with a clearer, well-lit leaf photo.",
                        "confidence":       round(confidence, 1),
                        "confidence_level": "LOW",
                        "top_predictions": [
                            {"disease": name, "confidence": round(conf, 1)}
                            for name, conf in result.get("top_predictions", [])[:3]
                        ],
                    }

                return {
                    "status":           "success",
                    "disease":          disease_name,
                    "confidence":       round(confidence, 1),
                    "plant":            result.get("plant", "Unknown"),
                    "condition":        result.get("condition", "Unknown"),
                    "confidence_level": result.get("confidence_level", "LOW"),
                    # D2 — Top-3 alternative diagnoses
                    "top_predictions": [
                        {"disease": name, "confidence": round(conf, 1)}
                        for name, conf in result.get("top_predictions", [])[:3]
                    ],
                }
            else:
                error_response(result.get("error", "Disease prediction failed"))

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    except HTTPException:
        raise
    except Exception as e:
        error_response(f"Disease prediction exception: {e}")


# ══════════════════════════════════════════════════════════════
# DETECT-DISEASE — ENSEMBLE + GRAD-CAM ENDPOINT (v3.1)
# ══════════════════════════════════════════════════════════════

@app.post("/detect-disease")
async def detect_disease(request: Request, file: UploadFile = File(...)):
    """
    Ensemble-based disease detection (EfficientNet-B0 + ResNet-50 + EfficientNet-B1).

    Output JSON (v3.1)
    -------------------
    {
        "prediction":            str,
        "confidence":            float,
        "heatmap":               str  (base64 JPEG),
        "heatmap_url":           str,
        "is_unknown":            bool,
        "unknown_reason":        str,
        "used_ensemble":         bool,
        "early_exit_triggered":  bool,
        "ensemble_weights":      dict,
        "model_confidences":     {"EfficientNet-B0": float, ...},
        "disagreement_detected": bool,
        "entropy":               float,
        "top_predictions":       [{"label": str, "confidence": float}, ...]
    }
    """
    log_request("/detect-disease", {"filename": file.filename})

    try:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in VALID_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": "Invalid image. Supported: jpg, jpeg, png, bmp, tiff, webp"}
            )

        temp_dir  = os.path.join(PROJECT_ROOT, "tmp")
        os.makedirs(temp_dir, exist_ok=True)
        safe_name = f"ensemble_{datetime.now().strftime('%H%M%S%f')}{ext}"
        file_path = os.path.join(temp_dir, safe_name)

        try:
            with open(file_path, "wb") as buf:
                shutil.copyfileobj(file.file, buf)

            # ── OPTION A: Full pipeline (Ensemble + Grad-CAM) ─
            if plant_doctor_pipeline is not None:
                diagnosis = plant_doctor_pipeline.diagnose(file_path, top_k=5)

                heatmap_b64  = ""
                heatmap_url  = ""
                heatmap_path = diagnosis.get("heatmap_path", "")
                if heatmap_path and os.path.isfile(heatmap_path):
                    try:
                        import base64
                        with open(heatmap_path, "rb") as hf:
                            heatmap_b64 = base64.b64encode(hf.read()).decode("utf-8")
                        cleanup_outputs(max_files=20)
                        heatmap_url = (
                            f"{str(request.base_url).rstrip('/')}"
                            f"/outputs/{os.path.basename(heatmap_path)}"
                        )
                    except Exception as b64_err:
                        log_error(f"Heatmap base64 failed: {b64_err}")

                em = diagnosis.get("ensemble_meta", {})
                is_unknown = em.get("is_unknown", diagnosis.get("status") == "Unknown")
                pred_str   = (
                    "Unknown Disease"
                    if is_unknown
                    else f"{diagnosis['plant']} - {diagnosis['disease']}"
                )

                log_prediction(
                    "DETECT-DISEASE",
                    f"{pred_str} ({diagnosis['confidence']:.1f}%) "
                    f"ensemble={em.get('used_ensemble')} "
                    f"early_exit={em.get('early_exit_triggered')} "
                    f"unknown={is_unknown} "
                    f"disagreement={em.get('disagreement_detected')} "
                    f"entropy={em.get('entropy', 0):.3f}"
                )

                # v3.1 top_predictions: prefer list-of-dicts, fall back to tuples
                raw_top = em.get("top_predictions_dict") or []
                if raw_top:
                    top_out = [
                        {"label": d["label"], "confidence": d["confidence_pct"]}
                        for d in raw_top[:5]
                    ]
                else:
                    top_out = [
                        {"label": name, "confidence": round(conf, 1)}
                        for name, conf in diagnosis.get("top_predictions", [])[:5]
                    ]

                return {
                    "status":                "success",
                    "prediction":            pred_str,
                    "confidence":            round(diagnosis["confidence"], 2),
                    "heatmap":               heatmap_b64,
                    "heatmap_url":           heatmap_url,
                    # open-set
                    "is_unknown":            is_unknown,
                    "unknown_detected":      is_unknown,
                    "unknown_reason":        em.get("unknown_reason", ""),
                    # ensemble meta
                    "used_ensemble":         em.get("used_ensemble", False),
                    "early_exit_triggered":  em.get("early_exit_triggered", False),
                    "ensemble_weights":      em.get("ensemble_weights", {}),
                    # quality signals
                    "model_confidences":     em.get("model_confidences", {}),
                    "disagreement_detected": em.get("disagreement_detected", False),
                    "entropy":               em.get("entropy", 0.0),
                    # predictions
                    "top_predictions":       top_out,
                    "plant":                 diagnosis.get("plant", "Unknown"),
                    "disease":               diagnosis.get("disease", "Unknown"),
                    "severity":              diagnosis.get("severity", {}),
                }

            # ── OPTION B: Ensemble only (no Grad-CAM) ─────────
            elif ensemble_engine is not None:
                result = ensemble_engine.predict(file_path, top_k=5)
                if not result.get("success"):
                    error_response(result.get("error", "Ensemble prediction failed"))

                top_out = [
                    {"label": d["label"], "confidence": d["confidence_pct"]}
                    for d in result.get("top_predictions", [])[:5]
                ]
                log_prediction(
                    "DETECT-DISEASE",
                    f"{result['prediction']} ({result['confidence']:.1f}%) "
                    f"ensemble={result.get('used_ensemble')} "
                    f"unknown={result.get('is_unknown')}"
                )
                return {
                    "status":                "success",
                    "prediction":            result["prediction"],
                    "confidence":            round(result["confidence"], 2),
                    "heatmap":               "",
                    "heatmap_url":           "",
                    "is_unknown":            result.get("is_unknown", False),
                    "unknown_detected":      result.get("unknown_detected", False),
                    "unknown_reason":        result.get("unknown_reason", ""),
                    "used_ensemble":         result.get("used_ensemble", False),
                    "early_exit_triggered":  result.get("early_exit_triggered", False),
                    "ensemble_weights":      result.get("ensemble_weights", {}),
                    "model_confidences":     result.get("model_confidences", {}),
                    "disagreement_detected": result.get("disagreement_detected", False),
                    "entropy":               result.get("entropy", 0.0),
                    "top_predictions":       top_out,
                }

            # ── OPTION C: Single B0 fallback ───────────────────
            elif _disease_loaded and disease_engine is not None:
                result = disease_engine.predict(file_path, top_k=5)
                if not result.get("success"):
                    error_response(result.get("error", "Disease prediction failed"))
                top_out = [
                    {"label": name, "confidence": round(conf, 1)}
                    for name, conf in result.get("top_predictions", [])[:5]
                ]
                return {
                    "status":                "success",
                    "prediction":            result["disease_name"],
                    "confidence":            round(result["confidence"], 2),
                    "heatmap":               "",
                    "heatmap_url":           "",
                    "is_unknown":            result["confidence"] < 70.0,
                    "unknown_detected":      result["confidence"] < 70.0,
                    "unknown_reason":        "low_confidence(single_model)" if result["confidence"] < 70.0 else "",
                    "used_ensemble":         False,
                    "early_exit_triggered":  False,
                    "ensemble_weights":      {},
                    "model_confidences":     {"efficientnet_b0": round(result["confidence"], 2)},
                    "disagreement_detected": False,
                    "entropy":               0.0,
                    "top_predictions":       top_out,
                }
            else:
                error_response("No disease models are loaded", 503)

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    except HTTPException:
        raise
    except Exception as e:
        error_response(f"Detect-disease exception: {e}")


# ══════════════════════════════════════════════════════════════
# ENSEMBLE WEIGHT MANAGEMENT ENDPOINTS
# ══════════════════════════════════════════════════════════════

@app.get("/ensemble-weights")
async def get_ensemble_weights():
    """
    Return current ensemble model weights.

    Response
    --------
    {
        "weights": {"efficientnet_b0": 0.4, "resnet50": 0.3, "efficientnet_b1": 0.3},
        "ensemble_loaded": bool
    }
    """
    if ensemble_engine is None:
        return {"weights": {}, "ensemble_loaded": False}
    return {"weights": ensemble_engine.weights, "ensemble_loaded": _ensemble_loaded}


@app.post("/ensemble-weights")
async def update_ensemble_weights(payload: dict):
    """
    Dynamically update ensemble weights at runtime.

    Accepts two modes:

    Mode 1 — Direct weights:
        { "weights": {"efficientnet_b0": 0.5, "resnet50": 0.25, "efficientnet_b1": 0.25} }

    Mode 2 — Accuracy-based (auto-normalized):
        { "accuracies": {"efficientnet_b0": 0.946, "resnet50": 0.921, "efficientnet_b1": 0.934} }

    Response
    --------
    { "status": "updated", "new_weights": { ... } }
    """
    if ensemble_engine is None:
        raise HTTPException(status_code=503, detail="Ensemble engine not loaded.")

    try:
        from smart_system.ensemble_engine import compute_weights_from_accuracy

        if "accuracies" in payload:
            accs = payload["accuracies"]
            if not isinstance(accs, dict) or len(accs) == 0:
                raise HTTPException(status_code=422, detail="'accuracies' must be a non-empty dict.")
            ensemble_engine.set_weights_from_accuracy(accs)
            log_info(f"Ensemble weights updated from accuracies: {accs}")

        elif "weights" in payload:
            w = payload["weights"]
            if not isinstance(w, dict) or len(w) == 0:
                raise HTTPException(status_code=422, detail="'weights' must be a non-empty dict.")
            ensemble_engine.set_weights(w)
            log_info(f"Ensemble weights manually updated: {w}")

        else:
            raise HTTPException(
                status_code=422,
                detail="Payload must contain 'weights' or 'accuracies' key."
            )

        return {"status": "updated", "new_weights": ensemble_engine.weights}

    except HTTPException:
        raise
    except Exception as e:
        error_response(f"Weight update failed: {e}")


@app.post("/predict-crop")
async def predict_crop(request: CropRequest):
    log_request("/predict-crop", request.dict())
    try:
        if not _crop_loaded or crop_engine is None:
            error_response("Crop model is not loaded", 503)

        result = crop_engine.predict(
            N=request.Nitrogen,
            P=request.Phosphorus,
            K=request.Potassium,
            temperature=request.Temperature,
            humidity=request.Humidity,
            ph=request.pH,
            rainfall=request.Rainfall,
        )

        if result.get("success"):
            crop_name  = result["crop_name"]
            confidence = result.get("confidence", 0.0)
            log_prediction("CROP", f"{crop_name} ({confidence:.1f}%)")
            
            # C5 — Agronomic advice based on soil/weather
            advice = RecommendationEngine.get_crop_advice(
                crop_name=crop_name,
                N=request.Nitrogen,
                P=request.Phosphorus,
                K=request.Potassium,
                temperature=request.Temperature,
                humidity=request.Humidity,
                ph=request.pH,
                rainfall=request.Rainfall,
            )
            
            return {
                "status":           "success",
                "recommended_crop": crop_name,
                "confidence":       round(confidence, 1),
                "agronomic_advice": advice,
                "ai_advice":        result.get("ai_advice", "AI advice temporally unavailable."),
                # C1 — Top-3 alternative crop recommendations
                "top_recommendations": [
                    {"crop": crop, "confidence": round(conf, 1)}
                    for crop, conf in result.get("top_predictions", [])[:3]
                ],
            }
        else:
            error_response(result.get("error", "Crop prediction failed"))

    except HTTPException:
        raise
    except Exception as e:
        error_response(f"Crop prediction exception: {e}")


@app.post("/predict-yield")
async def predict_yield(request: YieldRequest):
    log_request("/predict-yield", request.dict())
    try:
        if not _yield_loaded or yield_engine is None:
            error_response("Yield model is not loaded", 503)

        result = yield_engine.predict(
            area=request.Area,
            crop=request.Crop,
            year=request.Year,
            season=request.Season,
        )

        if result.get("success"):
            pred_yield  = result["predicted_yield"]
            yield_level = result.get("yield_level", "UNKNOWN")
            uncertainty = result.get("yield_uncertainty")
            log_prediction("YIELD", f"{pred_yield:.2f} t/ha ({yield_level})")
            return {
                "status":            "success",
                "predicted_yield":   pred_yield,
                "yield_level":       yield_level,
                "yield_uncertainty": uncertainty,
                "yield_unit":        result.get("yield_unit", "hg/ha"),
            }
        else:
            detail_msg = result.get("error", "Yield prediction failed")
            suggestions = result.get("suggestions")
            if suggestions:
                detail_msg += f" — Did you mean: {suggestions[:5]}"
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": detail_msg}
            )

    except HTTPException:
        raise
    except Exception as e:
        error_response(f"Yield prediction exception: {e}")


# ══════════════════════════════════════════════════════════════
# PHASE 1 — NEW YIELD PREDICTION PIPELINE
# ══════════════════════════════════════════════════════════════

@app.post("/predict-yield-v2")
async def predict_yield_v2(payload: dict):
    """
    Phase-1 Yield Prediction Pipeline.

    Input  : { "crop": str, "state": str, "season": str, "year": int }
    Output : predicted_yield (hg/ha), yield_level, weather data used
    """
    from smart_system.yield_predictor.schema import YieldInput
    from pydantic import ValidationError

    log_request("/predict-yield-v2", payload)

    # Validate input with Pydantic
    try:
        yield_input = YieldInput(**payload)
    except ValidationError as ve:
        raise HTTPException(
            status_code=422,
            detail={"status": "error", "message": ve.errors()}
        )

    if yield_pipeline is None:
        error_response("Yield Prediction Pipeline is not loaded", 503)

    try:
        result = yield_pipeline.predict(yield_input)

        if result.get("success"):
            log_prediction(
                "YIELD-V2",
                f"{result['area']} | {result['crop']} | {result['year']} "
                f"→ {result['predicted_yield']:,.2f} hg/ha ({result['yield_level']})"
            )
            return {"status": "success", **result}
        else:
            detail_msg = result.get("error", "Yield prediction failed")
            suggestions = result.get("suggestions")
            if suggestions:
                detail_msg += f" — Did you mean: {suggestions[:5]}"
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": detail_msg}
            )

    except HTTPException:
        raise
    except Exception as e:
        error_response(f"Yield-v2 prediction exception: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — INTELLIGENCE LAYER ENDPOINT
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/predict-yield-v2/full")
async def predict_yield_full(payload: dict):
    """
    Phase-2 Yield Prediction + Intelligence Pipeline.

    Runs Phase-1 (prediction) and augments the result with:
      - explanation  : WHY the model predicted this yield
      - recommendations : fertilizer, irrigation, pest watch, best practices
      - risk         : overall risk score + factor breakdown + mitigations

    Input  : { "crop": str, "state": str, "season": str, "year": int }
    Output : Phase-1 result + 'intelligence' block (structured JSON)
    """
    from smart_system.yield_predictor.schema import YieldInput
    from pydantic import ValidationError

    log_request("/predict-yield-v2/full", payload)

    # Validate input
    try:
        yield_input = YieldInput(**payload)
    except ValidationError as ve:
        raise HTTPException(
            status_code=422,
            detail={"status": "error", "message": ve.errors()}
        )

    if yield_pipeline is None:
        error_response("Yield Prediction Pipeline is not loaded", 503)

    try:
        result = yield_pipeline.predict_full(yield_input)

        if result.get("success"):
            intel   = result.get("intelligence", {})
            risk    = intel.get("risk", {})
            log_prediction(
                "YIELD-FULL",
                f"{result['area']} | {result['crop']} | {result['year']} "
                f"→ {result['predicted_yield']:,.2f} hg/ha "
                f"({result['yield_level']}) | Risk: {risk.get('overall_risk', '?')}"
            )
            return {"status": "success", **result}
        else:
            detail_msg  = result.get("error", "Yield prediction failed")
            suggestions = result.get("suggestions")
            if suggestions:
                detail_msg += f" — Did you mean: {suggestions[:5]}"
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": detail_msg}
            )

    except HTTPException:
        raise
    except Exception as e:
        error_response(f"Yield-full prediction exception: {e}")


@app.post("/farm-assistant")
async def farm_assistant(request: FarmAssistantRequest):
    log_request("/farm-assistant", request.dict())
    try:
        question = request.question
        answer = generate_farming_response(question)
        
        # We don't log the full answer to keep logs clean, but log the query
        logger.info(f"Farm Assistant Query: '{question}'")
        
        return {
            "status": "success",
            "question": question,
            "answer": answer
        }
    except Exception as e:
        error_response(f"Farm assistant exception: {e}")


# ══════════════════════════════════════════════════════════════
# PLANT DOCTOR — AI DIAGNOSIS PIPELINE
# ══════════════════════════════════════════════════════════════

@app.post("/plant-doctor")
async def plant_doctor_diagnose(request: Request, file: UploadFile = File(...)):
    """Full AI Plant Doctor diagnosis with explainability."""
    log_request("/plant-doctor", {"filename": file.filename})
    try:
        if plant_doctor_pipeline is None:
            error_response("Plant Doctor pipeline is not loaded", 503)

        # Validate image extension
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in VALID_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": "Invalid image file. Supported: jpg, jpeg, png, bmp, tiff, webp"}
            )

        # Save temp file
        temp_dir = os.path.join(PROJECT_ROOT, "tmp")
        os.makedirs(temp_dir, exist_ok=True)
        safe_name = f"doctor_{datetime.now().strftime('%H%M%S%f')}{ext}"
        file_path = os.path.join(temp_dir, safe_name)

        try:
            with open(file_path, "wb") as buf:
                shutil.copyfileobj(file.file, buf)

            # Run the full diagnostic pipeline
            result = plant_doctor_pipeline.diagnose(file_path)

            # ── Construct Visual Output URL (Improvement #4) ─────
            # Return a full URL instead of a local file path
            if result.get("heatmap_path"):
                base_url = str(request.base_url).rstrip("/")
                filename = os.path.basename(result["heatmap_path"])
                result["visual_output"] = f"{base_url}/outputs/{filename}"
                
                # Dynamic cleanup (Improvement #7)
                cleanup_outputs(max_files=20)
            else:
                result["visual_output"] = ""

            log_prediction("PLANT_DOCTOR",
                f"{result['plant']} — {result['disease']} "
                f"({result['confidence']:.1f}%) "
                f"[{result['status']}] "
                f"Severity: {result['severity']['level']}"
            )

            return {
                "status": "success",
                **result,
            }

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    except HTTPException:
        raise
    except Exception as e:
        error_response(f"Plant Doctor exception: {e}")


@app.post("/yield-trends")
async def get_yield_trends(request: YieldTrendRequest):
    log_request("/yield-trends", request.dict())
    if yield_trends_df is None:
        error_response("Yield trends data not loaded", 503)
        
    try:
        filtered = yield_trends_df[
            (yield_trends_df['Area'].str.lower() == request.Area.lower()) &
            (yield_trends_df['Item'].str.lower() == request.Crop.lower())
        ]
        
        if filtered.empty:
            return {"status": "success", "success": True, "area": request.Area, "crop": request.Crop, "trends": []}
            
        filtered = filtered.sort_values(by='Year')
        
        trends = []
        for _, row in filtered.iterrows():
            trends.append({
                "Year": int(row['Year']),
                "Yield": float(row['Yield'])
            })
            
        return {
            "status": "success",
            "success": True,
            "area": request.Area,
            "crop": request.Crop,
            "trends": trends
        }
    except Exception as e:
        log_error(f"Yield trends error: {e}")
        error_response(f"Failed to fetch trends: {e}")


@app.post("/smart-report")
async def smart_report(
    file:        UploadFile = File(None),
    Nitrogen:    float      = Form(...),
    Phosphorus:  float      = Form(...),
    Potassium:   float      = Form(...),
    Temperature: float      = Form(...),
    Humidity:    float      = Form(...),
    pH:          float      = Form(...),
    Rainfall:    float      = Form(...),
    Area:        str        = Form(...),
    Crop:        str        = Form(...),
    Year:        int        = Form(...),
    Season:      str        = Form(None),
):
    log_request("/smart-report", {"Area": Area, "Crop": Crop, "Year": Year})
    report = {
        "disease_prediction":   None,
        "crop_recommendation":  None,
        "yield_prediction":     None,
        "summary":              "Smart Farm Report generated.",
    }

    # 1. Disease —————————————————————————————————————————
    if file and file.filename:
        try:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in VALID_IMAGE_EXTENSIONS:
                report["disease_prediction"] = {"error": "Invalid image file type"}
            elif not _disease_loaded or disease_engine is None:
                report["disease_prediction"] = {"error": "Disease model not loaded"}
            else:
                temp_dir  = os.path.join(PROJECT_ROOT, "tmp")
                os.makedirs(temp_dir, exist_ok=True)
                safe_name = f"report_{datetime.now().strftime('%H%M%S%f')}{ext}"
                file_path = os.path.join(temp_dir, safe_name)
                try:
                    with open(file_path, "wb") as buf:
                        shutil.copyfileobj(file.file, buf)
                    d_res = disease_engine.predict(file_path)
                    if d_res.get("success"):
                        report["disease_prediction"] = {
                            "disease":    d_res["disease_name"],
                            "confidence": d_res["confidence"],
                        }
                        log_prediction("DISEASE", d_res["disease_name"])
                    else:
                        report["disease_prediction"] = {"error": d_res.get("error")}
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)
        except Exception as e:
            report["disease_prediction"] = {"error": str(e)}
            log_error(f"Smart-report disease error: {e}")

    # 2. Crop ─────────────────────────────────────────────
    try:
        if not _crop_loaded or crop_engine is None:
            report["crop_recommendation"] = {"error": "Crop model not loaded"}
        else:
            c_res = crop_engine.predict(
                N=Nitrogen, P=Phosphorus, K=Potassium,
                temperature=Temperature, humidity=Humidity,
                ph=pH, rainfall=Rainfall,
            )
            if c_res.get("success"):
                report["crop_recommendation"] = {
                    "recommended_crop": c_res["crop_name"],
                    "confidence":       c_res.get("confidence"),
                }
                log_prediction("CROP", c_res["crop_name"])
            else:
                report["crop_recommendation"] = {"error": c_res.get("error")}
    except Exception as e:
        report["crop_recommendation"] = {"error": str(e)}
        log_error(f"Smart-report crop error: {e}")

    # 3. Yield ────────────────────────────────────────────
    try:
        if not _yield_loaded or yield_engine is None:
            report["yield_prediction"] = {"error": "Yield model not loaded"}
        else:
            y_res = yield_engine.predict(area=Area, crop=Crop, year=Year, season=Season)
            if y_res.get("success"):
                report["yield_prediction"] = {
                    "predicted_yield":   y_res["predicted_yield"],
                    "yield_level":       y_res.get("yield_level"),
                    "yield_uncertainty": y_res.get("yield_uncertainty"),
                    "yield_unit":        y_res.get("yield_unit", "hg/ha"),
                }
                log_prediction("YIELD", f"{y_res['predicted_yield']:.2f} t/ha")
            else:
                report["yield_prediction"] = {"error": y_res.get("error")}
    except Exception as e:
        report["yield_prediction"] = {"error": str(e)}
        log_error(f"Smart-report yield error: {e}")

    return {"smart_report": report}


# ══════════════════════════════════════════════════════════════
# GLOBAL EXCEPTION HANDLER — never crash
# ══════════════════════════════════════════════════════════════

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_error(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
