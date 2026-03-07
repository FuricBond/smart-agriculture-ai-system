"""
Crop Recommendation Page — Smart Agriculture Dashboard
"""

import streamlit as st
from components.ui import (
    inject_css, page_header, section_header, floating_navbar, theme_toggle,
    confidence_bar, result_display, glass_card, recommendation_card,
)
from components.charts import soil_radar_chart, confidence_bar_chart, crop_probability_chart
from utils.model_loader import load_crop_engine, load_risk_analyzer, load_recommendation_engine
from utils.history import add_prediction

st.set_page_config(page_title="Crop Recommendation — Smart Agri AI", page_icon="🌱", layout="wide", initial_sidebar_state="collapsed")
inject_css()
floating_navbar("Crop")
theme_toggle()

page_header("🌱", "Crop Recommendation", "AI-powered crop suggestion based on soil & weather conditions")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ── Load Model ────────────────────────────────────────────────
crop_info = load_crop_engine()
engine = crop_info['engine']

if not crop_info['loaded']:
    st.error(f"⚠️ Crop model not available: {crop_info.get('error', 'Unknown error')}")
    st.stop()

# Model info badges
st.markdown(f'''
<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:1rem;">
    <span class="status-badge status-active">🧠 Ensemble ML</span>
    <span class="status-badge status-active">🌾 {crop_info["num_crops"]} Crops</span>
    <span class="status-badge status-active">⏱️ {crop_info["load_time"]}s load</span>
    <span class="status-badge status-active">📐 21 Features</span>
</div>
''', unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# INPUT PARAMETERS
# ══════════════════════════════════════════════════════════════
section_header("📋", "Soil & Weather Parameters")

col1, col2 = st.columns(2)

with col1:
    st.markdown('''
    <div class="glass-card">
        <div style="font-family:'Poppins',sans-serif;font-weight:600;color:#00ff88;
            margin-bottom:0.5rem;">🧪 Soil Nutrients (kg/ha)</div>
    </div>
    ''', unsafe_allow_html=True)
    
    N = st.slider("Nitrogen (N)", 0, 200, 90, help="Nitrogen content in kg/ha")
    P = st.slider("Phosphorus (P)", 0, 150, 42, help="Phosphorus content in kg/ha")
    K = st.slider("Potassium (K)", 0, 250, 43, help="Potassium content in kg/ha")
    ph = st.slider("pH Level", 0.0, 14.0, 6.5, 0.1, help="Soil pH value (0-14)")

with col2:
    st.markdown('''
    <div class="glass-card">
        <div style="font-family:'Poppins',sans-serif;font-weight:600;color:#00d4ff;
            margin-bottom:0.5rem;">🌤️ Weather Conditions</div>
    </div>
    ''', unsafe_allow_html=True)
    
    temperature = st.slider("Temperature (°C)", -5, 55, 25, help="Current temperature")
    humidity = st.slider("Humidity (%)", 0, 100, 80, help="Relative humidity percentage")
    rainfall = st.slider("Rainfall (mm)", 0, 3000, 200, help="Seasonal rainfall in mm")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ── Soil Radar Preview ────────────────────────────────────────
with st.expander("📊 View Soil & Environment Profile", expanded=True):
    fig = soil_radar_chart(N, P, K, temperature, humidity, ph, rainfall)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# PREDICTION
# ══════════════════════════════════════════════════════════════
predict_btn = st.button("🌱  Get Crop Recommendation", use_container_width=True, type="primary")

if predict_btn:
    with st.spinner(""):
        st.markdown('''
        <div style="text-align:center;padding:1rem;">
            <div class="loading-spinner"></div>
            <div style="color:#8b9a92;font-size:0.85rem;margin-top:0.5rem;">
                Analyzing soil profile with Ensemble ML model...
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        result = engine.predict(N, P, K, temperature, humidity, ph, rainfall, top_k=5)
    
    if result['success']:
        # Save to history
        add_prediction('crop', {
            'N': N, 'P': P, 'K': K, 'Temperature': temperature,
            'Humidity': humidity, 'pH': ph, 'Rainfall': rainfall
        }, result)
        
        crop_name = result['crop_name']
        confidence = result['confidence']
        
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        
        # ── Main Result ───────────────────────────────────────
        section_header("🎯", "Recommendation Result")
        
        res_col1, res_col2 = st.columns([2, 1])
        with res_col1:
            result_display("Recommended Crop", crop_name)
        with res_col2:
            result_display("Confidence", f"{confidence:.1f}%")
        
        # ── Confidence Bar ────────────────────────────────────
        color = "#00ff88" if confidence >= 80 else ("#feca57" if confidence >= 50 else "#ff9f43")
        confidence_bar("Prediction Confidence", confidence, color=color)
        
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        
        # ── Top-5 Results ─────────────────────────────────────
        section_header("🏆", "Top 5 Crop Candidates")
        
        top_preds = result.get('top_predictions', [])
        if top_preds:
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                names = [p[0] for p in top_preds[:5]]
                values = [p[1] for p in top_preds[:5]]
                fig = confidence_bar_chart(names, values, "Crop Probability Ranking")
                st.plotly_chart(fig, use_container_width=True)
            
            with chart_col2:
                fig2 = crop_probability_chart(names, values)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Individual bars
            for name, prob in top_preds[:5]:
                c = "#00ff88" if prob >= 50 else ("#00d4ff" if prob >= 10 else "#4a5a52")
                confidence_bar(name, prob, color=c)
        
        # ── Soil Quality Analysis ─────────────────────────────
        analyzer = load_risk_analyzer()
        if analyzer:
            soil = analyzer.calculate_soil_quality(N, P, K, ph, temperature, humidity, rainfall)
            
            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            section_header("🌍", "Soil Quality Assessment")
            
            sq_col1, sq_col2, sq_col3 = st.columns(3)
            with sq_col1:
                result_display("Soil Score", f"{soil['score']:.0f}/100")
            with sq_col2:
                result_display("Quality Level", soil['level'])
            with sq_col3:
                npk = soil.get('npk_ratio', {})
                ratio_str = npk.get('N:P ratio', 'N/A')
                result_display("N:P Ratio", ratio_str, color="#00d4ff")
            
            # Issues
            issues = soil.get('issues', [])
            if issues:
                with st.expander("⚠️ Soil Issues Identified", expanded=True):
                    for issue in issues:
                        st.markdown(f"- {issue}")
        
        # ── Crop Growing Advice ───────────────────────────────
        recommender = load_recommendation_engine()
        if recommender:
            advice = recommender.get_crop_advice(
                crop_name, N, P, K, temperature, humidity, ph, rainfall)
            
            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            recommendation_card("🌱", f"Growing Advice for {crop_name}", advice)
    else:
        st.error(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
