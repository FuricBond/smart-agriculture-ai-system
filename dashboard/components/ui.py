"""
UI Components — Ultra Elite AI Dashboard
================================================
Reusable visual components for the Streamlit dashboard.
All components inject custom HTML with CSS classes from main.css.
"""

import os
import streamlit as st

def inject_css():
    """Inject the custom CSS stylesheet and handle light/dark mode."""
    css_path = os.path.join(os.path.dirname(__file__), '..', 'styles', 'main.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        
        # Inject base CSS
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

        # Handle Light/Dark Mode Overrides
        theme = st.session_state.get('theme_toggle', False) # False = Dark, True = Light
        if theme:
            light_css = """
            <style>
            :root {
                --bg-primary:     #f0f4f2;
                --bg-secondary:   #ffffff;
                --bg-card:        rgba(255, 255, 255, 0.85);
                --bg-card-hover:  rgba(255, 255, 255, 0.95);
                --text-primary:   #060b09;
                --text-secondary: #4a5a52;
                --text-muted:     #8b9a92;
                --border-glow:    rgba(0, 0, 0, 0.1);
                --border-hover:   rgba(0, 255, 136, 0.4);
                --shadow-glow:    0 8px 30px rgba(0, 0, 0, 0.05);
                --shadow-hover:   0 12px 40px rgba(0, 255, 136, 0.2);
                --nav-bg:         rgba(255, 255, 255, 0.8);
            }
            .stApp::before {
                background:
                    radial-gradient(ellipse at 20% 50%, rgba(0,255,136,0.1) 0%, transparent 40%),
                    radial-gradient(ellipse at 80% 20%, rgba(0,212,255,0.1) 0%, transparent 40%);
            }
            .hero-subtitle, .stat-label, .feature-desc, .result-label {
                color: var(--text-secondary) !important;
            }
            </style>
            """
            st.markdown(light_css, unsafe_allow_html=True)


def floating_navbar(active_page="Home"):
    """Render a native Streamlit floating navigation bar."""
    st.markdown('''
    <style>
    /* Target ONLY the floating nav container using :has() */
    [data-testid="stHorizontalBlock"]:has(.nav-anchor) {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--nav-bg);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid var(--border-glow);
        border-radius: 50px;
        padding: 5px 25px;
        z-index: 999999;
        box-shadow: 0 10px 40px rgba(0,255,136,0.1);
        width: fit-content;
        gap: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Style Page Links inside the block */
    [data-testid="stHorizontalBlock"]:has(.nav-anchor) [data-testid="stPageLink-NavLink"] {
        text-decoration: none;
        color: var(--text-secondary);
        font-weight: 600;
        font-family: var(--font-body);
        padding: 4px 10px;
        border-radius: 20px;
        transition: var(--transition);
        background: transparent;
    }
    [data-testid="stHorizontalBlock"]:has(.nav-anchor) [data-testid="stPageLink-NavLink"]:hover {
        color: var(--accent-green);
        background: rgba(0,255,136,0.1);
    }
    
    /* Hide the default sidebar completely */
    [data-testid="stSidebar"] { display: none !important; }
    </style>
    ''', unsafe_allow_html=True)
    
    cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1], gap="small")
    with cols[0]: 
        st.markdown('<div class="nav-anchor" style="display:none;"></div>', unsafe_allow_html=True)
        st.page_link("app.py", label="Home", icon="🏠")
    with cols[1]: st.page_link("pages/1_Disease_Detection.py", label="Disease", icon="🔬")
    with cols[2]: st.page_link("pages/2_Crop_Recommendation.py", label="Crop", icon="🌱")
    with cols[3]: st.page_link("pages/3_Yield_Prediction.py", label="Yield", icon="📊")
    with cols[4]: st.page_link("pages/4_Smart_Farm_Report.py", label="Report", icon="📋")
    with cols[5]: st.page_link("pages/5_System_Status.py", label="Status", icon="⚙️")
    with cols[6]: st.page_link("pages/7_Prediction_History.py", label="History", icon="🕒")
    with cols[7]: st.page_link("pages/8_Logs.py", label="Logs", icon="📝")


