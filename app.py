"""Streamlit entry point for the Sign Speech Converter project."""

from __future__ import annotations

import importlib
import logging
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
    required_sections = {"app", "gesture", "audio", "smoothing", "nlp"}
    missing = required_sections.difference(config)
    if missing:
        raise RuntimeError(f"Configuration is missing sections: {', '.join(sorted(missing))}")
    return config


def inject_dark_theme() -> None:
    """Inject the premium smart-home dashboard visual system."""
    st.markdown(
        """
        <style>
        :root {
            --ssc-bg-a: #1A1015;
            --ssc-bg-b: #0D0A0E;
            --ssc-sidebar: #110D14;
            --ssc-glass: rgba(255, 255, 255, 0.05);
            --ssc-border: rgba(255, 255, 255, 0.10);
            --ssc-text: #F5F0FF;
            --ssc-muted: rgba(245, 240, 255, 0.68);
            --ssc-amber: #E8893C;
            --ssc-purple: #9B6DFF;
            --ssc-green: #39D98A;
            --ssc-blue: #5AA7FF;
            --ssc-red: #FF5E6C;
            --ssc-gray: #8B8494;
            --ssc-radius: 24px;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        @keyframes glow {
            0%, 100% { opacity: 0.64; box-shadow: 0 0 20px rgba(232, 137, 60, 0.22); }
            50% { opacity: 1; box-shadow: 0 0 40px rgba(155, 109, 255, 0.40); }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fillBar {
            from { transform: scaleX(0); }
            to { transform: scaleX(1); }
        }
        .stApp {
            background:
                radial-gradient(circle at 18% 8%, rgba(232, 137, 60, 0.22), transparent 30%),
                radial-gradient(circle at 86% 18%, rgba(155, 109, 255, 0.22), transparent 32%),
                radial-gradient(circle at 50% 100%, rgba(232, 137, 60, 0.10), transparent 42%),
                linear-gradient(145deg, var(--ssc-bg-a), var(--ssc-bg-b) 64%);
            color: var(--ssc-text);
        }
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.018) 1px, transparent 1px);
            background-size: 42px 42px;
            mask-image: radial-gradient(circle at center, black, transparent 78%);
        }
        .block-container {
            animation: fadeIn 520ms ease-out both;
            max-width: 1260px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }
        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top, rgba(232, 137, 60, 0.14), transparent 34%),
                var(--ssc-sidebar);
            border-right: 1px solid rgba(232, 137, 60, 0.16);
            box-shadow: 16px 0 54px rgba(0, 0, 0, 0.30);
        }
        [data-testid="stSidebar"] > div {
            padding-top: 1.5rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            margin-bottom: 0.55rem;
            padding: 0.68rem 0.85rem;
            transition: all 180ms ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(232, 137, 60, 0.12);
            border-color: rgba(232, 137, 60, 0.46);
            box-shadow: 0 0 24px rgba(232, 137, 60, 0.16);
            transform: translateX(2px);
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, rgba(232, 137, 60, 0.26), rgba(155, 109, 255, 0.14));
            border-color: rgba(232, 137, 60, 0.64);
            box-shadow: 0 0 30px rgba(232, 137, 60, 0.22);
        }
        h1, h2, h3 {
            background: linear-gradient(90deg, var(--ssc-amber), var(--ssc-purple));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
            letter-spacing: 0;
        }
        h1 {
            font-size: clamp(2.25rem, 5vw, 4.25rem) !important;
            font-weight: 950 !important;
        }
        p, label, span, div {
            color: inherit;
        }
        [data-testid="stMetric"], .stMetric {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 20px;
            padding: 1rem;
            box-shadow: 0 0 26px rgba(155, 109, 255, 0.12);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        .stButton > button, .stDownloadButton > button {
            background: linear-gradient(135deg, var(--ssc-amber), var(--ssc-purple));
            border: 0;
            border-radius: 999px;
            color: white;
            font-weight: 850;
            letter-spacing: 0;
            min-height: 3rem;
            box-shadow: 0 0 26px rgba(232, 137, 60, 0.28), 0 0 42px rgba(155, 109, 255, 0.18);
            transition: transform 170ms ease, box-shadow 170ms ease, filter 170ms ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            border: 0;
            color: white;
            filter: brightness(1.08);
            transform: translateY(-1px);
            box-shadow: 0 0 36px rgba(232, 137, 60, 0.42), 0 0 52px rgba(155, 109, 255, 0.26);
        }
        .stButton > button[kind="primary"] {
            animation: pulse 2.6s ease-in-out infinite;
            font-size: 1.08rem;
            min-height: 3.65rem;
        }
        .stAlert {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.10);
            border-radius: 20px;
            color: var(--ssc-text);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        [data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 20px;
            box-shadow: 0 0 30px rgba(155, 109, 255, 0.10);
            overflow: hidden;
        }
        [data-testid="stDataFrame"] [role="row"]:hover {
            background: rgba(232, 137, 60, 0.10) !important;
        }
        .ssc-card {
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(145deg, rgba(255, 255, 255, 0.09), rgba(255, 255, 255, 0.035)),
                rgba(255, 255, 255, 0.05);
            border: 1px solid var(--ssc-border);
            border-radius: var(--ssc-radius);
            padding: 1.25rem;
            box-shadow: 0 18px 56px rgba(0, 0, 0, 0.30), 0 0 30px rgba(232, 137, 60, 0.12);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            animation: fadeIn 520ms ease-out both;
        }
        .ssc-card::after {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background:
                radial-gradient(circle at 20% 0%, rgba(232, 137, 60, 0.20), transparent 28%),
                radial-gradient(circle at 100% 20%, rgba(155, 109, 255, 0.18), transparent 30%);
            opacity: 0.72;
        }
        .ssc-card > * {
            position: relative;
            z-index: 1;
        }
        .ssc-card-label {
            color: var(--ssc-muted);
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.10em;
            margin-bottom: 0.55rem;
            text-transform: uppercase;
        }
        .ssc-muted { color: var(--ssc-muted); }
        .ssc-stat-grid {
            display: grid;
            gap: 0.85rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .ssc-stat {
            background: rgba(255, 255, 255, 0.045);
            border: 1px solid var(--ssc-border);
            border-radius: 20px;
            padding: 0.85rem;
        }
        .ssc-stat-value {
            color: var(--ssc-text);
            font-size: 1.38rem;
            font-weight: 900;
        }
        .ssc-section-title {
            align-items: center;
            color: var(--ssc-text);
            display: flex;
            font-size: 1.2rem;
            font-weight: 900;
            gap: 0.8rem;
            margin: 1.5rem 0 0.85rem;
        }
        .ssc-section-title::after {
            background: linear-gradient(90deg, rgba(232, 137, 60, 0.68), transparent);
            content: "";
            flex: 1;
            height: 1px;
        }
        .ssc-gesture-dial-card {
            align-items: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 460px;
            text-align: center;
        }
        .ssc-gesture-dial {
            align-items: center;
            animation: glow 3.2s ease-in-out infinite;
            aspect-ratio: 1;
            background:
                radial-gradient(circle at 50% 48%, rgba(245, 240, 255, 0.12), transparent 34%),
                conic-gradient(from 150deg, rgba(232, 137, 60, 0.98), rgba(155, 109, 255, 0.78), rgba(232, 137, 60, 0.98));
            border-radius: 50%;
            box-shadow: 0 0 46px rgba(232, 137, 60, 0.48), inset 0 0 44px rgba(13, 10, 14, 0.84);
            display: grid;
            place-items: center;
            width: min(330px, 76vw);
        }
        .ssc-gesture-dial-inner {
            align-items: center;
            aspect-ratio: 1;
            background: radial-gradient(circle, rgba(26, 16, 21, 0.92), rgba(13, 10, 14, 0.98));
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            width: 82%;
        }
        .ssc-gesture-value {
            color: var(--ssc-text);
            font-size: clamp(4.25rem, 14vw, 8rem);
            font-weight: 950;
            letter-spacing: 0;
            line-height: 0.95;
            text-shadow: 0 0 34px rgba(232, 137, 60, 0.74);
        }
        .ssc-confidence-text {
            color: var(--ssc-amber);
            font-size: 1.12rem;
            font-weight: 850;
            margin-top: 0.8rem;
        }
        .ssc-confidence-list {
            display: grid;
            gap: 0.9rem;
            margin-top: 1rem;
        }
        .ssc-confidence-row {
            align-items: center;
            display: grid;
            gap: 0.8rem;
            grid-template-columns: 4.5rem 1fr 3.5rem;
        }
        .ssc-confidence-track {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 999px;
            height: 0.8rem;
            overflow: hidden;
        }
        .ssc-confidence-fill {
            animation: fillBar 820ms ease-out both;
            background: linear-gradient(90deg, var(--ssc-amber), var(--ssc-purple));
            border-radius: inherit;
            box-shadow: 0 0 18px rgba(232, 137, 60, 0.38);
            height: 100%;
            transform-origin: left;
        }
        .ssc-sentence {
            color: var(--ssc-text);
            font-size: 1.28rem;
            line-height: 1.6;
            min-height: 6rem;
            overflow-wrap: anywhere;
            text-shadow: 0 0 20px rgba(245, 240, 255, 0.16);
        }
        .ssc-badge {
            align-items: center;
            border-radius: 999px;
            color: white;
            display: inline-flex;
            font-weight: 850;
            justify-content: center;
            letter-spacing: 0;
            min-height: 2rem;
            padding: 0.25rem 0.85rem;
            box-shadow: 0 0 20px rgba(155, 109, 255, 0.22);
        }
        .ssc-badge-happy { background: var(--ssc-green); }
        .ssc-badge-sad { background: var(--ssc-blue); }
        .ssc-badge-angry { background: var(--ssc-red); }
        .ssc-badge-neutral { background: var(--ssc-gray); }
        .ssc-badge-calm,
        .ssc-badge-fearful,
        .ssc-badge-disgust { background: var(--ssc-purple); }
        .ssc-emotion-orb {
            aspect-ratio: 1;
            background: radial-gradient(circle, rgba(255,255,255,0.10), rgba(255,255,255,0.03) 58%, rgba(13,10,14,0.70));
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 50%;
            display: grid;
            margin: 0 auto;
            place-items: center;
            text-align: center;
            width: min(290px, 72vw);
        }
        .ssc-emotion-happy { animation: pulse 3s ease-in-out infinite; box-shadow: 0 0 48px rgba(57, 217, 138, 0.45), inset 0 0 42px rgba(57, 217, 138, 0.12); }
        .ssc-emotion-sad { animation: pulse 3s ease-in-out infinite; box-shadow: 0 0 48px rgba(90, 167, 255, 0.42), inset 0 0 42px rgba(90, 167, 255, 0.12); }
        .ssc-emotion-angry { animation: pulse 3s ease-in-out infinite; box-shadow: 0 0 48px rgba(255, 94, 108, 0.45), inset 0 0 42px rgba(255, 94, 108, 0.12); }
        .ssc-emotion-neutral { animation: pulse 3s ease-in-out infinite; box-shadow: 0 0 48px rgba(139, 132, 148, 0.34), inset 0 0 42px rgba(139, 132, 148, 0.12); }
        .ssc-emotion-calm,
        .ssc-emotion-fearful,
        .ssc-emotion-disgust { animation: pulse 3s ease-in-out infinite; box-shadow: 0 0 48px rgba(155, 109, 255, 0.45), inset 0 0 42px rgba(155, 109, 255, 0.12); }
        .ssc-history-grid {
            display: grid;
            gap: 1rem;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            margin-top: 1rem;
        }
        .ssc-history-card { min-height: 180px; }
        div[data-testid="stSlider"] [data-baseweb="slider"] > div {
            background: rgba(255, 255, 255, 0.09);
        }
        div[data-testid="stSlider"] [role="slider"] {
            background: linear-gradient(135deg, var(--ssc-amber), var(--ssc-purple));
            box-shadow: 0 0 18px rgba(232, 137, 60, 0.38);
        }
        div[data-testid="stSlider"] [data-baseweb="slider"] div {
            border-radius: 999px;
        }
        [data-testid="stToggle"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 20px;
            padding: 0.7rem 0.9rem;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        [data-testid="stAudioInput"] {
            border: 1px solid rgba(255, 94, 108, 0.28);
            border-radius: 24px;
            padding: 0.75rem;
            box-shadow: 0 0 28px rgba(255, 94, 108, 0.14);
        }
        [data-testid="stAudioInput"] button {
            animation: pulse 1.9s ease-in-out infinite;
            box-shadow: 0 0 24px rgba(255, 94, 108, 0.26);
        }
        @media (max-width: 700px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .ssc-stat-grid { grid-template-columns: 1fr; }
            .ssc-gesture-dial-card { min-height: 360px; }
            .ssc-confidence-row { grid-template-columns: 3.5rem 1fr 3rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_pages() -> Dict[str, str]:
    """Return display labels mapped to page module names."""
    return {
        "● Live Detection": "pages.live_detection",
        "◆ Audio Emotion": "pages.audio_emotion",
        "▣ History": "pages.history",
        "⚙ Settings": "pages.settings",
    }


def load_page_renderer(module_name: str) -> Callable[[Dict[str, Any]], None]:
    """Import a page module and return its render function."""
    try:
        module = importlib.import_module(module_name)
        renderer = getattr(module, "render_page")
        return renderer
    except Exception as exc:
        LOGGER.exception("Could not load page %s: %s", module_name, exc)
        raise RuntimeError(f"Could not load page {module_name}: {exc}") from exc


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="Sign Speech Converter",
        page_icon="SSC",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_dark_theme()
    try:
        config = load_config()
        initialize_session(config)
    except Exception as exc:
        st.error(f"Startup failed: {exc}")
        return
    st.sidebar.markdown(
        f"""
        <div class="ssc-card">
            <div class="ssc-card-label">Smart console</div>
            <div style="font-size:1.35rem;font-weight:900;color:#F5F0FF;">{config["app"]["name"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    pages = get_pages()
    selected_page = st.sidebar.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
    st.sidebar.markdown(
        f"""
        <div class="ssc-card" style="margin-top:1rem;">
            <div class="ssc-card-label">Session</div>
            <div class="ssc-stat-grid">
                <div class="ssc-stat">
                    <div class="ssc-muted">Emotion</div>
                    <div class="ssc-stat-value">{st.session_state.emotion.title()}</div>
                </div>
                <div class="ssc-stat">
                    <div class="ssc-muted">Language</div>
                    <div class="ssc-stat-value">{st.session_state.language.upper()}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        renderer = load_page_renderer(pages[selected_page])
        renderer(config)
    except Exception as exc:
        st.error(f"Page failed: {exc}")


if __name__ == "__main__":
    main()
