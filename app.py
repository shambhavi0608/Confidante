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
    """Inject dark theme CSS matching the requested palette."""
    st.markdown(
        """
        <style>
        .stApp { background: #0D1117; color: #F0F6FC; }
        [data-testid="stSidebar"] { background: #161B22; border-right: 1px solid #30363D; }
        h1, h2, h3 { color: #F0F6FC; letter-spacing: 0; }
        .stButton > button, .stDownloadButton > button {
            background: #7C3AED;
            color: white;
            border: 0;
            border-radius: 8px;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: #059669;
            color: white;
            border: 0;
        }
        [data-testid="stMetricValue"] { color: #059669; }
        .stAlert { background: #161B22; color: #F0F6FC; border-color: #30363D; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_pages() -> Dict[str, str]:
    """Return display labels mapped to page module names."""
    return {
        "Live Detection": "pages.live_detection",
        "Audio Emotion": "pages.audio_emotion",
        "History": "pages.history",
        "Settings": "pages.settings",
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
    st.sidebar.title(config["app"]["name"])
    pages = get_pages()
    selected_page = st.sidebar.radio("Navigation", list(pages.keys()))
    st.sidebar.caption(f"Emotion: {st.session_state.emotion}")
    st.sidebar.caption(f"Language: {st.session_state.language.upper()}")
    try:
        renderer = load_page_renderer(pages[selected_page])
        renderer(config)
    except Exception as exc:
        st.error(f"Page failed: {exc}")


if __name__ == "__main__":
    main()