def particles_background():
    """Inject subtle animated particle background with glowing dots."""
    particles_html = '<div class="particles-bg">'
    import random
    for i in range(25):
        x = random.randint(0, 100)
        size = random.uniform(2, 6)
        duration = random.uniform(10, 20)
        delay = random.uniform(0, 5)
        opacity = random.uniform(0.3, 0.8)
        color = random.choice(['#00ff88', '#00d4ff', '#a855f7'])
        particles_html += (
            f'<div class="particle" style="left:{x}%;width:{size}px;height:{size}px;'
            f'background:{color};box-shadow:0 0 {size*2}px {color};'
            f'animation-duration:{duration}s;animation-delay:{delay}s;'
            f'opacity:{opacity};"></div>'
        )
    particles_html += '</div>'
    st.markdown(particles_html, unsafe_allow_html=True)


def theme_toggle():
    """Render a clean theme toggle switch."""
    col1, col2 = st.columns([8, 1])
    with col2:
        st.toggle("☀️ Light Mode", key="theme_toggle")


def hero_section(title="SMART AGRICULTURE AI PLATFORM",
                 subtitle="Ultra-Elite Crop Intelligence System",
                 version="v3.0.0"):
    """Render the hero section with gradient title."""
    st.markdown(f'''
    <div class="hero-container">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle animate-fade-in-up" style="animation-delay: 0.2s;">{subtitle}</div>
        <div class="hero-version animate-fade-in-up" style="animation-delay: 0.4s;">{version} — Artificial Intelligence Core</div>
    </div>
    ''', unsafe_allow_html=True)


def page_header(icon, title, subtitle=""):
    """Render a styled page header."""
    sub_html = f'<div class="page-header-subtitle">{subtitle}</div>' if subtitle else ''
    st.markdown(f'''
    <div class="page-header animate-fade-in-up">
        <span class="page-header-icon">{icon}</span>
        <div class="page-header-title">{title}</div>
        {sub_html}
    </div>
    ''', unsafe_allow_html=True)


def section_header(icon, title):
    """Render a section header with decorative line."""
    st.markdown(f'''
    <div class="section-header animate-fade-in-up">
        {icon} {title}
        <div class="section-header-line"></div>
    </div>
    ''', unsafe_allow_html=True)


def glass_card(content, extra_class=""):
    """Wrap content as a generic glass card."""
    st.markdown(f'''
    <div class="glass-card {extra_class} animate-fade-in-up">
        {content}
    </div>
    ''', unsafe_allow_html=True)


def stat_card(icon, value, label):
    """Render a stat card with icon, value, and label."""
    st.markdown(f'''
    <div class="stat-card animate-fade-in-up">
        <span class="stat-icon">{icon}</span>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    ''', unsafe_allow_html=True)


def feature_card(icon, title, description):
    """Render a feature card with hover effect."""
    st.markdown(f'''
    <div class="feature-card animate-fade-in-up">
        <span class="feature-icon">{icon}</span>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    ''', unsafe_allow_html=True)


