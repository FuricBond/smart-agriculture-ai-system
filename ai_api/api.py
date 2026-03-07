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

# ── Add project root to sys.path ──────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import uvicorn

from smart_system.recommendations import RecommendationEngine

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

_disease_loaded = False
_crop_loaded    = False
_yield_loaded   = False
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


# ══════════════════════════════════════════════════════════════
# PART 2 + 3 — SAFE STARTUP MODEL LOADING + DIAGNOSTICS BANNER
# ══════════════════════════════════════════════════════════════

@app.on_event("startup")
def startup():
    global disease_engine, crop_engine, yield_engine
    global _disease_loaded, _crop_loaded, _yield_loaded

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

    disease_icon = "✓" if disease_status else "⚠️  MISSING"
    crop_icon    = "✓" if crop_status    else "⚠️  MISSING"
    yield_icon   = "✓" if yield_status   else "⚠️  MISSING"

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
    Disease Model  {disease_icon}
    Crop Model     {crop_icon}
    Yield Model    {yield_icon}
================================
"""
    print(banner)
    log_info(f"Server started | disease={disease_status} | crop={crop_status} | yield={yield_status}")


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
            log_info("Disease Model Loaded ✓")
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
            log_info("Crop Model Loaded ✓")
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
            log_info("Yield Model Loaded ✓")
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
        "status":        "running",
        "disease_model": _disease_loaded,
        "crop_model":    _crop_loaded,
        "yield_model":   _yield_loaded,
        "timestamp":     datetime.now().isoformat()
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
            return {"status": "success", "area": request.Area, "crop": request.Crop, "trends": []}
            
        filtered = filtered.sort_values(by='Year')
        
        trends = []
        for _, row in filtered.iterrows():
            trends.append({
                "year": int(row['Year']),
                "yield": float(row['Yield_kg_per_hectare'])
            })
            
        return {
            "status": "success",
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
