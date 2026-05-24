"""System settings page for SignSpeak AI."""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st


def render_page(config: Dict[str, Any]) -> None:
    """Render the SignSpeak AI system settings screen."""
    st.markdown('<div class="ss-title" style="font-size:2.4rem;margin-bottom:18px;">Settings</div>', unsafe_allow_html=True)
    global_tab, security_tab, accessibility_tab = st.tabs(["Global", "Security", "Accessibility"])
    with global_tab:
        _render_global_settings(config)
    with security_tab:
        _placeholder_panel("Security", "Encryption, workspace access, and account protection controls are online.")
    with accessibility_tab:
        _placeholder_panel("Accessibility", "Visual contrast, caption density, and assistive feedback preferences.")
    st.markdown(
        """
        <div class="ss-footer">
            <span>DOCUMENTATION</span><span>API ACCESS</span><span>SUPPORT</span>
        </div>
        <div style="text-align:center;color:#8888AA;font-size:.78rem;">SYSTEM ONLINE v4.2.1-P10</div>
        """,
        unsafe_allow_html=True,
    )


def _render_global_settings(config: Dict[str, Any]) -> None:
    """Render the Global settings tab."""
    st.markdown(
        """
        <div style="margin:22px 0;">
            <div class="ss-title">System Preferences</div>
            <div class="ss-muted">Configure detection, voice synthesis, theme, and account behavior.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="ss-card"><div class="ss-title">Detection Sensitivity</div>', unsafe_allow_html=True)
        st.session_state.confidence_threshold = st.slider(
            "Gesture Confidence Threshold",
            min_value=0.1,
            max_value=0.99,
            value=float(st.session_state.confidence_threshold),
            step=0.01,
        )
        st.markdown('<div class="ss-muted">Higher confidence reduces false positives.</div>', unsafe_allow_html=True)
        st.selectbox("Facial Expression Tracking", ["High", "Medium", "Low"], index=0)
        st.toggle("Adaptive Lighting Calibration", value=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="ss-card"><div class="ss-title">Audio Volume</div>', unsafe_allow_html=True)
        st.slider("Synthesis Volume", min_value=0, max_value=100, value=65)
        st.segmented_control("Voice Model Selection", ["HumaniAI", "Synth-Fluid"], default="HumaniAI")
        st.toggle("Emotional Inflection", value=True)
        st.markdown("</div>", unsafe_allow_html=True)
    _render_theme_section()
    _render_account_section()
    st.session_state.smoother.update_settings(confidence_threshold=st.session_state.confidence_threshold)


def _render_theme_section() -> None:
    """Render the UI theme section."""
    st.markdown(
        """
        <div class="ss-card" style="margin-top:22px;">
            <div class="ss-title">UI Theme</div>
            <div style="display:grid;gap:14px;margin-top:18px;">
                <div style="display:flex;justify-content:space-between;align-items:center;"><span><span class="ss-dot"></span> Midnight Obsidian</span><span class="ss-muted">Selected</span></div>
                <div style="display:flex;justify-content:space-between;align-items:center;"><span>🔒 Clinical Light</span><span class="ss-muted">Locked</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.slider("Glassmorphism Intensity", min_value=0, max_value=100, value=55)


def _render_account_section() -> None:
    """Render account settings cards."""
    st.markdown(
        """
        <div class="ss-card" style="margin-top:22px;">
            <div class="ss-title">Account Settings</div>
            <div style="display:flex;align-items:center;gap:14px;margin-top:18px;">
                <div class="ss-avatar">SA</div>
                <div><div style="font-weight:900;">Samira Anand</div><div class="ss-muted">samira@signspeak.ai</div></div>
            </div>
            <div style="display:grid;gap:14px;margin-top:20px;">
                <div style="display:flex;justify-content:space-between;border-top:1px solid #2A2A3A;padding-top:14px;">Privacy & Data Handling <span>→</span></div>
                <div style="display:flex;justify-content:space-between;border-top:1px solid #2A2A3A;padding-top:14px;">Subscription & Billing <span>→</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    danger, logout, spacer = st.columns([1, 1, 2])
    danger.button("Delete Account", use_container_width=True)
    logout.button("Log Out", use_container_width=True)


def _placeholder_panel(title: str, body: str) -> None:
    """Render a placeholder settings panel."""
    st.markdown(
        f"""
        <div class="ss-card" style="margin-top:22px;">
            <div class="ss-title">{title}</div>
            <div class="ss-muted" style="margin-top:8px;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
