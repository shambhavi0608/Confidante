"""Translation history page for SignSpeak AI."""

from typing import Dict

import streamlit as st


def render_page(config: Dict) -> None:
    """Render the SignSpeak AI translation history screen."""
    # Header
    st.markdown(
        """
        <div style="display:flex;align-items:end;justify-content:space-between;margin-bottom:22px;">
            <div>
                <div class="ss-title" style="font-size:2.4rem;">Translation History</div>
                <div class="ss-muted" style="margin-top:6px;">42 saved records</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Search bar
    st.text_input("Search", placeholder="Search across transcripts, dates, or emotions...", label_visibility="collapsed")
    
    # Sample history cards
    st.markdown(
        """
        <div class="ss-card ss-history-card" style="margin-top:18px;">
            <div>
                <div style="display:flex;justify-content:space-between;gap:18px;align-items:center;">
                    <div class="ss-label">OCT 24, 10:15 AM</div>
                    <span class="ss-badge ss-badge-purple">Focused</span>
                </div>
                <div class="ss-quote">"Hello, how are you today?"</div>
            </div>
            <div class="ss-avatar" style="width:58px;height:58px;">SA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Buttons for first card
    cols = st.columns([1, 1, 4])
    cols[0].button("Play Audio", key="play-1")
    cols[1].button("Copy Text", key="copy-1")
    
    # Second history card
    st.markdown(
        """
        <div class="ss-card ss-history-card" style="margin-top:18px;">
            <div>
                <div style="display:flex;justify-content:space-between;gap:18px;align-items:center;">
                    <div class="ss-label">OCT 24, 10:08 AM</div>
                    <span class="ss-badge ss-badge-amber">Determined</span>
                </div>
                <div class="ss-quote">"Please start the meeting when everyone is ready."</div>
            </div>
            <div class="ss-avatar" style="width:58px;height:58px;">SA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Buttons for second card
    cols = st.columns([1, 1, 4])
    cols[0].button("Play Audio", key="play-2")
    cols[1].button("Copy Text", key="copy-2")
    
    # Third history card
    st.markdown(
        """
        <div class="ss-card ss-history-card" style="margin-top:18px;">
            <div>
                <div style="display:flex;justify-content:space-between;gap:18px;align-items:center;">
                    <div class="ss-label">OCT 23, 06:42 PM</div>
                    <span class="ss-badge ss-badge-purple">Focused</span>
                </div>
                <div class="ss-quote">"Thank you for listening and responding so clearly."</div>
            </div>
            <div class="ss-avatar" style="width:58px;height:58px;">SA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Buttons for third card
    cols = st.columns([1, 1, 4])
    cols[0].button("Play Audio", key="play-3")
    cols[1].button("Copy Text", key="copy-3")
    
    # Load button at bottom
    st.markdown("<br>", unsafe_allow_html=True)
    center = st.columns([1, 1, 1])
    center[1].button("Load Previous Records", use_container_width=True)
