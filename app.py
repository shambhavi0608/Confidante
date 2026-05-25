from __future__ import annotations

import importlib
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict

import streamlit as st
import yaml

from utils.session import initialize_session

LOGGER = logging.getLogger(__name__)
CONFIG_PATH = Path(__file__).with_name("config.yaml")


def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """Load YAML configuration from disk with production-safe validation."""
    try:
        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
    except FileNotFoundError as exc:
        raise RuntimeError(f"Configuration file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Configuration file is invalid: {exc}") from exc
    missing = {"app", "gesture", "audio", "smoothing", "nlp"}.difference(config)
    if missing:
        raise RuntimeError(f"Configuration is missing sections: {', '.join(sorted(missing))}")
    return config


def inject_dark_theme() -> None:
    """Inject the full SignSpeak AI CSS design system."""
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        section[data-testid="stSidebar"] > div > div > div > ul { display: none !important; }
        :root {
            --bg: #0A0A0F;
            --card: #12121A;
            --line: #2A2A3A;
            --side: #0D0D15;
            --amber: #E8893C;
            --amber2: #F5A623;
            --violet: #6B7FD4;
            --text: #F0F0FF;
            --muted: #8888AA;
            --green: #22C55E;
            --blue: #3B82F6;
            --purple: #8B5CF6;
            --red: #EF4444;
            --pink: #EC4899;
            --cyan: #06B6D4;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%,100% { transform: scale(1); opacity: .8; } 50% { transform: scale(1.05); opacity: 1; } }
        @keyframes bars { 0%,100% { transform: scaleY(.35); } 50% { transform: scaleY(1); } }
        @keyframes blink { 0%,45% { opacity: 1; } 46%,100% { opacity: 0; } }
        @keyframes ring { 0% { box-shadow: 0 0 0 0 rgba(239,68,68,.42); } 80% { box-shadow: 0 0 0 22px rgba(239,68,68,0); } 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); } }
        .stApp {
            background:
                radial-gradient(circle at 15% 5%, rgba(232,137,60,.11), transparent 25%),
                radial-gradient(circle at 90% 15%, rgba(107,127,212,.13), transparent 28%),
                linear-gradient(135deg, #0A0A0F 0%, #0A0A0F 55%, #11111A 100%);
            background-attachment: fixed;
            color: var(--text);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                radial-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
                linear-gradient(rgba(255,255,255,.012), rgba(255,255,255,0));
            background-size: 22px 22px, 100% 100%;
            opacity: .45;
        }
        .block-container { max-width: 1380px; padding: 30px 34px 42px; animation: fadeIn .45s ease both; }
        [data-testid="stSidebar"] { background: var(--side) !important; border-right: 1px solid #191925; box-shadow: 18px 0 42px rgba(0,0,0,.34); }
        [data-testid="stSidebar"] * { color: var(--text) !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            min-height: 48px; padding: 0 16px; margin: 8px 0; border-radius: 16px;
            background: transparent; border: 1px solid transparent; transition: all .18s ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] input { display: none !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(232,137,60,.09); border-color: rgba(232,137,60,.22); transform: translateX(2px);
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(90deg, rgba(232,137,60,.24), rgba(245,166,35,.08));
            border-color: rgba(232,137,60,.52);
            box-shadow: inset 3px 0 0 var(--amber), 0 0 22px rgba(232,137,60,.12);
        }
        h1, h2, h3 { color: var(--text) !important; letter-spacing: 0 !important; }
        h1 { font-size: clamp(2rem, 4vw, 3.25rem) !important; font-weight: 900 !important; }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background: #0D0D15 !important; border: 1px solid var(--line) !important; border-radius: 16px !important; color: var(--text) !important;
        }
        .stButton > button, .stDownloadButton > button {
            border: 0; border-radius: 999px; color: #16100B; font-weight: 900; min-height: 46px;
            background: linear-gradient(135deg, var(--amber), var(--amber2));
            box-shadow: 0 10px 28px rgba(232,137,60,.24); transition: all .18s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-2px); filter: brightness(1.05); color: #16100B; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid var(--line); }
        .stTabs [data-baseweb="tab"] { color: var(--muted); border-radius: 16px 16px 0 0; }
        .stTabs [aria-selected="true"] { color: var(--text) !important; background: rgba(232,137,60,.10); }
        div[data-testid="stSlider"] [role="slider"] { background: linear-gradient(135deg, var(--amber), var(--amber2)); box-shadow: 0 0 18px rgba(232,137,60,.35); }
        .ss-card {
            background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 22px;
            box-shadow: 0 18px 44px rgba(0,0,0,.28); transition: all .18s ease; animation: fadeIn .45s ease both;
        }
        .ss-card:hover { transform: translateY(-2px); border-color: rgba(232,137,60,.35); }
        .ss-label { color: var(--muted); font-size: .78rem; letter-spacing: .12em; text-transform: uppercase; font-weight: 800; }
        .ss-title { color: var(--text); font-weight: 900; font-size: 1.4rem; line-height: 1.1; }
        .ss-muted { color: var(--muted); }
        .ss-logo { padding: 10px 4px 20px; }
        .ss-logo-main { font-size: 1.72rem; font-weight: 950; color: var(--text); }
        .ss-logo-sub { color: var(--muted); font-size: .85rem; margin-top: 3px; }
        .ss-profile { display:flex; align-items:center; gap:12px; margin-top: 18px; padding: 14px; border:1px solid var(--line); border-radius:16px; background:#101018; }
        .ss-avatar { width:42px; height:42px; border-radius:50%; background:linear-gradient(135deg,var(--amber),var(--violet)); display:grid; place-items:center; font-weight:900; color:white; }
        .ss-dot { width:10px; height:10px; border-radius:50%; display:inline-block; background:var(--amber); box-shadow:0 0 14px var(--amber); }
        .ss-gesture-card { min-height: 390px; display:grid; place-items:center; text-align:center; box-shadow:0 0 36px rgba(232,137,60,.18); }
        .ss-gesture-word { font-size: clamp(3.4rem, 9vw, 7rem); color: var(--amber); font-weight: 950; text-shadow:0 0 30px rgba(232,137,60,.62); animation:pulse 2.4s ease infinite; }
        .ss-wave { height:42px; display:flex; gap:6px; align-items:end; justify-content:center; margin-top:24px; }
        .ss-wave span { width:7px; height:26px; border-radius:999px; background:linear-gradient(var(--amber2), var(--amber)); animation:bars 1.1s ease-in-out infinite; transform-origin:bottom; }
        .ss-wave span:nth-child(2n) { animation-delay:.15s; height:34px; } .ss-wave span:nth-child(3n) { animation-delay:.3s; height:18px; }
        .ss-badge { display:inline-flex; align-items:center; padding:7px 12px; border-radius:999px; font-weight:850; font-size:.82rem; }
        .ss-badge-amber { color:#180F08; background:linear-gradient(135deg,var(--amber),var(--amber2)); }
        .ss-badge-green { color:white; background:#22C55E; } .ss-badge-blue { color:white; background:#3B82F6; } .ss-badge-purple { color:white; background:#8B5CF6; }
        .ss-transcript { min-height:92px; font-size:1.35rem; line-height:1.45; color:var(--text); border:1px solid var(--line); border-radius:16px; background:#0D0D15; padding:18px; }
        .ss-cursor { display:inline-block; width:2px; height:1.25em; background:var(--amber); margin-left:4px; vertical-align:-.2em; animation:blink 1s step-end infinite; }
        .ss-progress-row { margin:18px 0; }
        .ss-progress-top { display:flex; justify-content:space-between; color:var(--text); font-weight:800; margin-bottom:8px; }
        .ss-track { height:10px; background:#20202C; border-radius:999px; overflow:hidden; border:1px solid #2A2A3A; }
        .ss-fill { height:100%; border-radius:inherit; background:linear-gradient(90deg,var(--amber),var(--amber2)); transform-origin:left; animation:fillBar .8s ease both; }
        .ss-history-card { display:grid; grid-template-columns:1fr auto; gap:18px; border-bottom:1px solid #242433; padding-bottom:18px; }
        .ss-quote { color:var(--text); font-size:1.45rem; line-height:1.35; font-weight:750; margin:18px 0; }
        .ss-record { width:76px; height:76px; border-radius:50%; border:0; display:grid; place-items:center; margin:18px auto 8px; background:#EF4444; color:white; font-size:1.9rem; animation:ring 1.7s infinite; }
        .ss-orb { width:min(360px,70vw); aspect-ratio:1; border-radius:50%; margin:0 auto; display:grid; place-items:center; position:relative; background:radial-gradient(circle,#202036,#101018 64%); border:1px solid #31314A; box-shadow:0 0 70px rgba(107,127,212,.28); }
        .ss-star { position:absolute; color:#F0F0FF; opacity:.75; font-size:1.35rem; animation:pulse 2s infinite; }
        .ss-star.a { top:8%; left:18%; } .ss-star.b { top:20%; right:8%; animation-delay:.4s; } .ss-star.c { bottom:14%; left:10%; animation-delay:.8s; }
        .ss-footer { display:flex; justify-content:center; gap:28px; color:var(--muted); font-size:.78rem; letter-spacing:.1em; margin:34px 0 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_pages() -> Dict[str, str]:
    """Return display labels mapped to page module names."""
    return {
        "🔴 Live Translator": "pages.live_detection",
        "📋 Translation History": "pages.history",
        "⚙️ Emotion Settings": "pages.settings",
        "📊 System Status": "pages.audio_emotion",
    }


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="SignSpeak AI", page_icon="🔴", layout="wide", initial_sidebar_state="expanded")
    inject_dark_theme()
    
    try:
        config = load_config()
        initialize_session(config)
    except Exception as exc:
        st.error(f"Startup failed: {exc}")
        import traceback
        st.error(traceback.format_exc())
        return
    
    st.sidebar.markdown(
        """
        <div class="ss-logo">
            <div class="ss-logo-main">SignSpeak AI</div>
            <div class="ss-logo-sub">Premium Sign-to-Speech</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    pages = get_pages()
    selected_page = st.sidebar.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
    st.sidebar.button("Start Session", use_container_width=True, type="primary")
    st.sidebar.markdown(
        """
        <div class="ss-profile">
            <div class="ss-avatar">SA</div>
            <div>
                <div style="font-weight:900;">Alex Morgan</div>
                <div class="ss-muted" style="font-size:.82rem;">Pro workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Render selected page with error handling
    try:
        if "Live Translator" in selected_page:
            from pages.live_detection import render_page
            render_page(config)
        elif "Translation History" in selected_page:
            from pages.history import render_page
            render_page(config)
        elif "Emotion Settings" in selected_page:
            from pages.settings import render_page
            render_page(config)
        elif "System Status" in selected_page:
            from pages.audio_emotion import render_page
            render_page(config)
    except Exception as exc:
        st.error(f"Page failed to load: {exc}")
        import traceback
        st.error(traceback.format_exc())
        
        # Show fallback content
        st.markdown("### 🚨 Page Error")
        st.write(f"The selected page '{selected_page}' encountered an error.")
        st.write("Please check the error details above or try selecting a different page.")


if __name__ == "__main__":
    main()
