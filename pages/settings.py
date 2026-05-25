"""Settings page for SignSpeak AI."""
from __future__ import annotations
import streamlit as st
from typing import Any, Dict


def render_page(config: Dict[str, Any]) -> None:

    st.markdown("""
    <h1 style='font-size:2.2rem;font-weight:900;margin-bottom:4px;'>Settings</h1>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Global", "Security", "Accessibility"])

    with tab1:
        st.markdown("""
        <div class='ss-card' style='margin-bottom:20px;'>
            <div class='ss-title' style='margin-bottom:6px;'>System Preferences</div>
            <div class='ss-muted'>Configure detection, voice synthesis, theme, and account behavior.</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='ss-card'>", unsafe_allow_html=True)
            st.markdown("**Detection Sensitivity**")

            threshold = st.slider(
                "Gesture Confidence Threshold",
                min_value=0.10, max_value=0.99,
                value=st.session_state.get("confidence_threshold", 0.75),
                step=0.01, key="conf_slider"
            )
            st.session_state["confidence_threshold"] = threshold
            st.caption("Higher confidence reduces false positives.")

            tracking = st.selectbox(
                "Facial Expression Tracking",
                ["High", "Medium", "Low"],
                key="facial_tracking"
            )

            lighting = st.toggle(
                "Adaptive Lighting Calibration",
                value=True, key="lighting_toggle"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='ss-card'>", unsafe_allow_html=True)
            st.markdown("**Audio Volume**")

            volume = st.slider(
                "Synthesis Volume",
                min_value=0, max_value=100,
                value=st.session_state.get("synthesis_volume", 65),
                key="volume_slider"
            )
            st.session_state["synthesis_volume"] = volume

            st.markdown("**Voice Model Selection**")
            voice_model = st.radio(
                "",
                ["HumaniAI", "Synth-Fluid"],
                horizontal=True,
                key="voice_model",
                label_visibility="collapsed"
            )

            emotional = st.toggle(
                "Emotional Inflection",
                value=True, key="emotional_toggle"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class='ss-card'>
            <div style='font-weight:900;font-size:1.1rem;margin-bottom:16px;'>UI Theme</div>
        """, unsafe_allow_html=True)

        theme_col1, theme_col2 = st.columns(2)
        with theme_col1:
            st.markdown("""
            <div style='display:flex;justify-content:space-between;align-items:center;
            padding:12px;border:1px solid rgba(232,137,60,.5);border-radius:12px;margin-bottom:8px;'>
                <span style='color:#E8893C;font-weight:800;'>🟠 Midnight Obsidian</span>
                <span style='color:#8888AA;font-size:.82rem;'>Selected</span>
            </div>
            <div style='display:flex;justify-content:space-between;align-items:center;
            padding:12px;border:1px solid #2A2A3A;border-radius:12px;'>
                <span style='color:#8888AA;'>🔒 Clinical Light</span>
                <span style='color:#8888AA;font-size:.82rem;'>Locked</span>
            </div>
            """, unsafe_allow_html=True)

        with theme_col2:
            glass = st.slider(
                "Glassmorphism Intensity",
                min_value=0, max_value=100,
                value=55, key="glass_slider"
            )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class='ss-card'>
            <div style='font-weight:900;font-size:1.1rem;margin-bottom:16px;'>Output Language</div>
        """, unsafe_allow_html=True)

        lang = st.radio(
            "",
            ["English", "Hindi"],
            horizontal=True,
            key="lang_radio",
            label_visibility="collapsed",
            index=0 if st.session_state.get("output_language", "en") == "en" else 1
        )
        st.session_state["output_language"] = "en" if lang == "English" else "hi"
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class='ss-card'>
            <div style='font-weight:900;font-size:1.1rem;margin-bottom:16px;'>Account Settings</div>
        """, unsafe_allow_html=True)

        acc_col1, acc_col2 = st.columns([1, 2])
        with acc_col1:
            st.markdown("""
            <div class='ss-avatar' style='width:56px;height:56px;font-size:1.2rem;'>SA</div>
            """, unsafe_allow_html=True)
        with acc_col2:
            st.markdown("""
            <div style='font-weight:900;'>Alex Morgan</div>
            <div class='ss-muted' style='font-size:.85rem;'>alex@signspeak.ai</div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("Privacy & Data Handling →", use_container_width=True):
                st.info("Privacy settings coming soon.")
        with btn2:
            if st.button("Subscription & Billing →", use_container_width=True):
                st.info("Billing portal coming soon.")

        danger1, danger2 = st.columns(2)
        with danger1:
            if st.button("🗑 Delete Account", use_container_width=True):
                st.warning("This action cannot be undone.")
        with danger2:
            if st.button("🚪 Log Out", use_container_width=True):
                st.session_state.clear()
                st.success("Logged out successfully.")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='ss-footer'>
            <span>DOCUMENTATION</span><span>API ACCESS</span><span>SUPPORT</span>
            <span style='margin-left:auto;'>SYSTEM ONLINE v4.2.1</span>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='ss-card'>", unsafe_allow_html=True)
        st.markdown("**Security Settings**")
        st.toggle("Two-Factor Authentication", value=False)
        st.toggle("Session Timeout (30 min)", value=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='ss-card'>", unsafe_allow_html=True)
        st.markdown("**Accessibility Settings**")
        st.toggle("High Contrast Mode", value=False)
        st.toggle("Screen Reader Support", value=True)
        font_size = st.slider("Font Size", 12, 24, 16)
        st.markdown("</div>", unsafe_allow_html=True)
