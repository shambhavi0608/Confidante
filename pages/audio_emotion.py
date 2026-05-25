"""Audio emotion analysis page for SignSpeak AI."""

from typing import Dict

import streamlit as st


def render_page(config: Dict) -> None:
    """Render the SignSpeak AI audio emotion analysis screen."""
    # Header
    st.markdown('<div class="ss-title">Emotion Analysis</div>', unsafe_allow_html=True)
    
    # Three-column layout
    left, center, right = st.columns([0.9, 1.15, 0.95], gap="large")
    
    with left:
        # Dominant Emotion card
        st.markdown(
            """
            <div class="ss-card">
                <div class="ss-label">DOMINANT EMOTION</div>
                <div style="display:flex;align-items:center;gap:10px;margin-top:14px;">
                    <span class="ss-dot" style="background:#3B82F6;box-shadow:0 0 14px #3B82F6;"></span>
                    <div class="ss-title">Calm</div>
                </div>
                <div style="font-weight:900;color:#3B82F6;margin-top:8px;">92% Confidence</div>
                <div class="ss-muted" style="line-height:1.55;margin-top:18px;">
                    The detected tone is steady, melodic, and lacks sharp frequency spikes, indicating a relaxed state.
                </div>
            </div>
            <div class="ss-card" style="margin-top:18px;">
                <div class="ss-label">AUDIO QUALITY</div>
                <div style="display:grid;gap:12px;margin-top:16px;">
                    <div style="display:flex;justify-content:space-between;"><span>SNR Ratio</span><b>High (32dB)</b></div>
                    <div style="display:flex;justify-content:space-between;"><span>Latency</span><b>14ms</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with center:
        # Center orb visualization
        st.markdown(
            """
            <div class="ss-card" style="text-align:center;">
                <div class="ss-orb">
                    <span class="ss-star a">✦</span><span class="ss-star b">✦</span><span class="ss-star c">✦</span>
                    <div>
                        <div class="ss-title" style="font-size:3rem;color:#F0F0FF;">Calm</div>
                        <div class="ss-wave">
                            <span></span><span></span><span></span><span></span><span></span>
                            <span></span><span></span><span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
                <button class="ss-record">🎙️</button>
                <div class="ss-label" style="color:#EF4444;">RECORDING LIVE AUDIO</div>
                <div class="ss-wave" style="margin-top:18px;">
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with right:
        # Emotion probability panel
        st.markdown(
            """
            <div class="ss-card">
                <div class="ss-title">EMOTION PROBABILITY</div>
                <div class="ss-progress-row" style="border-color:#E8893C;">
                    <div class="ss-progress-top"><span>Happy</span><span>24%</span></div>
                    <div class="ss-track"><div class="ss-fill" style="width:24%;"></div></div>
                </div>
                <div class="ss-progress-row" style="border-color:#E8893C;">
                    <div class="ss-progress-top"><span>Calm</span><span>68%</span></div>
                    <div class="ss-track"><div class="ss-fill" style="width:68%;"></div></div>
                </div>
                <div class="ss-progress-row">
                    <div class="ss-progress-top"><span>Sad</span><span>5%</span></div>
                    <div class="ss-track"><div class="ss-fill" style="width:5%;"></div></div>
                </div>
                <div class="ss-progress-row">
                    <div class="ss-progress-top"><span>Angry</span><span>3%</span></div>
                    <div class="ss-track"><div class="ss-fill" style="width:3%;"></div></div>
                </div>
            </div>
            <div class="ss-card" style="margin-top:18px;">
                <div class="ss-label">SIGNAL WAVEFORM</div>
                <div class="ss-wave" style="margin-top:18px;">
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                    <span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
