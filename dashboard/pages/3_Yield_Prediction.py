"""
Yield Prediction Page — Smart Agriculture Dashboard
"""

import streamlit as st
from components.ui import (
    inject_css, page_header, section_header, floating_navbar, theme_toggle,
    result_display, risk_badge, glass_card, recommendation_card,
)
from components.charts import yield_gauge, yield_trend_chart
from utils.model_loader import load_yield_engine, load_risk_analyzer, load_recommendation_engine
from utils.history import add_prediction

st.set_page_config(page_title="Yield Prediction — Smart Agri AI", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")
inject_css()
floating_navbar("Yield")
theme_toggle()

page_header("📊", "Yield Prediction", "Predict crop yield using AI and historical data analysis")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ── Load Model ────────────────────────────────────────────────
yield_info = load_yield_engine()
engine = yield_info['engine']

if not yield_info['loaded']:
    st.error(f"⚠️ Yield model not available: {yield_info.get('error', 'Unknown error')}")
    st.stop()

areas = yield_info.get('known_areas', [])
crops = yield_info.get('known_crops', [])

# Model info badges
st.markdown(f'''
<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:1rem;">
    <span class="status-badge status-active">🧠 RandomForest</span>
    <span class="status-badge status-active">🌍 {len(areas)} Regions</span>
    <span class="status-badge status-active">🌾 {len(crops)} Crops</span>
    <span class="status-badge status-active">⏱️ {yield_info["load_time"]}s load</span>
</div>
''', unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# INPUT PARAMETERS
# ══════════════════════════════════════════════════════════════
section_header("📋", "Prediction Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('''
    <div class="glass-card" style="padding:0.8rem;">
        <div style="font-family:'Poppins',sans-serif;font-weight:600;color:#00ff88;font-size:0.85rem;">
            🌍 Geographic Region
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if areas:
        selected_area = st.selectbox("Select Area", areas, index=areas.index("India") if "India" in areas else 0)
    else:
        selected_area = st.text_input("Enter Area", "India")

with col2:
    st.markdown('''
    <div class="glass-card" style="padding:0.8rem;">
        <div style="font-family:'Poppins',sans-serif;font-weight:600;color:#00d4ff;font-size:0.85rem;">
            🌾 Crop Selection
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    if crops:
        selected_crop = st.selectbox("Select Crop", crops, index=crops.index("Rice") if "Rice" in crops else 0)
    else:
        selected_crop = st.text_input("Enter Crop", "Rice")

with col3:
    st.markdown('''
    <div class="glass-card" style="padding:0.8rem;">
        <div style="font-family:'Poppins',sans-serif;font-weight:600;color:#a855f7;font-size:0.85rem;">
            📅 Prediction Year
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    selected_year = st.slider("Select Year", 1990, 2030, 2024)

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PREDICTION
# ══════════════════════════════════════════════════════════════
predict_btn = st.button("📊  Predict Yield", use_container_width=True, type="primary")

if predict_btn:
    with st.spinner(""):
        st.markdown('''
        <div style="text-align:center;padding:1rem;">
            <div class="loading-spinner"></div>
            <div style="color:#8b9a92;font-size:0.85rem;margin-top:0.5rem;">
                Predicting yield with RandomForest model...
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        result = engine.predict(selected_area, selected_crop, selected_year)
    
    if result['success']:
        predicted_yield = result['predicted_yield']
        yield_level = result.get('yield_level', 'MEDIUM')
        
        # Save to history
        add_prediction('yield', {
            'area': selected_area, 'crop': selected_crop, 'year': selected_year
        }, result)
        
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        
        # ── Main Results ──────────────────────────────────────
        section_header("🎯", "Prediction Results")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        with res_col1:
            result_display("Predicted Yield", f"{predicted_yield:,.2f}")
        with res_col2:
            color = "#00ff88" if yield_level == "HIGH" else ("#feca57" if yield_level == "MEDIUM" else "#ff4757")
            result_display("Yield Level", yield_level, color=color)
        with res_col3:
            result_display("Region", selected_area, color="#00d4ff")
        
        # ── Yield Gauge ───────────────────────────────────────
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        section_header("🎯", "Yield Gauge")
        
        fig = yield_gauge(predicted_yield, f"Yield — {selected_crop}")
        st.plotly_chart(fig, use_container_width=True)
        
        # ── Yield Level Indicator ─────────────────────────────
        level_colors = {'LOW': '#ff4757', 'MEDIUM': '#feca57', 'HIGH': '#00ff88'}
        lc = level_colors.get(yield_level, '#8b9a92')
        
        st.markdown(f'''
        <div class="glass-card animate-fade-in-up" style="text-align:center;">
            <div style="font-size:0.85rem;color:#8b9a92;text-transform:uppercase;
                letter-spacing:2px;margin-bottom:0.3rem;">Yield Classification</div>
            <div style="font-family:'Poppins',sans-serif;font-size:2rem;font-weight:800;
                color:{lc};text-shadow:0 0 20px {lc}40;">
                {'📈 HIGH YIELD' if yield_level == 'HIGH' else ('📊 MEDIUM YIELD' if yield_level == 'MEDIUM' else '📉 LOW YIELD')}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # ── Trend Chart ───────────────────────────────────────
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        section_header("📈", "Yield Trend Analysis")
        
        st.markdown('''
        <div style="font-size:0.82rem;color:#4a5a52;margin-bottom:0.5rem;">
            Generating yield predictions across multiple years...
        </div>
        ''', unsafe_allow_html=True)
        
        # Generate trend data
        years_range = list(range(selected_year - 8, selected_year + 3))
        trend_yields = []
        for y in years_range:
            r = engine.predict(selected_area, selected_crop, y)
            if r['success']:
                trend_yields.append(r['predicted_yield'])
            else:
                trend_yields.append(0)
        
        if any(v > 0 for v in trend_yields):
            fig_trend = yield_trend_chart(
                years_range, trend_yields,
                area=selected_area, crop=selected_crop
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # ── Yield Classification ──────────────────────────────
        analyzer = load_risk_analyzer()
        if analyzer:
            classification = analyzer.classify_yield(predicted_yield)
            
            with st.expander("📊 Detailed Yield Classification", expanded=False):
                st.markdown(f"**Level:** {classification['level']}")
                st.markdown(f"**Description:** {classification['description']}")
                st.markdown(f"**Position:** {classification.get('percentile', 'N/A')}")
        
        # ── Yield Advice ──────────────────────────────────────
        recommender = load_recommendation_engine()
        if recommender:
            advice = recommender.get_yield_advice(yield_level, predicted_yield, selected_crop)
            
            st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
            recommendation_card("📊", "Yield Improvement Advice", advice)
    
    else:
        st.error(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
        
        suggestions = result.get('suggestions', [])
        if suggestions:
            st.markdown("**💡 Did you mean?**")
            for s in suggestions[:5]:
                st.markdown(f"- {s}")
