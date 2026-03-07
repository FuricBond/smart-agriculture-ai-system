"""
Smart Agriculture AI Platform — Dashboard v2.0
===================================================
Main entry point and home page for the Streamlit dashboard.

Launch:
    cd C:\\CropProject\\dashboard
    streamlit run app.py
"""

import os
import streamlit as st
from components.ui import (
    inject_css, particles_background, hero_section, 
    stat_card, feature_card, status_indicator,
    section_header, architecture_diagram, glass_card,
    floating_navbar, theme_toggle
)

# ── Page Configuration ────────────────────────────────────────
st.set_page_config(
    page_title="Smart Agriculture AI Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inject Custom CSS ─────────────────────────────────────────
inject_css()

# ── Floating Navigation & Theme Toggle ─────────────────────────
floating_navbar("Home")
theme_toggle()

# ── Particles Background ─────────────────────────────────────
particles_background()

# ══════════════════════════════════════════════════════════════
# HERO SECTION
# ══════════════════════════════════════════════════════════════
hero_section()

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SYSTEM CAPABILITIES
# ══════════════════════════════════════════════════════════════
section_header("⚡", "System Capabilities")

cap_cols = st.columns(4)
capabilities = [
    ("🔬", "Disease Detection AI", "Deep learning CNN identifies 52 plant diseases from leaf images with high accuracy"),
    ("🌱", "Crop Recommendation AI", "Ensemble ML model recommends optimal crops based on soil & weather conditions"),
    ("📊", "Yield Prediction AI", "Random Forest regressor predicts crop yield from historical and regional data"),
    ("🧠", "Smart Advisory AI", "Cross-module intelligence combining all models for comprehensive farm analysis"),
]
for col, (icon, title, desc) in zip(cap_cols, capabilities):
    with col:
        feature_card(icon, title, desc)

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ANIMATED COUNTERS
# ══════════════════════════════════════════════════════════════
section_header("📈", "Training Data Scale")

counter_cols = st.columns(4)
counters = [
    ("🖼️", "115,000+", "Disease Images"),
    ("🦠", "52", "Disease Classes"),
    ("🌾", "6,600+", "Crop Records"),
    ("📊", "8.7M+", "Yield Records"),
]
for col, (icon, value, label) in zip(counter_cols, counters):
    with col:
        stat_card(icon, value, label)

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SYSTEM ARCHITECTURE
# ══════════════════════════════════════════════════════════════
section_header("🏗️", "System Architecture")

st.markdown("""
<div style='text-align:center;padding:0.5rem 0;'>
    <div style='font-size:0.85rem;color:#4a5a52;margin-bottom:0.5rem;'>
        Data flows from input sources through AI models into the Smart Decision Engine
    </div>
</div>
""", unsafe_allow_html=True)

architecture_diagram()

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MODEL STATUS PANEL (non-blocking — checks file existence only)
# ══════════════════════════════════════════════════════════════
section_header("📡", "Model Status")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

model_files = [
    ("🔬  Disease Detection Model — ResNet50 CNN",
     os.path.join(PROJECT_ROOT, 'disease_model', 'models', 'disease_model.pth'),
     "52 classes"),
    ("🌱  Crop Recommendation Model — Ensemble (RF+XGB+LGBM)",
     os.path.join(PROJECT_ROOT, 'crop_model', 'models', 'improved_crop_model.pkl'),
     "22 crops"),
    ("📊  Yield Prediction Model — RandomForest Regressor",
     os.path.join(PROJECT_ROOT, 'yield_model', 'models', 'yield_model.pkl'),
     "Multiple regions"),
]

for name, path, detail in model_files:
    exists = os.path.isfile(path)
    size_mb = round(os.path.getsize(path) / (1024 * 1024), 1) if exists else 0
    status_indicator(name, exists, 0, size_mb, detail)

# Smart System (always active)
st.markdown('''
<div class="glass-card" style="padding:1rem 1.4rem;margin-bottom:0.6rem;display:flex;align-items:center;justify-content:space-between;">
    <div>
        <span style="font-weight:600;color:#f0f4f2;font-family:'Poppins',sans-serif;">⚡  Smart Advisory Engine — Risk Analysis + Recommendations</span>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
        <span style="color:#4a5a52;font-size:0.78rem;">Always active</span>
        <span class="status-badge status-active"><span class="glow-dot glow-dot-green"></span> Active</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;font-size:0.78rem;color:#4a5a52;margin-top:0.3rem;">
    💡 Models are cached and loaded on first use — visit individual pages to activate them
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TECHNOLOGY STACK
# ══════════════════════════════════════════════════════════════
section_header("🛠️", "Technology Stack")

tech_cols = st.columns(5)
techs = [
    ("🐍", "Python", "Core Language"),
    ("🔥", "PyTorch", "Deep Learning"),
    ("📊", "Scikit-learn", "Machine Learning"),
    ("📈", "Plotly", "Visualization"),
    ("🎯", "Streamlit", "Dashboard"),
]
for col, (icon, name, role) in zip(tech_cols, techs):
    with col:
        st.markdown(f'''
        <div class="stat-card" style="min-height:100px;">
            <span style="font-size:1.5rem;">{icon}</span>
            <div style="font-family:'Poppins',sans-serif;font-weight:600;font-size:0.9rem;color:#f0f4f2;margin-top:0.3rem;">
                {name}
            </div>
            <div style="font-size:0.75rem;color:#4a5a52;">{role}</div>
        </div>
        ''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
st.markdown('''
<div style="text-align:center;padding:2rem 0;border-top:1px solid rgba(0,255,136,0.08);">
    <div style="font-family:'Poppins',sans-serif;font-weight:600;font-size:0.9rem;
        background:linear-gradient(135deg,#00ff88,#00d4ff);-webkit-background-clip:text;
        -webkit-text-fill-color:transparent;background-clip:text;">
        AI-Based Crop Health and Yield Prediction System
    </div>
    <div style="font-size:0.75rem;color:#4a5a52;margin-top:0.3rem;">
        Powered by Deep Learning &amp; Machine Learning — Version 2.0.0
    </div>
</div>
''', unsafe_allow_html=True)
