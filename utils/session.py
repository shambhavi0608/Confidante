"""Streamlit session state helpers for the Sign Speech Converter app."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

from src.nlp_module import SentenceBuilder
from utils.smoothing import MajorityVoteSmoother


def initialize_session(config: Dict[str, Any]) -> None:
    """Populate Streamlit session state with all required application keys."""
    smoothing_config = config.get("smoothing", {})
    nlp_config = config.get("nlp", {})
    defaults: Dict[str, Any] = {
        "history": [],
        "sentence": "",
        "emotion": "neutral",
        "language": config.get("app", {}).get("default_language", "en"),
        "confidence_threshold": float(smoothing_config.get("confidence_threshold", 0.75)),
        "buffer_size": int(smoothing_config.get("buffer_size", 7)),
        "cooldown_seconds": float(smoothing_config.get("cooldown_seconds", 1.5)),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    if "builder" not in st.session_state:
        st.session_state.builder = SentenceBuilder(word_limit=int(nlp_config.get("word_limit", 50)))
    if "smoother" not in st.session_state:
        st.session_state.smoother = MajorityVoteSmoother(
            buffer_size=st.session_state.buffer_size,
            cooldown_seconds=st.session_state.cooldown_seconds,
            confidence_threshold=st.session_state.confidence_threshold,
        )


def sync_sentence_from_builder() -> str:
    """Copy the sentence builder text into session state and return it."""
    st.session_state.sentence = st.session_state.builder.text
    return str(st.session_state.sentence)


def add_gesture_token(token: str) -> str:
    """Apply a gesture token to the sentence builder and return the sentence."""
    st.session_state.builder.add_token(token)
    return sync_sentence_from_builder()


def clear_sentence() -> str:
    """Clear the current sentence and return an empty string."""
    st.session_state.builder.clear()
    return sync_sentence_from_builder()


def backspace_sentence() -> str:
    """Remove the latest sentence token and return the updated sentence."""
    st.session_state.builder.backspace()
    return sync_sentence_from_builder()


def add_history_entry(sentence: str, emotion: str, language: str, spoken_text: str = "") -> None:
    """Append a conversation item to session history."""
    if not sentence.strip():
        return
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "sentence": sentence.strip(),
        "emotion": emotion,
        "language": language,
        "spoken_text": spoken_text.strip(),
    }
    st.session_state.history.append(entry)


def get_history() -> List[Dict[str, str]]:
    """Return conversation history as a list of dictionaries."""
    return list(st.session_state.get("history", []))
