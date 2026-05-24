"""Application settings page."""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st


def render_page(config: Dict[str, Any]) -> None:
    """Render premium dashboard controls for smoothing and language settings."""
    st.title("Settings")
    st.markdown('<div class="ssc-section-title">Detection tuning</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="ssc-card" style="margin-bottom:1rem;">
                <div class="ssc-card-label">Gesture stabilizer</div>
                <div class="ssc-muted">Tune sensitivity, smoothing, and repeat protection.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        slider_columns = st.columns(3, gap="large")
        with slider_columns[0]:
            st.session_state.confidence_threshold = st.slider(
                "Confidence threshold",
                min_value=0.1,
                max_value=0.99,
                value=float(st.session_state.confidence_threshold),
                step=0.01,
            )
        with slider_columns[1]:
            st.session_state.buffer_size = st.slider(
                "Smoothing frames",
                min_value=1,
                max_value=15,
                value=int(st.session_state.buffer_size),
                step=1,
            )
        with slider_columns[2]:
            st.session_state.cooldown_seconds = st.slider(
                "Cooldown seconds",
                min_value=0.0,
                max_value=5.0,
                value=float(st.session_state.cooldown_seconds),
                step=0.1,
            )
    st.markdown('<div class="ssc-section-title">Voice output</div>', unsafe_allow_html=True)
    language_options = config["app"]["supported_languages"]
    language_keys = list(language_options.keys())
    if st.session_state.language not in language_keys:
        st.session_state.language = config["app"].get("default_language", language_keys[0])
    hindi_enabled = st.toggle(
        "Hindi speech output",
        value=st.session_state.language == "hi",
        help="Switches synthesized speech between English and Hindi.",
    )
    st.session_state.language = "hi" if hindi_enabled and "hi" in language_keys else "en"
    st.markdown(
        f"""
        <div class="ssc-card" style="margin-top:1rem;">
            <div class="ssc-card-label">Active profile</div>
            <div class="ssc-stat-grid">
                <div class="ssc-stat">
                    <div class="ssc-muted">Language</div>
                    <div class="ssc-stat-value">{language_options.get(st.session_state.language, st.session_state.language)}</div>
                </div>
                <div class="ssc-stat">
                    <div class="ssc-muted">Confidence</div>
                    <div class="ssc-stat-value">{st.session_state.confidence_threshold:.0%}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.smoother.update_settings(
        buffer_size=st.session_state.buffer_size,
        cooldown_seconds=st.session_state.cooldown_seconds,
        confidence_threshold=st.session_state.confidence_threshold,
    )
