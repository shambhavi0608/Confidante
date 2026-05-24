"""Application settings page."""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st


def render_page(config: Dict[str, Any]) -> None:
    """Render smoothing and language settings controls."""
    st.title("Settings")
    st.session_state.confidence_threshold = st.slider(
        "Confidence threshold",
        min_value=0.1,
        max_value=0.99,
        value=float(st.session_state.confidence_threshold),
        step=0.01,
    )
    st.session_state.buffer_size = st.slider(
        "Smoothing frames",
        min_value=1,
        max_value=15,
        value=int(st.session_state.buffer_size),
        step=1,
    )
    st.session_state.cooldown_seconds = st.slider(
        "Cooldown seconds",
        min_value=0.0,
        max_value=5.0,
        value=float(st.session_state.cooldown_seconds),
        step=0.1,
    )
    language_options = config["app"]["supported_languages"]
    selected_label = st.radio(
        "Speech language",
        options=list(language_options.keys()),
        format_func=lambda key: language_options[key],
        index=list(language_options.keys()).index(st.session_state.language),
        horizontal=True,
    )
    st.session_state.language = selected_label
    st.session_state.smoother.update_settings(
        buffer_size=st.session_state.buffer_size,
        cooldown_seconds=st.session_state.cooldown_seconds,
        confidence_threshold=st.session_state.confidence_threshold,
    )
    st.success("Settings updated.")
