"""Streamlit session state helpers for the Sign Speech Converter app."""

from typing import Dict

import streamlit as st


def initialize_session(config: Dict) -> None:
    """Initialize session state with default values."""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "current_sentence" not in st.session_state:
        st.session_state.current_sentence = ""
    if "detected_emotion" not in st.session_state:
        st.session_state.detected_emotion = "neutral"
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False
    if "confidence_threshold" not in st.session_state:
        st.session_state.confidence_threshold = 0.75
    if "output_language" not in st.session_state:
        st.session_state.output_language = "en"
