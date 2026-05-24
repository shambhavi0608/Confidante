"""Live webcam gesture detection page."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.gesture_module import GestureDetectionError, GestureRecognizer
from src.tts_module import TextToSpeechError, TextToSpeechService
from utils.session import add_gesture_token, add_history_entry, backspace_sentence, clear_sentence


@st.cache_resource(show_spinner=False)
def get_gesture_recognizer(classes: tuple[str, ...], model_path: str) -> GestureRecognizer:
    """Return a cached gesture recognizer instance."""
    return GestureRecognizer(classes=classes, model_path=model_path)


@st.cache_resource(show_spinner=False)
def get_tts_service() -> TextToSpeechService:
    """Return a cached text-to-speech service instance."""
    return TextToSpeechService()


def render_page(config: Dict[str, Any]) -> None:
    """Render webcam capture, gesture prediction, sentence controls, and speech output."""
    st.title("Live Detection")
    classes = tuple(config["gesture"]["classes"])
    recognizer = get_gesture_recognizer(classes, config["gesture"]["model_path"])
    st.session_state.smoother.update_settings(
        buffer_size=st.session_state.buffer_size,
        cooldown_seconds=st.session_state.cooldown_seconds,
        confidence_threshold=st.session_state.confidence_threshold,
    )
    if not recognizer.model:
        st.warning("Gesture model file is missing. Heuristic fallback is active.")
    image = st.camera_input("Webcam frame")
    columns = st.columns([2, 1])
    prediction = {"label": "NOTHING", "confidence": 0.0, "probabilities": {label: 0.0 for label in classes}}
    if image is not None:
        try:
            bytes_data = image.getvalue()
            frame = cv2.imdecode(np.frombuffer(bytes_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            prediction = recognizer.predict_frame(frame)
            stable_label = st.session_state.smoother.add(prediction["label"], prediction["confidence"])
            if stable_label:
                add_gesture_token(stable_label)
            columns[0].image(cv2.cvtColor(prediction["frame"], cv2.COLOR_BGR2RGB), channels="RGB", use_column_width=True)
        except GestureDetectionError as exc:
            st.error(f"Gesture detection failed: {exc}")
        except Exception as exc:
            st.error(f"Could not process webcam frame: {exc}")
    with columns[1]:
        st.metric("Gesture", prediction["label"])
        st.metric("Confidence", f"{prediction['confidence']:.0%}")
        probabilities = pd.DataFrame(
            sorted(prediction["probabilities"].items(), key=lambda item: item[1], reverse=True)[:10],
            columns=["class", "probability"],
        )
        fig = px.bar(probabilities, x="class", y="probability", range_y=[0, 1], color_discrete_sequence=["#7C3AED"])
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0D1117", plot_bgcolor="#0D1117")
        st.plotly_chart(fig, use_container_width=True)
    st.text_area("Sentence", value=st.session_state.sentence, height=120, disabled=True)
    control_columns = st.columns(4)
    if control_columns[0].button("Backspace", use_container_width=True):
        backspace_sentence()
        st.rerun()
    if control_columns[1].button("Clear", use_container_width=True):
        clear_sentence()
        st.rerun()
    if control_columns[2].button("Add space", use_container_width=True):
        add_gesture_token("SPACE")
        st.rerun()
    if control_columns[3].button("Speak", use_container_width=True, type="primary"):
        _speak_current_sentence()


def _speak_current_sentence() -> None:
    """Synthesize and play the current sentence while recording it in history."""
    sentence = str(st.session_state.get("sentence", "")).strip()
    if not sentence:
        st.info("Build a sentence before speaking.")
        return
    try:
        service = get_tts_service()
        output_path, spoken_text = service.synthesize(
            sentence,
            emotion=st.session_state.emotion,
            language=st.session_state.language,
            output_dir=Path(".streamlit_audio"),
        )
        st.audio(str(output_path), format="audio/mp3")
        add_history_entry(sentence, st.session_state.emotion, st.session_state.language, spoken_text)
    except TextToSpeechError as exc:
        st.error(f"Speech synthesis failed: {exc}")
