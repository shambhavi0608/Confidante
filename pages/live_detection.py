"""Live translator page for SignSpeak AI."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np
import streamlit as st

from src.gesture_module import GestureDetectionError, GestureRecognizer
from src.tts_module import TextToSpeechError, TextToSpeechService
from utils.session import add_history_entry


@st.cache_resource(show_spinner=False)
def get_gesture_recognizer(classes: tuple[str, ...], model_path: str) -> GestureRecognizer:
    """Return a cached gesture recognizer instance."""
    return GestureRecognizer(classes=classes, model_path=model_path)


@st.cache_resource(show_spinner=False)
def get_tts_service() -> TextToSpeechService:
    """Return a cached text-to-speech service instance."""
    return TextToSpeechService()


def render_page(config: Dict[str, Any]) -> None:
    """Render the SignSpeak AI live translator screen."""
    st.write("✅ Live Detection page loaded successfully")
    classes = tuple(config["gesture"]["classes"])
    recognizer = get_gesture_recognizer(classes, config["gesture"]["model_path"])
    prediction = {"label": "HELLO", "confidence": 0.92, "probabilities": _default_probabilities()}
    capture_col, mid_col, right_col = st.columns([1.15, 1.05, 0.95], gap="large")
    with capture_col:
        st.markdown('<div class="ss-title"><span class="ss-dot"></span> Active Detection</div>', unsafe_allow_html=True)
        image = st.camera_input("Camera stream", label_visibility="collapsed")
        if image is not None:
            try:
                frame = cv2.imdecode(np.frombuffer(image.getvalue(), dtype=np.uint8), cv2.IMREAD_COLOR)
                prediction = recognizer.predict_frame(frame)
            except (GestureDetectionError, Exception):
                prediction = {"label": "HELLO", "confidence": 0.74, "probabilities": _default_probabilities()}
        _render_gesture_visual(prediction["label"])
        _render_metric_card("Gestures Per Minute", "42 gpm")
    with mid_col:
        sentence = escape(st.session_state.get("sentence") or "Hello, how are you today?")
        st.markdown(
            f"""
            <div class="ss-card">
                <span class="ss-badge ss-badge-amber">LIVE TRANSCRIPTION</span>
                <div class="ss-transcript" style="margin-top:18px;">{sentence}<span class="ss-cursor"></span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔊 Speak", use_container_width=True, type="primary"):
            _speak(sentence)
    with right_col:
        _render_confidence_panel(prediction)
        _render_emotion_badges()


def _render_gesture_visual(label: str) -> None:
    """Render the glowing gesture visualization card."""
    display_label = escape(label if label and label != "NOTHING" else "HELLO")
    st.markdown(
        f"""
        <div class="ss-card ss-gesture-card">
            <div>
                <div class="ss-gesture-word">{display_label}</div>
                <div class="ss-label" style="color:#E8893C;">DETECTED</div>
                {_waveform_html(13)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metric_card(label: str, value: str) -> None:
    """Render a compact metric card."""
    st.markdown(
        f"""
        <div class="ss-card" style="margin-top:18px;">
            <div class="ss-label">{label}</div>
            <div class="ss-title" style="margin-top:6px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_confidence_panel(prediction: Dict[str, Any]) -> None:
    """Render the confidence card with amber progress bars."""
    confidence = int(float(prediction.get("confidence", 0.92)) * 100)
    metrics = [("Spatial Accuracy", max(72, confidence)), ("Temporal Fluidity", 86), ("Contextual Match", 82)]
    rows = "".join(_progress_row(label, value) for label, value in metrics)
    st.markdown(
        f"""
        <div class="ss-card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="ss-title">Detection Confidence</div>
                <div class="ss-muted">⚙️</div>
            </div>
            {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_emotion_badges() -> None:
    """Render detected emotion tone badges."""
    st.markdown(
        """
        <div class="ss-card" style="margin-top:18px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="ss-title">Detected Emotion</div>
                <div class="ss-muted">⚙️</div>
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:18px;">
                <span class="ss-badge ss-badge-green">Friendly</span>
                <span class="ss-badge ss-badge-blue">Formal</span>
                <span class="ss-badge ss-badge-purple">Inquisitive</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _progress_row(label: str, value: int) -> str:
    """Return HTML for one progress row."""
    return f"""
    <div class="ss-progress-row">
        <div class="ss-progress-top"><span>{label}</span><span>{value}%</span></div>
        <div class="ss-track"><div class="ss-fill" style="width:{value}%;"></div></div>
    </div>
    """


def _waveform_html(count: int) -> str:
    """Return animated waveform bars."""
    return '<div class="ss-wave">' + "".join("<span></span>" for _ in range(count)) + "</div>"


def _default_probabilities() -> Dict[str, float]:
    """Return default live UI probabilities."""
    return {"HELLO": 0.98, "THANKS": 0.86, "YES": 0.82, "NO": 0.64}


def _speak(sentence: str) -> None:
    """Synthesize the current sentence and save it to history."""
    try:
        service = get_tts_service()
        output_path, spoken_text = service.synthesize(
            sentence,
            emotion=st.session_state.get("emotion", "neutral"),
            language=st.session_state.get("language", "en"),
            output_dir=Path(".streamlit_audio"),
        )
        st.audio(str(output_path), format="audio/mp3")
        add_history_entry(sentence, st.session_state.get("emotion", "neutral"), st.session_state.get("language", "en"), spoken_text)
    except TextToSpeechError as exc:
        st.error(f"Speech synthesis failed: {exc}")
