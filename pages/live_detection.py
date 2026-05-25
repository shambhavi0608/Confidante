"""Live translator page for SignSpeak AI."""

from typing import Dict

import streamlit as st


def render_page(config: Dict) -> None:
    """Render the SignSpeak AI live translator screen."""
    # Header
    st.markdown('<div class="ss-title"><span class="ss-dot"></span> Active Detection</div>', unsafe_allow_html=True)
    
    # Two-column layout
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # Gesture display card
        st.markdown(
            """
            <div class="ss-card ss-gesture-card">
                <div>
                    <div class="ss-gesture-word">HELLO</div>
                    <div class="ss-label" style="color:#E8893C;">DETECTED</div>
                    <div class="ss-wave">
                        <span></span><span></span><span></span><span></span><span></span>
                        <span></span><span></span><span></span><span></span><span></span>
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Confidence panel
        st.markdown(
            """
            <div class="ss-card" style="margin-top:18px;">
                <div class="ss-title">Detection Confidence</div>
                <div class="ss-progress-row">
                    <div class="ss-progress-top"><span>Spatial Accuracy</span><span>98%</span></div>
                    <div class="ss-track"><div class="ss-fill" style="width:98%;"></div></div>
                </div>
                <div class="ss-progress-row">
                    <div class="ss-progress-top"><span>Temporal Fluidity</span><span>86%</span></div>
                    <div class="ss-track"><div class="ss-fill" style="width:86%;"></div></div>
                </div>
                <div class="ss-progress-row">
                    <div class="ss-progress-top"><span>Contextual Match</span><span>82%</span></div>
                    <div class="ss-track"><div class="ss-fill" style="width:82%;"></div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col2:
        # Transcription card
        st.markdown(
            """
            <div class="ss-card">
                <span class="ss-badge ss-badge-amber">LIVE TRANSCRIPTION</span>
                <div class="ss-transcript" style="margin-top:18px;">Hello, how are you today?<span class="ss-cursor"></span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Speak button
        st.button("🔊 Speak", use_container_width=True, type="primary")
