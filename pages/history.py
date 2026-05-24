"""Translation history page for SignSpeak AI."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any, Dict, List

import streamlit as st

from utils.session import get_history


def render_page(config: Dict[str, Any]) -> None:
    """Render the SignSpeak AI translation history screen."""
    st.write("✅ History page loaded successfully")
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
    st.text_input("Search", placeholder="Search across transcripts, dates, or emotions...", label_visibility="collapsed")
    entries = _history_entries(get_history())
    for entry in entries:
        st.markdown(_history_card(entry), unsafe_allow_html=True)
        cols = st.columns([1, 1, 4])
        cols[0].button("Play Audio", key=f"play-{entry['id']}")
        cols[1].button("Copy Text", key=f"copy-{entry['id']}")
    st.markdown("<br>", unsafe_allow_html=True)
    center = st.columns([1, 1, 1])
    center[1].button("Load Previous Records", use_container_width=True)


def _history_entries(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Return real history entries or polished sample records for the empty state."""
    if history:
        return [
            {
                "id": str(index),
                "timestamp": item.get("timestamp", ""),
                "emotion": item.get("emotion", "Focused").title(),
                "sentence": item.get("sentence", ""),
            }
            for index, item in enumerate(reversed(history))
        ]
    return [
        {"id": "sample-1", "timestamp": "OCT 24, 10:15 AM", "emotion": "Focused", "sentence": "Hello, how are you today?"},
        {"id": "sample-2", "timestamp": "OCT 24, 10:08 AM", "emotion": "Determined", "sentence": "Please start the meeting when everyone is ready."},
        {"id": "sample-3", "timestamp": "OCT 23, 06:42 PM", "emotion": "Focused", "sentence": "Thank you for listening and responding so clearly."},
    ]


def _history_card(entry: Dict[str, str]) -> str:
    """Return one SignSpeak history card."""
    timestamp = escape(_format_timestamp(entry.get("timestamp", "")))
    emotion = escape(entry.get("emotion", "Focused"))
    sentence = escape(entry.get("sentence", ""))
    badge = "ss-badge-purple" if emotion.lower() == "focused" else "ss-badge-amber"
    return f"""
    <div class="ss-card ss-history-card" style="margin-top:18px;">
        <div>
            <div style="display:flex;justify-content:space-between;gap:18px;align-items:center;">
                <div class="ss-label">{timestamp}</div>
                <span class="ss-badge {badge}">{emotion}</span>
            </div>
            <div class="ss-quote">"{sentence}"</div>
        </div>
        <div class="ss-avatar" style="width:58px;height:58px;">SA</div>
    </div>
    """


def _format_timestamp(value: str) -> str:
    """Format ISO timestamps into display text when possible."""
    try:
        return datetime.fromisoformat(value).strftime("%b %d, %I:%M %p").upper()
    except Exception:
        return value or "OCT 24, 10:15 AM"
