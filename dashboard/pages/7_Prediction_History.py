"""
Prediction History Page — Smart Agriculture Dashboard
"""

import streamlit as st
from components.ui import (
    inject_css, page_header, section_header, floating_navbar, theme_toggle,
    glass_card,
)
from utils.history import get_history, clear_history, get_type_icon, get_type_color

st.set_page_config(page_title="Prediction History — Smart Agri AI", page_icon="🕒", layout="wide", initial_sidebar_state="collapsed")
inject_css()
floating_navbar("History")
theme_toggle()

page_header("🕒", "Prediction History", "Review all past AI inferences and system recommendations")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DATA FILTERING & HISTORY
# ══════════════════════════════════════════════════════════════
history = get_history()

if history:
    section_header("📜", "Historical Inferences")
    
    st.markdown(f'''
    <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:0.8rem;">
        Showing last {len(history)} system actions across all models
    </div>
    ''', unsafe_allow_html=True)
    
    # Optional filtering
    types = ["All"] + sorted(list(set([h['type'] for h in history])))
    filter_col, _ = st.columns([1, 4])
    with filter_col:
        selected_type = st.selectbox("Filter by Module", types)
    
    filtered_history = history if selected_type == "All" else [h for h in history if h['type'] == selected_type]
    
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    
    for entry in filtered_history:
        icon = get_type_icon(entry['type'])
        color = get_type_color(entry['type'])
        results = entry.get('results', {})
        parameters = entry.get('parameters', {})
        
        # Build summary and detail
        detail = ""
        if entry['type'] == 'disease':
            summary = f"Detected: {results.get('disease_name', 'N/A')} ({results.get('confidence', 0):.0f}%)"
            detail = f"Image: {parameters.get('image', 'Unknown')} | Plant: {results.get('plant', 'N/A')}"
        elif entry['type'] == 'crop':
            summary = f"Recommended: {results.get('crop_name', 'N/A')} ({results.get('confidence', 0):.0f}%)"
            detail = f"N:{parameters.get('N',0)} | P:{parameters.get('P',0)} | K:{parameters.get('K',0)} | pH:{parameters.get('pH',0)} | Temp:{parameters.get('Temperature',0)}°C"
        elif entry['type'] == 'yield':
            summary = f"Yield: {results.get('predicted_yield', 0):,.0f} ({results.get('yield_level', 'N/A')})"
            detail = f"Area: {parameters.get('area', 'N/A')} | Crop: {parameters.get('crop', 'N/A')} | Year: {parameters.get('year', 'N/A')}"
        elif entry['type'] == 'report':
            summary = f"Farm Grade: {results.get('grade', '?')} — Disease: {results.get('disease', 'None')}"
            detail = f"Crop Rec: {results.get('crop', 'N/A')} | Yield: {results.get('yield', 0):,.0f}"
        else:
            summary = str(results)[:60]
        
        st.markdown(f'''
        <div class="glass-card animate-fade-in-up" style="padding:1.2rem;margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="display:flex;align-items:center;margin-bottom:0.2rem;">
                        <span style="font-size:1.2rem;">{icon}</span>
                        <span style="font-family:var(--font-heading);font-weight:700;color:{color};font-size:0.95rem;margin-left:8px;text-transform:uppercase;">
                            {entry['type']}
                        </span>
                        <span style="color:var(--text-secondary);font-size:0.8rem;margin-left:15px;background:rgba(0,0,0,0.1);padding:2px 8px;border-radius:10px;">
                            {entry['timestamp']}
                        </span>
                    </div>
                    <div style="color:var(--text-primary);font-size:1.05rem;font-weight:600;margin-left:32px;">
                        {summary}
                    </div>
                    <div style="color:var(--text-muted);font-size:0.85rem;margin-left:32px;margin-top:0.3rem;">
                        {detail}
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    if st.button("🗑️ Clear History", type="secondary"):
        clear_history()
        st.rerun()

else:
    section_header("📜", "Historical Inferences")
    st.markdown('''
    <div class="glass-card animate-fade-in-up" style="text-align:center;padding:3rem;">
        <span style="font-size:3rem;opacity:0.3;">📜</span>
        <div style="color:var(--text-secondary);margin-top:1rem;font-size:1.1rem;font-weight:600;">No prediction records available</div>
        <div style="color:var(--text-muted);font-size:0.85rem;margin-top:0.5rem;">
            Records will appear here automatically when you use the models
        </div>
    </div>
    ''', unsafe_allow_html=True)
