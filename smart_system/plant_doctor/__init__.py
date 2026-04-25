"""
Plant Doctor — AI Plant Disease Detection & Decision Support
================================================================
Modular post-processing pipeline that wraps the ensemble disease model
with advanced features:

  • Image quality assessment (blur, brightness)
  • Ensemble inference (EfficientNet-B0 + ResNet-50 + EfficientNet-B1)
  • Confidence calibration (temperature scaling + soft cap)
  • Grad-CAM disease localization from EfficientNet-B0 only
  • Severity estimation from Grad-CAM masks
  • Risk level assessment (Low / Moderate / High)
  • Open-world unknown disease detection (ensemble probability threshold)
  • Explanation engine (why the disease occurred)
  • Treatment recommendations (what to do)
  • FAISS-based disease similarity search
  • Multi-label top-K output
  • Global plant + disease label parsing
  • Display formatting (frontend-ready output)

Architecture (v3.0 Ensemble)
------------------------------
  Input Image
    -> Image Quality Check
    -> Ensemble Inference (EfficientNet-B0 + ResNet-50 + EfficientNet-B1)
    -> Confidence Calibration
    -> Top-K + Confidence
    -> Open-World Detection (ensemble probability threshold)
    -> Grad-CAM (EfficientNet-B0 ONLY)
    -> Severity Estimation
    -> Risk Assessment
    -> Explanation Engine
    -> Treatment System
    -> Similarity Search
    -> Display Formatter
    -> Final Structured Output

Author  : Smart Agriculture AI Team
Version : 3.0.0
"""

from .pipeline import PlantDoctorPipeline
from .image_quality import ImageQualityChecker
from .confidence_calibrator import ConfidenceCalibrator
from .gradcam import GradCAMGenerator
from .severity import SeverityEstimator
from .risk_assessor import RiskAssessor
from .open_world import OpenWorldDetector
from .explanation_engine import ExplanationEngine
from .treatment_engine import TreatmentEngine
from .similarity import DiseaseSimilaritySearch
from .label_parser import LabelParser
from .display_formatter import DisplayFormatter
from .final_output_enhancer import FinalOutputEnhancer
from .ensemble_predictor import EnsemblePredictor

__all__ = [
    "PlantDoctorPipeline",
    "EnsemblePredictor",
    "ImageQualityChecker",
    "ConfidenceCalibrator",
    "GradCAMGenerator",
    "SeverityEstimator",
    "RiskAssessor",
    "OpenWorldDetector",
    "ExplanationEngine",
    "TreatmentEngine",
    "DiseaseSimilaritySearch",
    "LabelParser",
    "DisplayFormatter",
    "FinalOutputEnhancer",
]
