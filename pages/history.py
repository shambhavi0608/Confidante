"""Conversation history page."""

from __future__ import annotations

from html import escape
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from utils.session import get_history


def render_page(config: Dict[str, Any]) -> None:
    """Render conversation history as premium frosted glass cards."""
    st.title("History")
    history = get_history()
    if not history:
        st.markdown(
            """
            <div class="ssc-card">
                <div class="ssc-card-label">Conversation archive</div>
                <div style="font-size:1.35rem;font-weight:900;color:#F5F0FF;">No history yet</div>
                <div class="ssc-muted" style="margin-top:0.45rem;">Spoken sentences will appear here as glass cards.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    st.markdown('<div class="ssc-section-title">Conversation archive</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ssc-history-grid">{_render_history_cards(history)}</div>', unsafe_allow_html=True)
    frame = pd.DataFrame(history)
    csv_bytes = frame.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Export conversation CSV",
        data=csv_bytes,
        file_name="sign_speech_history.csv",
        mime="text/csv",
        use_container_width=True,
    )


def _render_history_cards(history: List[Dict[str, str]]) -> str:
    """Return HTML for conversation history cards."""
    cards = []
    for entry in reversed(history):
        emotion = escape(entry.get("emotion", "neutral").lower())
        timestamp = escape(entry.get("timestamp", ""))
        sentence = escape(entry.get("sentence", ""))
        language = escape(entry.get("language", "en").upper())
        spoken_text = escape(entry.get("spoken_text", ""))
        spoken_html = f'<div class="ssc-muted" style="margin-top:0.8rem;">{spoken_text}</div>' if spoken_text else ""
        cards.append(
            f"""
            <div class="ssc-card ssc-history-card">
                <div class="ssc-card-label">{timestamp}</div>
                <div style="font-size:1.2rem;line-height:1.55;font-weight:850;color:#F5F0FF;">{sentence}</div>
                {spoken_html}
                <div style="display:flex;gap:0.55rem;align-items:center;flex-wrap:wrap;margin-top:1rem;">
                    <span class="ssc-badge ssc-badge-{emotion}">{emotion.title()}</span>
                    <span class="ssc-badge" style="background:linear-gradient(135deg,#E8893C,#9B6DFF);">{language}</span>
                </div>
            </div>
            """
        )
    return "".join(cards)