def status_indicator(name, loaded, load_time=0, model_size=0, detail=""):
    """Render a model status indicator row."""
    if loaded:
        badge = '<span class="status-badge status-active"><span class="glow-dot glow-dot-green"></span> Active</span>'
        info = f'{model_size} MB &nbsp;•&nbsp; {load_time}s'
    else:
        badge = '<span class="status-badge status-error"><span class="glow-dot glow-dot-red"></span> Offline</span>'
        info = 'Not available'
    
    detail_html = f'<span style="color:var(--text-secondary);font-size:0.75rem;margin-left:8px">{detail}</span>' if detail else ''
    
    st.markdown(f'''
    <div class="glass-card animate-fade-in-up" style="padding:1.2rem 1.6rem;margin-bottom:0.8rem;display:flex;align-items:center;justify-content:space-between;">
        <div>
            <span style="font-weight:700;color:var(--text-primary);font-family:var(--font-heading);font-size:1.05rem;">{name}</span>
            {detail_html}
        </div>
        <div style="display:flex;align-items:center;gap:15px;">
            <span style="color:var(--text-secondary);font-size:0.85rem;font-weight:500;">{info}</span>
            {badge}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def result_display(label, value, color="#00ff88"):
    """Render a result value with large gradient text."""
    st.markdown(f'''
    <div class="result-card animate-fade-in-up">
        <div class="result-label">{label}</div>
        <div class="result-value" style="background:linear-gradient(135deg, {color}, #00d4ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            {value}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def confidence_bar(label, value, max_val=100, color="#00ff88"):
    """Render an animated confidence bar."""
    pct = min(100, (value / max_val) * 100) if max_val > 0 else 0
    st.markdown(f'''
    <div style="margin:0.6rem 0;" class="animate-fade-in-up">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="font-size:0.85rem;color:var(--text-secondary);font-family:var(--font-body);font-weight:600;">{label}</span>
            <span style="font-size:0.85rem;color:{color};font-weight:800;">{value:.1f}%</span>
        </div>
        <div class="confidence-bar-container">
            <div class="confidence-bar-fill" style="width:{pct}%;background:linear-gradient(90deg, {color}, #00d4ff);">
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def risk_badge(level, score=None):
    """Render a risk level badge with appropriate color."""
    colors = {
        'LOW': ('#00ff88', 'rgba(0,255,136,0.1)'),
        'MODERATE': ('#feca57', 'rgba(254,202,87,0.1)'),
        'HIGH': ('#ff9f43', 'rgba(255,159,67,0.1)'),
        'CRITICAL': ('#ff4757', 'rgba(255,71,87,0.1)'),
    }
    color, bg = colors.get(level, ('var(--text-secondary)', 'rgba(0,0,0,0.1)'))
    score_text = f' ({score}/100)' if score is not None else ''
    st.markdown(f'''
    <span style="display:inline-flex;align-items:center;gap:6px;padding:8px 20px;
        border-radius:30px;font-size:0.9rem;font-weight:800;font-family:var(--font-body);
        background:{bg};color:{color};border:1px solid {color}40;box-shadow:0 4px 15px {color}20;">
        {level}{score_text}
    </span>
    ''', unsafe_allow_html=True)


def grade_display(grade, score, summary):
    """Render the overall farm health grade."""
    grade_colors = {
        'A': '#00ff88', 'B': '#00d4ff', 'C': '#feca57',
        'D': '#ff9f43', 'F': '#ff4757'
    }
    color = grade_colors.get(grade, 'var(--text-secondary)')
    st.markdown(f'''
    <div class="glass-card animate-fade-in-up" style="text-align:center;padding:3rem 2rem;">
        <div style="font-size:0.95rem;color:var(--text-secondary);text-transform:uppercase;letter-spacing:3px;
            margin-bottom:1rem;font-weight:700;">Overall Farm Health</div>
        <div style="font-family:var(--font-heading);font-size:5.5rem;font-weight:900;
            color:{color};line-height:1;margin-bottom:0.5rem;
            text-shadow:0 0 50px {color}60;">{grade}</div>
        <div style="font-size:1.5rem;color:{color};font-weight:800;
            font-family:var(--font-heading);">{score}/100</div>
        <div style="font-size:1rem;color:var(--text-muted);margin-top:1rem;font-weight:500;">{summary}</div>
    </div>
    ''', unsafe_allow_html=True)


def architecture_diagram():
    """Render the system architecture flow diagram."""
    st.markdown('''
    <div class="arch-flow animate-fade-in-up">
        <div class="arch-node">
            <span class="arch-node-icon">📷</span>
            <div class="arch-node-label">Leaf Image</div>
        </div>
        <span class="arch-arrow">→</span>
        <div class="arch-node">
            <span class="arch-node-icon">🧠</span>
            <div class="arch-node-label">Disease AI</div>
        </div>
        <span class="arch-arrow">→</span>
        <div class="arch-node" style="border-color:#00ff88;box-shadow:0 0 20px rgba(0,255,136,0.15);">
            <span class="arch-node-icon">⚡</span>
            <div class="arch-node-label" style="color:#00ff88;font-weight:700;">Smart Engine</div>
        </div>
        <span class="arch-arrow">←</span>
        <div class="arch-node">
            <span class="arch-node-icon">🌱</span>
            <div class="arch-node-label">Crop AI</div>
        </div>
        <span class="arch-arrow">←</span>
        <div class="arch-node">
            <span class="arch-node-icon">📊</span>
            <div class="arch-node-label">Yield AI</div>
        </div>
        <span class="arch-arrow">→</span>
        <div class="arch-node">
            <span class="arch-node-icon">📋</span>
            <div class="arch-node-label">Report</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def recommendation_card(icon, title, items, color="#00ff88"):
    """Render a recommendation list card."""
    list_html = ""
    for item in items[:6]:
        list_html += f'<li style="margin-bottom:10px;color:var(--text-secondary);font-size:0.9rem;font-weight:500;line-height:1.6;">{item}</li>'
    
    st.markdown(f'''
    <div class="glass-card animate-fade-in-up">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1.2rem;">
            <span style="font-size:1.5rem;">{icon}</span>
            <span style="font-family:var(--font-heading);font-weight:700;font-size:1.15rem;color:{color};">
                {title}
            </span>
        </div>
        <ul style="padding-left:1.5rem;margin:0;">{list_html}</ul>
    </div>
    ''', unsafe_allow_html=True)
