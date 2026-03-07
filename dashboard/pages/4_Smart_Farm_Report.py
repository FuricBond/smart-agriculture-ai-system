"""
Smart Farm Report Page — Full Integration Dashboard
"""

import os
import datetime
import tempfile
import streamlit as st
from components.ui import (
    inject_css, page_header, section_header, floating_navbar, theme_toggle,
    result_display, confidence_bar, risk_badge, grade_display,
    glass_card, recommendation_card,
)
from components.charts import (
    confidence_bar_chart, soil_radar_chart, yield_gauge,
    soil_breakdown_chart, health_components_chart,
)
from utils.model_loader import (
    load_disease_engine, load_crop_engine, load_yield_engine,
    load_risk_analyzer, load_recommendation_engine,
)
from utils.history import add_prediction

st.set_page_config(page_title="Smart Farm Report — Smart Agri AI", page_icon="📋", layout="wide", initial_sidebar_state="collapsed")
inject_css()
floating_navbar("Report")
theme_toggle()

page_header("📋", "Smart Farm Report", "Complete farm analysis using all AI models — Disease + Crop + Yield")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
st.divider()

# ══════════════════════════════════════════════════════════════
# INPUTS — ALL THREE MODULES
# ══════════════════════════════════════════════════════════════
section_header("📥", "Input Data")

tab1, tab2, tab3 = st.tabs(["🔬 Disease Image", "🌱 Soil & Weather", "📊 Yield Parameters"])

