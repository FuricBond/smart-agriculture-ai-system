"""
Disease Detection Page — Smart Agriculture Dashboard
"""

import os
import streamlit as st
from components.ui import (
    inject_css, page_header, section_header, floating_navbar, theme_toggle,
    confidence_bar, result_display, risk_badge, glass_card,
    recommendation_card,
)
from components.charts import confidence_bar_chart
from utils.model_loader import load_disease_engine, load_risk_analyzer, load_recommendation_engine
from utils.history import add_prediction

st.set_page_config(page_title="Disease Detection — Smart Agri AI", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")
inject_css()
floating_navbar("Disease")
theme_toggle()

# ── Page Header ───────────────────────────────────────────────
page_header("🔬", "Disease Detection", "Upload a leaf image to detect plant diseases using AI")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ── Load Model ────────────────────────────────────────────────
disease_info = load_disease_engine()
engine = disease_info['engine']

if not disease_info['loaded']:
    st.error(f"⚠️ Disease model not available: {disease_info.get('error', 'Unknown error')}")
    st.info("Please ensure the model file exists at `disease_model/models/disease_model.pth`")
    st.stop()

# ── Model Info Badge ──────────────────────────────────────────
st.markdown(f'''
<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:1rem;">
    <span class="status-badge status-active">🧠 ResNet50 CNN</span>
    <span class="status-badge status-active">📦 {disease_info["num_classes"]} Classes</span>
    <span class="status-badge status-active">⏱️ {disease_info["load_time"]}s load</span>
    <span class="status-badge status-active">💾 {disease_info["model_size"]} MB</span>
</div>
''', unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# IMAGE UPLOAD
# ══════════════════════════════════════════════════════════════
col_upload, col_preview = st.columns([1, 1])

with col_upload:
    section_header("📤", "Upload Leaf Image")
    uploaded_file = st.file_uploader(
        "Drag & drop or click to upload",
        type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
        help="Upload a clear photo of a plant leaf for disease analysis"
    )
    
    if uploaded_file:
        st.markdown(f'''
        <div class="glass-card" style="padding:0.8rem;">
            <div style="font-size:0.82rem;color:#8b9a92;">
                📁 <strong>{uploaded_file.name}</strong><br>
                📏 {uploaded_file.size / 1024:.1f} KB &nbsp;•&nbsp; 
                📄 {uploaded_file.type}
            </div>
        </div>
        ''', unsafe_allow_html=True)

with col_preview:
    section_header("🖼️", "Image Preview")
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True, caption="Uploaded Leaf Image")
    else:
        st.markdown('''
        <div class="glass-card" style="text-align:center;padding:3rem 1rem;min-height:250px;
            display:flex;flex-direction:column;align-items:center;justify-content:center;">
            <span style="font-size:3rem;opacity:0.3;">🍃</span>
            <div style="color:#4a5a52;margin-top:0.5rem;">No image uploaded yet</div>
            <div style="color:#4a5a52;font-size:0.78rem;margin-top:0.3rem;">
                Supported: JPG, PNG, BMP, WebP
            </div>
        </div>
        ''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PREDICTION
# ══════════════════════════════════════════════════════════════
if uploaded_file:
    st.divider()
    
    analyze_btn = st.button("🔬  Analyze Disease", use_container_width=True, type="primary")
    
    if analyze_btn:
        with st.spinner(""):
            # Show custom loading
            st.markdown('''
            <div style="text-align:center;padding:1rem;">
                <div class="loading-spinner"></div>
                <div style="color:#8b9a92;font-size:0.85rem;margin-top:0.5rem;">
                    Analyzing leaf image with ResNet50 CNN...
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Save uploaded file temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            
            # Run prediction
            result = engine.predict(tmp_path, top_k=5)
            
            # Clean up
            os.unlink(tmp_path)
        
        if result['success']:
            # Store in history
            add_prediction('disease', {'image': uploaded_file.name}, result)
            
            is_healthy = 'healthy' in result['disease_name'].lower()
            confidence = result['confidence']
            
            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            
            # ── Results ───────────────────────────────────────
            section_header("✅" if is_healthy else "⚠️", "Detection Results")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                result_display("Plant", result['plant'], "#00ff88" if is_healthy else "#ff4757")
            with res_col2:
                result_display("Condition", result['condition'], "#00ff88" if is_healthy else "#ff9f43")
            with res_col3:
                result_display("Confidence", f"{confidence:.1f}%", "#00ff88" if confidence >= 85 else "#feca57")
            
            # ── Health Indicator ──────────────────────────────
            if is_healthy:
                st.markdown('''
                <div class="glass-card animate-fade-in-up" style="text-align:center;
                    border-color:rgba(0,255,136,0.3);padding:1.5rem;">
                    <span style="font-size:3rem;">✅</span>
                    <div style="font-family:'Poppins',sans-serif;font-weight:700;font-size:1.3rem;
                        color:#00ff88;margin-top:0.3rem;">PLANT IS HEALTHY</div>
                    <div style="color:#8b9a92;font-size:0.85rem;">No disease detected — continue regular monitoring</div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="glass-card animate-fade-in-up" style="text-align:center;
                    border-color:rgba(255,71,87,0.3);padding:1.5rem;">
                    <span style="font-size:3rem;">🦠</span>
                    <div style="font-family:'Poppins',sans-serif;font-weight:700;font-size:1.3rem;
                        color:#ff4757;margin-top:0.3rem;">DISEASE DETECTED</div>
                    <div style="color:#ff9f43;font-size:0.95rem;font-weight:600;">
                        {result['condition']}</div>
                    <div style="color:#8b9a92;font-size:0.85rem;margin-top:0.3rem;">
                        Immediate treatment recommended</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # ── Confidence Bar ────────────────────────────────
            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            section_header("📊", "Prediction Confidence")
            
            color = "#00ff88" if confidence >= 85 else ("#feca57" if confidence >= 60 else "#ff4757")
            confidence_bar("Primary Prediction", confidence, color=color)
            
            # ── Top-5 Predictions Chart ───────────────────────
            top_preds = result.get('top_predictions', [])
            if top_preds:
                st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
                section_header("🏆", "Top 5 Predictions")
                
                names = [p[0] for p in top_preds[:5]]
                values = [p[1] for p in top_preds[:5]]
                fig = confidence_bar_chart(names, values, "Disease Predictions")
                st.plotly_chart(fig, use_container_width=True)
            
            # ── Disease Risk Assessment ───────────────────────
            analyzer = load_risk_analyzer()
            if analyzer:
                risk = analyzer.assess_disease_risk(result['disease_name'], confidence)
                
                section_header("⚠️", "Disease Risk Assessment")
                
                risk_col1, risk_col2 = st.columns(2)
                with risk_col1:
                    st.markdown("**Risk Level:**")
                    risk_badge(risk['risk_level'], round(risk['risk_score']))
                with risk_col2:
                    st.markdown(f"**Description:** {risk['description']}")
            
            # ── Treatment Recommendations ─────────────────────
            recommender = load_recommendation_engine()
            if recommender:
                treatments = recommender.get_disease_treatment(
                    result['disease_name'], result['plant'], result['condition'])
                
                st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
                recommendation_card(
                    "💊", "Treatment Recommendations", treatments,
                    color="#00ff88" if is_healthy else "#ff9f43"
                )
        else:
            st.error(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
