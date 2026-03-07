"""
System Status Page — Smart Agriculture Dashboard
"""

import os
import sys
import streamlit as st
from components.ui import (
    inject_css, page_header, section_header, floating_navbar, theme_toggle,
    status_indicator, glass_card,
)
from utils.model_loader import get_all_models

st.set_page_config(page_title="System Status — Smart Agri AI", page_icon="⚙️", layout="wide", initial_sidebar_state="collapsed")
inject_css()
floating_navbar("Status")
theme_toggle()

page_header("⚙️", "System Status", "Monitor AI models and system health in real-time")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MODEL STATUS
# ══════════════════════════════════════════════════════════════
section_header("📡", "Active Model Status")

models = get_all_models()

for key, name, arch in [
    ('disease', '🔬 Disease Detection Model', 'ResNet50 CNN (PyTorch)'),
    ('crop', '🌱 Crop Recommendation Model', 'Ensemble (RF + XGB + LGBM)'),
    ('yield', '📊 Yield Prediction Model', 'RandomForest Regressor'),
]:
    m = models[key]
    status_indicator(
        f"{name} — {arch}",
        m['loaded'], m['load_time'], m['model_size'],
    )

# Smart Engine
st.markdown('''
<div class="glass-card animate-fade-in-up" style="padding:1.2rem 1.6rem;margin-bottom:0.8rem;display:flex;
    align-items:center;justify-content:space-between;">
    <div><span style="font-weight:700;color:var(--text-primary);font-family:var(--font-heading);font-size:1.05rem;">
        ⚡ Smart Advisory Engine — Risk Analysis + Recommendations
    </span></div>
    <div style="display:flex;align-items:center;gap:15px;">
        <span style="color:var(--text-secondary);font-size:0.85rem;font-weight:500;">Always active</span>
        <span class="status-badge status-active">
            <span class="glow-dot glow-dot-green"></span> Active
        </span>
    </div>
</div>
''', unsafe_allow_html=True)

# Summary metrics
loaded = sum(1 for k in ['disease', 'crop', 'yield'] if models[k]['loaded'])
total_time = sum(models[k]['load_time'] for k in ['disease', 'crop', 'yield'])
total_size = sum(models[k]['model_size'] for k in ['disease', 'crop', 'yield'])

mc1, mc2, mc3, mc4 = st.columns(4)
mc1.metric("Models Loaded", f"{loaded}/3")
mc2.metric("Total Load Time", f"{total_time:.1f}s")
mc3.metric("Total Model Size", f"{total_size:.0f} MB")
mc4.metric("System Status", "✅ Online" if loaded == 3 else "⚠️ Partial")

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MODEL DETAILS
# ══════════════════════════════════════════════════════════════
section_header("📦", "Technical Specifications")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from smart_system import config
    
    for key in ['disease', 'crop', 'yield']:
        info = config.MODEL_INFO[key]
        with st.expander(f"{'🔬' if key == 'disease' else '🌱' if key == 'crop' else '📊'} {info['name']}", expanded=True):
            mc1, mc2 = st.columns(2)
            with mc1:
                st.markdown(f"**Architecture:** {info['architecture']}")
                st.markdown(f"**Framework:** {info['framework']}")
                st.markdown(f"**Dataset:** {info['dataset']}")
            with mc2:
                st.markdown(f"**Dataset Size:** {info['dataset_size']}")
                st.markdown(f"**Classes:** {info['classes']}")
                st.markdown(f"**Input:** {info['input']}")
                st.markdown(f"**Output:** {info['output']}")
except Exception:
    st.info("Detailed model specifications are currently unavailable. Wait for modules to initialize.")

st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