with tab1:
    uploaded_file = st.file_uploader(
        "Upload leaf image for disease detection",
        type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
        key='report_image'
    )
    if uploaded_file:
        col_img1, col_img2 = st.columns([1, 2])
        with col_img1:
            st.image(uploaded_file, use_container_width=True, caption="Leaf Image")
        with col_img2:
            st.markdown(f'''
            <div class="glass-card">
                <div style="font-size:0.85rem;color:#8b9a92;">
                    📁 {uploaded_file.name}<br>
                    📏 {uploaded_file.size/1024:.1f} KB &nbsp;•&nbsp; {uploaded_file.type}
                </div>
            </div>
            ''', unsafe_allow_html=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        N = st.slider("Nitrogen (N, kg/ha)", 0, 200, 80, key='r_n')
        P = st.slider("Phosphorus (P, kg/ha)", 0, 150, 48, key='r_p')
        K = st.slider("Potassium (K, kg/ha)", 0, 250, 40, key='r_k')
        ph = st.slider("pH Level", 0.0, 14.0, 6.5, 0.1, key='r_ph')
    with c2:
        temperature = st.slider("Temperature (°C)", -5, 55, 25, key='r_temp')
        humidity = st.slider("Humidity (%)", 0, 100, 75, key='r_hum')
        rainfall = st.slider("Rainfall (mm)", 0, 3000, 200, key='r_rain')

with tab3:
    yield_info = load_yield_engine()
    y_engine = yield_info['engine'] if yield_info['loaded'] else None
    
    c1, c2, c3 = st.columns(3)
    with c1:
        areas = yield_info.get('known_areas', [])
        if areas:
            area = st.selectbox("Area", areas, index=areas.index("India") if "India" in areas else 0, key='r_area')
        else:
            area = st.text_input("Area", "India", key='r_area')
    with c2:
        crops = yield_info.get('known_crops', [])
        if crops:
            crop = st.selectbox("Crop", crops, index=crops.index("Rice") if "Rice" in crops else 0, key='r_crop')
        else:
            crop = st.text_input("Crop", "Rice", key='r_crop')
    with c3:
        year = st.slider("Year", 1990, 2030, 2024, key='r_year')

st.divider()

# ══════════════════════════════════════════════════════════════
# GENERATE REPORT
# ══════════════════════════════════════════════════════════════
generate_btn = st.button("⚡  Generate Smart Farm Report", use_container_width=True, type="primary")

if generate_btn:
    progress = st.progress(0)
    status_text = st.empty()
    
    # Initialize results
    disease_result = {'success': False, 'error': 'No image provided'}
    crop_result = {'success': False}
    yield_result = {'success': False}
    
    # ── Step 1: Disease Detection ─────────────────────────────
    status_text.markdown("🔬 **Step 1/4:** Running disease detection...")
    progress.progress(10)
    
    disease_info = load_disease_engine()
    if disease_info['loaded'] and uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name
        disease_result = disease_info['engine'].predict(tmp_path, top_k=5)
        os.unlink(tmp_path)
    
    progress.progress(30)
    
    # ── Step 2: Crop Recommendation ───────────────────────────
    status_text.markdown("🌱 **Step 2/4:** Getting crop recommendation...")
    
    crop_info = load_crop_engine()
    if crop_info['loaded']:
        crop_result = crop_info['engine'].predict(N, P, K, temperature, humidity, ph, rainfall)
    
    progress.progress(50)
    
    # ── Step 3: Yield Prediction ──────────────────────────────
    status_text.markdown("📊 **Step 3/4:** Predicting yield...")
    
    if yield_info['loaded'] and y_engine:
        yield_result = y_engine.predict(area, crop, year)
    
    progress.progress(70)
    
    # ── Step 4: Analysis ──────────────────────────────────────
    status_text.markdown("🧠 **Step 4/4:** Running risk analysis & generating recommendations...")
    
    analyzer = load_risk_analyzer()
    recommender = load_recommendation_engine()
    
    # Risk Analysis
    soil_quality = {}
    disease_risk = {'risk_level': 'MODERATE', 'risk_score': 50, 'description': 'N/A'}
    yield_classification = {'level': 'MEDIUM', 'description': 'N/A'}
    overall_health = {'overall_grade': '?', 'overall_score': 0, 'summary': 'N/A', 'components': {}}
    
    if analyzer:
        soil_quality = analyzer.calculate_soil_quality(N, P, K, ph, temperature, humidity, rainfall)
        
        if disease_result.get('success'):
            disease_risk = analyzer.assess_disease_risk(
                disease_result['disease_name'], disease_result['confidence'])
        
        if yield_result.get('success'):
            yield_classification = analyzer.classify_yield(yield_result['predicted_yield'])
        
        overall_health = analyzer.compute_overall_health(
            soil_quality, disease_risk, yield_classification)
    
    # Recommendations
    treatments = ['Provide a leaf image for disease-specific advice']
    crop_advice = ['Enter soil parameters for recommendations']
    yield_advice = ['Enter yield data for improvement advice']
    combined_advisory = []
    
    if recommender:
        if disease_result.get('success'):
            treatments = recommender.get_disease_treatment(
                disease_result['disease_name'], disease_result['plant'], disease_result['condition'])
        
        if crop_result.get('success'):
            crop_advice = recommender.get_crop_advice(
                crop_result['crop_name'], N, P, K, temperature, humidity, ph, rainfall)
        
        if yield_result.get('success'):
            yield_advice = recommender.get_yield_advice(
                yield_classification['level'], yield_result['predicted_yield'], crop)
        
        combined_advisory = recommender.get_combined_advisory(
            disease_result, crop_result, yield_result, soil_quality, disease_risk)
    
    # Save to history
    add_prediction('report', {
        'image': uploaded_file.name if uploaded_file else 'None',
        'N': N, 'P': P, 'K': K, 'area': area, 'crop': crop, 'year': year
    }, {
        'disease': disease_result.get('disease_name', 'N/A'),
        'crop': crop_result.get('crop_name', 'N/A'),
        'yield': yield_result.get('predicted_yield', 0),
        'grade': overall_health.get('overall_grade', '?'),
    })
    
    progress.progress(100)
    status_text.empty()
    progress.empty()
    
    # ══════════════════════════════════════════════════════════
    # DISPLAY REPORT
    # ══════════════════════════════════════════════════════════
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    # ── Overall Health Grade ──────────────────────────────────
    grade_display(
        overall_health.get('overall_grade', '?'),
        overall_health.get('overall_score', 0),
        overall_health.get('summary', '')
    )
    
    # Health components chart
    components = overall_health.get('components', {})
    if components:
        fig = health_components_chart(components)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ── Disease Results ───────────────────────────────────────
    section_header("🔬", "Disease Detection")
    if disease_result.get('success'):
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            result_display("Plant", disease_result['plant'])
        with dc2:
            is_h = 'healthy' in disease_result['disease_name'].lower()
            result_display("Condition", disease_result['condition'],
                          "#00ff88" if is_h else "#ff4757")
        with dc3:
            result_display("Confidence", f"{disease_result['confidence']:.1f}%")
        
        # Risk badge
        st.markdown("**Disease Risk:**")
        risk_badge(disease_risk['risk_level'], round(disease_risk.get('risk_score', 0)))
        
        # Top predictions
        top_p = disease_result.get('top_predictions', [])
        if top_p:
            fig = confidence_bar_chart(
                [p[0] for p in top_p[:5]], [p[1] for p in top_p[:5]],
                "Disease Predictions"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Disease detection skipped — no image provided")
    
    st.divider()
    
    # ── Crop Results ──────────────────────────────────────────
    section_header("🌱", "Crop Recommendation")
    if crop_result.get('success'):
        cc1, cc2 = st.columns(2)
        with cc1:
            result_display("Recommended Crop", crop_result['crop_name'])
        with cc2:
            result_display("Confidence", f"{crop_result['confidence']:.1f}%")
        
        # Radar chart
        fig = soil_radar_chart(N, P, K, temperature, humidity, ph, rainfall)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Crop recommendation failed")
    
    st.divider()
    
    # ── Yield Results ─────────────────────────────────────────
    section_header("📊", "Yield Prediction")
    if yield_result.get('success'):
        yc1, yc2, yc3 = st.columns(3)
        with yc1:
            result_display("Predicted Yield", f"{yield_result['predicted_yield']:,.2f}")
        with yc2:
            result_display("Yield Level", yield_classification['level'])
        with yc3:
            result_display("Region", area, color="#00d4ff")
        
        fig = yield_gauge(yield_result['predicted_yield'], f"Yield — {crop}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"⚠️ Yield prediction: {yield_result.get('error', 'Failed')}")
    
    st.divider()
    
    # ── Soil Quality ──────────────────────────────────────────
    if soil_quality:
        section_header("🌍", "Soil Quality Analysis")
        
        sc1, sc2 = st.columns(2)
        with sc1:
            result_display("Soil Score", f"{soil_quality.get('score', 0):.0f}/100")
        with sc2:
            result_display("Quality", soil_quality.get('level', 'N/A'))
        
        breakdown = soil_quality.get('breakdown', {})
        if breakdown:
            fig = soil_breakdown_chart(breakdown)
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ── Recommendations ───────────────────────────────────────
    section_header("💡", "Smart Recommendations")
    
    # Cross-module advisory
    if combined_advisory:
        glass_card(f'''
        <div style="margin-bottom:0.5rem;">
            <span style="font-family:'Poppins',sans-serif;font-weight:700;color:#a855f7;font-size:1rem;">
                🧠 Intelligent Cross-Module Advisory
            </span>
        </div>
        <ul style="padding-left:1.2rem;margin:0;">
            {''.join(f'<li style="color:#c0c8c4;font-size:0.85rem;margin-bottom:6px;line-height:1.5;">{a}</li>' for a in combined_advisory)}
        </ul>
        ''')
    
    rec_col1, rec_col2, rec_col3 = st.columns(3)
    with rec_col1:
        recommendation_card("💊", "Disease Treatment", treatments, color="#ff9f43")
    with rec_col2:
        recommendation_card("🌱", "Crop Advice", crop_advice, color="#00ff88")
    with rec_col3:
        recommendation_card("📊", "Yield Strategy", yield_advice, color="#00d4ff")
    
    # ── Download Report ───────────────────────────────────────
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    section_header("📥", "Export Report")
    
    # Build text report
    report_lines = [
        "=" * 60,
        "SMART FARM REPORT",
        f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        "=" * 60,
        "",
        f"Overall Grade: {overall_health.get('overall_grade', '?')} ({overall_health.get('overall_score', 0):.0f}/100)",
        f"Summary: {overall_health.get('summary', 'N/A')}",
        "",
        "--- DISEASE DETECTION ---",
        f"Plant: {disease_result.get('plant', 'N/A')}",
        f"Condition: {disease_result.get('condition', 'N/A')}",
        f"Confidence: {disease_result.get('confidence', 0):.1f}%",
        f"Risk Level: {disease_risk.get('risk_level', 'N/A')}",
        "",
        "--- CROP RECOMMENDATION ---",
        f"Recommended: {crop_result.get('crop_name', 'N/A')}",
        f"Confidence: {crop_result.get('confidence', 0):.1f}%",
        "",
        "--- YIELD PREDICTION ---",
        f"Area: {area}",
        f"Crop: {crop}",
        f"Year: {year}",
        f"Predicted Yield: {yield_result.get('predicted_yield', 0):,.2f}",
        f"Level: {yield_classification.get('level', 'N/A')}",
        "",
        "--- SOIL QUALITY ---",
        f"Score: {soil_quality.get('score', 0):.0f}/100",
        f"Level: {soil_quality.get('level', 'N/A')}",
        "",
        "--- RECOMMENDATIONS ---",
    ]
    for t in treatments[:5]:
        report_lines.append(f"  • {t}")
    report_lines.append("")
    for a in crop_advice[:5]:
        report_lines.append(f"  • {a}")
    report_lines.append("")
    for y in yield_advice[:5]:
        report_lines.append(f"  • {y}")
    report_lines.append("")
    report_lines.append("=" * 60)
    
    report_text = "\n".join(report_lines)
    
    # Save to dashboard/reports
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(reports_dir, f"smart_farm_report_{ts}.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            "📥  Download Report (TXT)",
            data=report_text,
            file_name=f"smart_farm_report_{ts}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl_col2:
        st.success(f"✅ Auto-saved to `dashboard/reports/`")
