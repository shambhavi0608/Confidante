from __future__ import annotations
import streamlit as st
from typing import Any, Dict


def initialize_session(config: Dict[str, Any]) -> None:
    defaults = {
        "current_gesture": "NOTHING",
        "current_sentence": "",
        "conversation_history": [],
        "detected_emotion": "neutral",
        "emotion_confidence": 0.0,
        "emotion_probabilities": {
            "happy": 0.0, "calm": 0.0, "neutral": 1.0,
            "sad": 0.0, "angry": 0.0, "fearful": 0.0, "disgust": 0.0
        },
        "is_recording": False,
        "confidence_threshold": 0.75,
        "output_language": "en",
        "gestures_per_minute": 0,
        "session_active": False,
        "smoothing_buffer": [],
        "last_gesture_time": 0.0,
        "audio_bytes": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_to_history(original: str, emotion: str, hindi: str = "") -> None:
    from datetime import datetime
    entry = {
        "timestamp": datetime.now().strftime("%b %d, %I:%M %p"),
        "original_text": original,
        "hindi_translation": hindi,
        "detected_emotion": emotion,
    }
    st.session_state["conversation_history"].insert(0, entry)
