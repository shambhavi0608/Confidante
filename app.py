from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

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


def inject_dark_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
    [data-testid="stSidebarNav"], [data-testid="stSidebarNav"] *, section[data-testid="stSidebar"] ul, header[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
    .stApp { background: radial-gradient(ellipse at top, #1A1015 0%, #0D0A0E 60%) !important; }
    section[data-testid="stSidebar"] { background: #0D0D15 !important; border-right: 1px solid #2A2A3A !important; }
    section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
    .ss-logo { padding: 28px 20px 20px; border-bottom: 1px solid #2A2A3A; margin-bottom: 16px; }
    .ss-logo-main { font-size: 1.5rem; font-weight: 900; color: #F0F0FF; }
    .ss-logo-sub { font-size: .78rem; color: #8888AA; letter-spacing: .1em; text-transform: uppercase; margin-top: 4px; }
    [data-testid="stRadio"] > div { gap: 4px !important; }
    [data-testid="stRadio"] [data-baseweb="radio"] { display: none !important; }
    [data-testid="stRadio"] label { background: transparent !important; border-radius: 12px !important; padding: 12px 16px !important; color: #8888AA !important; font-weight: 600 !important; transition: all .2s !important; border: 1px solid transparent !important; cursor: pointer; }
    [data-testid="stRadio"] label:hover { background: rgba(232,137,60,.1) !important; color: #E8893C !important; }
    [data-testid="stRadio"] label[data-checked="true"], [data-testid="stRadio"] label[aria-checked="true"] { background: rgba(232,137,60,.15) !important; color: #E8893C !important; border-color: rgba(232,137,60,.4) !important; }
    .ss-card { background: #12121A; border: 1px solid #2A2A3A; border-radius: 20px; padding: 20px 22px; margin-bottom: 16px; }
    .ss-card:hover { border-color: rgba(232,137,60,.25); transition: border-color .3s; }
    .ss-title { font-size: 1.1rem; font-weight: 900; color: #F0F0FF; }
    .ss-label { font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #8888AA; }
    .ss-muted { color: #8888AA; font-size: .9rem; }
    .ss-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: .78rem; font-weight: 700; }
    .ss-badge-amber { background: rgba(232,137,60,.2); color: #E8893C; border: 1px solid rgba(232,137,60,.3); }
    .ss-badge-blue { background: rgba(59,130,246,.2); color: #60A5FA; border: 1px solid rgba(59,130,246,.3); }
    .ss-badge-purple { background: rgba(139,92,246,.2); color: #A78BFA; border: 1px solid rgba(139,92,246,.3); }
    .ss-dot { width: 10px; height: 10px; border-radius: 50%; background: #22C55E; box-shadow: 0 0 8px #22C55E; animation: pulse 2s infinite; }
    .ss-gesture-card { text-align: center; min-height: 200px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1A1015 0%, #12121A 100%); border: 1px solid rgba(232,137,60,.3); box-shadow: 0 0 40px rgba(232,137,60,.08); }
    .ss-gesture-word { font-size: 3.5rem; font-weight: 900; color: #E8893C; text-shadow: 0 0 30px rgba(232,137,60,.5); letter-spacing: .05em; }
    .ss-transcript { background: #0D0D15; border: 1px solid #2A2A3A; border-radius: 16px; padding: 18px 20px; min-height: 80px; font-size: 1.1rem; color: #F0F0FF; line-height: 1.7; position: relative; }
    .ss-cursor { display: inline-block; width: 2px; height: 1.1em; background: #E8893C; margin-left: 2px; vertical-align: middle; animation: blink 1s infinite; }
    .ss-track { height: 8px; background: #2A2A3A; border-radius: 4px; overflow: hidden; }
    .ss-fill { height: 100%; background: linear-gradient(90deg, #E8893C, #F5A623); border-radius: 4px; transition: width .5s ease; }
    .ss-progress-row { margin-bottom: 14px; }
    .ss-progress-top { display: flex; justify-content: space-between; font-size: .88rem; margin-bottom: 6px; color: #F0F0FF; }
    .ss-orb { width: 180px; height: 180px; border-radius: 50%; background: radial-gradient(circle, #1A1015, #0D0A0E); border: 2px solid rgba(232,137,60,.3); display: flex; align-items: center; justify-content: center; margin: 0 auto; position: relative; box-shadow: 0 0 40px rgba(232,137,60,.15); }
    .ss-star { position: absolute; color: #E8893C; font-size: 1.2rem; opacity: .7; }
    .ss-star.a { top: 10px; right: 20px; } .ss-star.b { bottom: 15px; left: 10px; } .ss-star.c { top: 40px; left: 0; }
    .ss-wave { display: flex; align-items: flex-end; gap: 3px; height: 32px; }
    .ss-wave span { width: 4px; background: linear-gradient(to top, #E8893C, #F5A623); border-radius: 2px; animation: wave 1.2s ease-in-out infinite; }
    .ss-wave span:nth-child(1){height:40%;animation-delay:0s} .ss-wave span:nth-child(2){height:70%;animation-delay:.1s} .ss-wave span:nth-child(3){height:90%;animation-delay:.2s} .ss-wave span:nth-child(4){height:60%;animation-delay:.3s} .ss-wave span:nth-child(5){height:80%;animation-delay:.4s} .ss-wave span:nth-child(6){height:50%;animation-delay:.5s} .ss-wave span:nth-child(7){height:75%;animation-delay:.6s} .ss-wave span:nth-child(8){height:45%;animation-delay:.7s}
    .ss-footer { display: flex; gap: 24px; padding: 16px 0 0; border-top: 1px solid #2A2A3A; font-size: .75rem; color: #8888AA; letter-spacing: .1em; }
    .ss-avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #E8893C, #9B6DFF); display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; font-size: .9rem; }
    .ss-history-card { background: #12121A; border: 1px solid #2A2A3A; border-radius: 16px; padding: 18px 20px; margin-bottom: 12px; }
    .ss-quote { font-size: 1.05rem; color: #F0F0FF; line-height: 1.7; font-style: italic; margin: 8px 0; }
    .stButton > button { background: linear-gradient(135deg, #E8893C, #F5A623) !important; color: #0D0A0E !important; font-weight: 800 !important; border: none !important; border-radius: 20px !important; padding: 10px 24px !important; transition: all .2s !important; box-shadow: 0 4px 20px rgba(232,137,60,.3) !important; }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(232,137,60,.4) !important; }
    .stButton > button[kind="secondary"] { background: #12121A !important; color: #F0F0FF !important; border: 1px solid #2A2A3A !important; box-shadow: none !important; }
    .stTextInput > div > div > input { background: #0D0D15 !important; border: 1px solid #2A2A3A !important; border-radius: 12px !important; color: #F0F0FF !important; padding: 10px 14px !important; }
    .stSelectbox > div > div { background: #12121A !important; border: 1px solid #2A2A3A !important; border-radius: 12px !important; color: #F0F0FF !important; }
    .stSlider > div > div > div { background: linear-gradient(90deg, #E8893C, #F5A623) !important; }
    .stTabs [data-baseweb="tab-list"] { background: #12121A !important; border-radius: 12px !important; gap: 4px !important; padding: 4px !important; }
    .stTabs [data-baseweb="tab"] { color: #8888AA !important; border-radius: 10px !important; font-weight: 700 !important; }
    .stTabs [aria-selected="true"] { background: rgba(232,137,60,.16) !important; color: #E8893C !important; }
    @keyframes pulse { 0%, 100% { opacity: .65; transform: scale(1); } 50% { opacity: 1; transform: scale(1.08); } }
    @keyframes blink { 0%, 45% { opacity: 1; } 46%, 100% { opacity: 0; } }
    @keyframes wave { 0%, 100% { transform: scaleY(.45); } 50% { transform: scaleY(1); } }
    </style>
    """, unsafe_allow_html=True)


def main() -> None:
    """Run the Streamlit application."""
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

    nav_options = {
        "🔴 Live Translator": "live_detection",
        "📋 Translation History": "history",
        "⚙️ Emotion Settings": "settings",
        "📊 System Status": "audio_emotion",
    }
    selected = st.sidebar.radio("", list(nav_options.keys()), label_visibility="collapsed", key="main_nav")
    page_key = nav_options[selected]
    try:
        if page_key == "live_detection":
            from pages.live_detection import render_page

            render_page(config)
        elif page_key == "history":
            from pages.history import render_page

            render_page(config)
        elif page_key == "settings":
            from pages.settings import render_page

            render_page(config)
        elif page_key == "audio_emotion":
            from pages.audio_emotion import render_page

            render_page(config)
    except Exception as e:
        st.error(f"Page error: {e}")
        import traceback

        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
