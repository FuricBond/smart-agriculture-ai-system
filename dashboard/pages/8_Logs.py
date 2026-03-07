"""
System Logs Viewer — Smart Agriculture Dashboard
"""

import os
import streamlit as st
from components.ui import (
    inject_css, page_header, section_header, floating_navbar, theme_toggle,
    glass_card,
)

st.set_page_config(page_title="System Logs — Smart Agri AI", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")
inject_css()
floating_navbar("Logs")
theme_toggle()

page_header("📝", "System Logs Viewer", "Review raw diagnostic logs and module loading traces")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SYSTEM LOGS VIEWER
# ══════════════════════════════════════════════════════════════
section_header("⚙️", "Diagnostic Logs")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
log_dir = os.path.join(PROJECT_ROOT, 'logs')
log_file = os.path.join(log_dir, 'system_log.txt')

if os.path.isfile(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    log_lines = log_content.strip().split('\n')
    
    # Filter controls
    limit_options = [50, 100, 500, 'All']
    col_filter, col_btn = st.columns([1, 1], gap="large")
    with col_filter:
        limit = st.selectbox("Number of lines to display:", limit_options)
    
    if limit == 'All':
        recent = log_lines
    else:
        recent = log_lines[-limit:] if len(log_lines) > limit else log_lines
        
    st.markdown(f'''
    <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:1rem;">
        📄 <strong>{log_file}</strong><br>
        Total entries: {len(log_lines)} • Showing last {len(recent)}
    </div>
    ''', unsafe_allow_html=True)
    
    st.code('\n'.join(recent), language='yaml')

    with col_btn:
        st.markdown("<div style='height: 1.8rem'></div>", unsafe_allow_html=True)
        st.download_button(
            "📥 Download Raw Logs",
            data=log_content,
            file_name="system_log.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )
else:
    st.info("📝 No log file found. Logs will appear here automatically when the backend operates.")

st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
