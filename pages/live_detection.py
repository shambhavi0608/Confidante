"""Live webcam gesture detection page."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np
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
    top_columns = st.columns([1.05, 1], gap="large")
    prediction = {"label": "NOTHING", "confidence": 0.0, "probabilities": {label: 0.0 for label in classes}}
    with top_columns[0]:
        image = st.camera_input("Webcam frame")
        if image is not None:
            try:
                bytes_data = image.getvalue()
                frame = cv2.imdecode(np.frombuffer(bytes_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                prediction = recognizer.predict_frame(frame)
                stable_label = st.session_state.smoother.add(prediction["label"], prediction["confidence"])
                if stable_label:
                    add_gesture_token(stable_label)
                st.image(
                    cv2.cvtColor(prediction["frame"], cv2.COLOR_BGR2RGB),
                    channels="RGB",
                    use_container_width=True,
                )
            except GestureDetectionError as exc:
                st.error(f"Gesture detection failed: {exc}")
            except Exception as exc:
                st.error(f"Could not process webcam frame: {exc}")
    with top_columns[1]:
        _render_gesture_card(prediction["label"], prediction["confidence"])
        _render_confidence_bars(prediction["probabilities"])
    sentence_text = escape(st.session_state.sentence or "Sentence will appear here.")
    st.markdown(
        f"""
        <div class="ssc-card" style="margin-top:1rem;box-shadow:0 0 38px rgba(232,137,60,0.18);">
            <div class="ssc-card-label">Current sentence</div>
            <div class="ssc-sentence">{sentence_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
    if control_columns[3].button("Speak sentence", use_container_width=True, type="primary"):
        _speak_current_sentence()


def _render_gesture_card(label: str, confidence: float) -> None:
    """Render the large gesture display card."""
    safe_label = escape(label)
    st.markdown(
        f"""
        <div class="ssc-card ssc-gesture-dial-card">
            <div class="ssc-card-label">Gesture dial</div>
            <div class="ssc-gesture-dial">
                <div class="ssc-gesture-dial-inner">
                    <div class="ssc-gesture-value">{safe_label}</div>
                    <div class="ssc-confidence-text">{confidence:.0%} confidence</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_confidence_bars(probabilities: Dict[str, float]) -> None:
    """Render animated gradient confidence bars for top gesture classes."""
    rows = []
    for label, probability in sorted(probabilities.items(), key=lambda item: item[1], reverse=True)[:7]:
        safe_label = escape(label)
        width = max(2.0, min(100.0, probability * 100.0))
        rows.append(
            f"""
            <div class="ssc-confidence-row">
                <div class="ssc-muted" style="font-weight:800;">{safe_label}</div>
                <div class="ssc-confidence-track">
                    <div class="ssc-confidence-fill" style="width:{width:.2f}%;"></div>
                </div>
                <div style="font-weight:850;color:#F5F0FF;">{probability:.0%}</div>
            </div>
            """
        )
    st.markdown(
        f"""
        <div class="ssc-card" style="margin-top:1rem;">
            <div class="ssc-card-label">Confidence field</div>
            <div class="ssc-confidence-list">{''.join(rows)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
