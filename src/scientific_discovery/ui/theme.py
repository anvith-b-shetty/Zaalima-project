"""
Unified UI/UX Design System for Autonomous Scientific Discovery Agent.

Provides centralized CSS styles, typography, color palettes, animations,
and reusable modern HTML component renderers for Streamlit.
"""

import textwrap

# Color Palette Tokens
COLORS = {
    "primary": "#4f46e5",       # Indigo 600
    "primary_dark": "#3730a3",  # Indigo 800
    "primary_light": "#818cf8", # Indigo 400
    "accent_cyan": "#0ea5e9",   # Sky 500
    "accent_violet": "#8b5cf6", # Purple 500
    "success": "#10b981",       # Emerald 500
    "success_bg": "#ecfdf5",
    "warning": "#f59e0b",       # Amber 500
    "warning_bg": "#fffbeb",
    "danger": "#ef4444",        # Rose 500
    "danger_bg": "#fef2f2",
    "neutral_dark": "#0f172a",  # Slate 900
    "neutral_slate": "#334155", # Slate 700
    "neutral_muted": "#64748b", # Slate 500
    "neutral_light": "#f8fafc", # Slate 50
    "border_subtle": "#e2e8f0", # Slate 200
    "card_bg": "#ffffff",
}

# Global Custom CSS (Clean without extra indentation)
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stText {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1e293b;
}

@keyframes pulse-halo {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.live-pulse {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background-color: #10b981;
    animation: pulse-halo 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
    margin-right: 6px;
    vertical-align: middle;
}

.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 3.5rem;
    max-width: 1300px;
}

.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 45%, #0f172a 100%);
    border-radius: 16px;
    padding: 26px 30px;
    color: #ffffff;
    box-shadow: 0 10px 30px -8px rgba(15, 23, 42, 0.35);
    margin-bottom: 24px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    position: relative;
    overflow: hidden;
}

.hero-title {
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    background: linear-gradient(90deg, #ffffff 0%, #e2e8f0 60%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.hero-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    margin-top: 6px;
    margin-bottom: 16px;
    font-weight: 500;
}

.hero-chips-bar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
}

.chip {
    display: inline-flex;
    align-items: center;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 9999px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #e2e8f0;
    backdrop-filter: blur(8px);
}

.chip-online {
    background: rgba(16, 185, 129, 0.16);
    border-color: rgba(16, 185, 129, 0.4);
    color: #34d399;
}

.chip-accent {
    background: rgba(99, 102, 241, 0.2);
    border-color: rgba(129, 140, 248, 0.4);
    color: #a5b4fc;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #f1f5f9;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
    font-size: 0.88rem;
    color: #64748b;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    background-color: transparent;
    border: none !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #0f172a;
    background-color: rgba(255, 255, 255, 0.7);
}

.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #4f46e5 !important;
    box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.1), 0 1px 3px -1px rgba(15, 23, 42, 0.06) !important;
}

div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px -4px rgba(15, 23, 42, 0.08);
}

div[data-testid="stMetricLabel"] {
    font-size: 0.78rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

div[data-testid="stMetricValue"] {
    font-weight: 800;
    color: #0f172a;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.45rem;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.88rem;
    letter-spacing: -0.01em;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid #cbd5e1;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    border-color: #818cf8;
}

.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
    color: #ffffff;
    border: none;
    box-shadow: 0 2px 6px rgba(79, 70, 229, 0.3);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
}

div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background-color: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    margin-bottom: 12px;
}

section[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}

pre code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
}
</style>
"""


def render_page_header(
    title: str = "Autonomous Multimodal Scientific Discovery",
    subtitle: str = "Enterprise Supervisor Command Hub · Multi-Agent Verification · Real-Time Telemetry & Reporting",
) -> str:
    """Returns clean HTML for the global hero banner with zero markdown code-block indentation."""
    html = f"""<div class="hero-banner">
<h1 class="hero-title">
<span>🔬</span>
<span>{title}</span>
</h1>
<div class="hero-subtitle">{subtitle}</div>
<div class="hero-chips-bar">
<div class="chip chip-online"><span class="live-pulse"></span>Discovery Cluster Online</div>
<div class="chip chip-accent">⚡ 5-Agent Pipeline Active</div>
<div class="chip">🛡️ Docker Sandbox Hardened</div>
<div class="chip">📊 Supervisor Live Monitoring</div>
</div>
</div>"""
    return html


def render_section_header(title: str, subtitle: str, icon: str = "") -> str:
    """Returns clean HTML for a section header."""
    icon_html = f"<span style='font-size: 1.35rem;'>{icon}</span>" if icon else ""
    return f"""<div style="margin-bottom: 18px; margin-top: 4px;">
<div style="display: flex; align-items: center; gap: 8px;">
{icon_html}
<div style="font-size: 1.3rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">{title}</div>
</div>
<div style="font-size: 0.88rem; color: #64748b; margin-top: 3px; font-weight: 500;">{subtitle}</div>
</div>"""


def render_stat_tile(label: str, value: str, subvalue: str = "", border_color: str = "#4f46e5") -> str:
    """Returns clean HTML for a KPI tile."""
    sub_html = f"<div style='font-size: 0.72rem; color: #64748b; margin-top: 2px;'>{subvalue}</div>" if subvalue else ""
    return f"""<div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid {border_color}; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
<div style="font-size: 0.74rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
<div style="font-size: 1.4rem; font-weight: 800; color: #0f172a; font-family: 'Plus Jakarta Sans', sans-serif; margin-top: 4px;">{value}</div>
{sub_html}
</div>"""
