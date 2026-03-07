"""
Model Loader — Dashboard Utility
===================================
Handles cached loading of all three AI models for the dashboard.
Uses @st.cache_resource to load models once and persist across reruns.
"""

import os
import sys
import time
import streamlit as st

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@st.cache_resource(show_spinner=False)
def load_disease_engine():
    """Load and cache the Disease Detection engine."""
    try:
        from smart_system.disease_engine import DiseaseEngine
        engine = DiseaseEngine()
        start = time.time()
        success = engine.load()
        load_time = time.time() - start
        
        model_path = os.path.join(PROJECT_ROOT, 'disease_model', 'models', 'disease_model.pth')
        model_size = os.path.getsize(model_path) / (1024 * 1024) if os.path.exists(model_path) else 0
        
        return {
            'engine': engine if success else None,
            'loaded': success,
            'load_time': round(load_time, 2),
            'model_size': round(model_size, 1),
            'num_classes': engine.num_classes if success else 0,
            'error': None if success else 'Failed to load model'
        }
    except Exception as e:
        return {
            'engine': None, 'loaded': False, 'load_time': 0,
            'model_size': 0, 'num_classes': 0, 'error': str(e)
        }


@st.cache_resource(show_spinner=False)
def load_crop_engine():
    """Load and cache the Crop Recommendation engine."""
    try:
        from smart_system.crop_engine import CropEngine
        engine = CropEngine()
        start = time.time()
        success = engine.load()
        load_time = time.time() - start
        
        model_path = os.path.join(PROJECT_ROOT, 'crop_model', 'models', 'improved_crop_model.pkl')
        model_size = os.path.getsize(model_path) / (1024 * 1024) if os.path.exists(model_path) else 0
        
        num_crops = len(engine.label_encoder.classes_) if success and engine.label_encoder else 0
        
        return {
            'engine': engine if success else None,
            'loaded': success,
            'load_time': round(load_time, 2),
            'model_size': round(model_size, 1),
            'num_crops': num_crops,
            'error': None if success else 'Failed to load model'
        }
    except Exception as e:
        return {
            'engine': None, 'loaded': False, 'load_time': 0,
            'model_size': 0, 'num_crops': 0, 'error': str(e)
        }


@st.cache_resource(show_spinner=False)
def load_yield_engine():
    """Load and cache the Yield Prediction engine."""
    try:
        from smart_system.yield_engine import YieldEngine
        engine = YieldEngine()
        start = time.time()
        success = engine.load()
        load_time = time.time() - start
        
        model_path = os.path.join(PROJECT_ROOT, 'yield_model', 'models', 'yield_model.pkl')
        model_size = os.path.getsize(model_path) / (1024 * 1024) if os.path.exists(model_path) else 0
        
        return {
            'engine': engine if success else None,
            'loaded': success,
            'load_time': round(load_time, 2),
            'model_size': round(model_size, 1),
            'known_areas': engine.known_areas if success else [],
            'known_crops': engine.known_crops if success else [],
            'error': None if success else 'Failed to load model'
        }
    except Exception as e:
        return {
            'engine': None, 'loaded': False, 'load_time': 0,
            'model_size': 0, 'known_areas': [], 'known_crops': [],
            'error': str(e)
        }


def load_risk_analyzer():
    """Load the Risk Analyzer (stateless, no caching needed)."""
    try:
        from smart_system.risk_analysis import RiskAnalyzer
        return RiskAnalyzer()
    except Exception:
        return None


def load_recommendation_engine():
    """Load the Recommendation Engine (stateless)."""
    try:
        from smart_system.recommendations import RecommendationEngine
        return RecommendationEngine()
    except Exception:
        return None


def get_all_models():
    """Load all models and return status dict."""
    disease = load_disease_engine()
    crop = load_crop_engine()
    yield_m = load_yield_engine()
    
    return {
        'disease': disease,
        'crop': crop,
        'yield': yield_m,
        'all_loaded': disease['loaded'] and crop['loaded'] and yield_m['loaded']
    }
