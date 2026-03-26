"""
Plant Doctor — AI Plant Disease Detection & Decision Support
================================================================
Modular post-processing pipeline that wraps the existing
EfficientNet disease model with advanced features:

  • Image quality assessment (blur, brightness)
  • Confidence calibration (temperature scaling + soft cap)
  • Grad-CAM disease localization & heatmap generation
  • Severity estimation from Grad-CAM masks
  • Risk level assessment (Low / Moderate / High)
  • Open-world unknown disease detection
  • Explanation engine (why the disease occurred)
  • Treatment recommendations (what to do)
  • FAISS-based disease similarity search
  • Multi-label top-K output
  • Global plant + disease label parsing
  • Display formatting (frontend-ready output)

Architecture (v2.0)
--------------------
  Input Image
    -> Image Quality Check
    -> Core Model (EfficientNet)
    -> Confidence Calibration
    -> Top-K + Confidence
    -> Open-World Detection
    -> Grad-CAM
    -> Severity Estimation
    -> Risk Assessment
    -> Explanation Engine
    -> Treatment System
    -> Similarity Search
    -> Display Formatter
    -> Final Structured Output

Author  : Smart Agriculture AI Team
Version : 2.0.0
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

__all__ = [
    "PlantDoctorPipeline",
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
