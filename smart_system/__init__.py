"""
Smart Agriculture System — Intelligent Advisory Engine
=========================================================
A professional AI system that integrates Disease Detection,
Crop Recommendation, and Yield Prediction models into a
unified intelligent prediction pipeline.

Modules
-------
config           : Centralized paths, thresholds, model metadata
disease_engine   : Disease detection wrapper (ResNet50 CNN)
crop_engine      : Crop recommendation wrapper (Ensemble ML)
yield_engine     : Yield prediction wrapper (RandomForest)
risk_analysis    : Soil quality, disease severity, overall health
recommendations  : Intelligent advisory engine
report           : Smart Farm Report generator
logger           : Session & event logging
smart_predict    : Main interactive pipeline
evaluation       : Automated testing suite

Usage
-----
    cd C:\\CropProject
    python -m smart_system             # Interactive mode
    python -m smart_system.evaluation  # Automated evaluation

Author  : Smart Agriculture AI Team
Version : 2.0.0
"""

__version__ = "2.0.0"
__author__  = "Smart Agriculture AI Team"
__all__     = [
    "config",
    "disease_engine",
    "crop_engine",
    "yield_engine",
    "risk_analysis",
    "recommendations",
    "report",
    "logger",
    "smart_predict",
    "evaluation",
]
