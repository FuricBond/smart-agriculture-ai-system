"""
Prediction History Manager — Dashboard Utility
==================================================
Stores and manages the last 20 predictions in session state.
"""

import datetime
import streamlit as st


MAX_HISTORY = 20


def _ensure_history():
    """Initialize history in session state if needed."""
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []


def add_prediction(pred_type: str, inputs: dict, results: dict):
    """
    Add a prediction to history.
    
    Parameters
    ----------
    pred_type : str
        'disease', 'crop', or 'yield'
    inputs : dict
        Input parameters used.
    results : dict
        Prediction results.
    """
    _ensure_history()
    
    entry = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': pred_type,
        'inputs': inputs,
        'results': results,
    }
    
    st.session_state.prediction_history.insert(0, entry)
    
    # Keep only last N entries
    if len(st.session_state.prediction_history) > MAX_HISTORY:
        st.session_state.prediction_history = st.session_state.prediction_history[:MAX_HISTORY]


def get_history():
    """Get all prediction history entries."""
    _ensure_history()
    return st.session_state.prediction_history


def clear_history():
    """Clear all prediction history."""
    st.session_state.prediction_history = []


def get_history_count():
    """Get count of history entries."""
    _ensure_history()
    return len(st.session_state.prediction_history)


def get_type_icon(pred_type: str) -> str:
    """Get icon for prediction type."""
    icons = {
        'disease': '🔬',
        'crop': '🌱',
        'yield': '📊',
        'report': '📋',
    }
    return icons.get(pred_type, '📌')


def get_type_color(pred_type: str) -> str:
    """Get color for prediction type."""
    colors = {
        'disease': '#ff4757',
        'crop': '#00ff88',
        'yield': '#00d4ff',
        'report': '#a855f7',
    }
    return colors.get(pred_type, '#8b9a92')
