"""Conversation history page."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import streamlit as st

from utils.session import get_history


def render_page(config: Dict[str, Any]) -> None:
    """Render the conversation history table and CSV export control."""
    st.title("History")
    history = get_history()
    if not history:
        st.info("No conversation history yet.")
        return
    frame = pd.DataFrame(history)
    st.dataframe(frame, use_container_width=True, hide_index=True)
    csv_bytes = frame.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Export CSV",
        data=csv_bytes,
        file_name="sign_speech_history.csv",
        mime="text/csv",
        use_container_width=True,
    )
