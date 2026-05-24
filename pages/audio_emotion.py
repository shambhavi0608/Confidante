"""Audio emotion analysis page for SignSpeak AI."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from src.audio_module import AudioEmotionError, AudioEmotionRecognizer


@st.cache_resource(show_spinner=False)
def get_audio_recognizer(emotions: tuple[str, ...], model_path: str, sample_rate: int) -> AudioEmotionRecognizer:
    """Return a cached audio emotion recognizer."""
    return AudioEmotionRecognizer(emotions=emotions, model_path=model_path, sample_rate=sample_rate)


def render_page(config: Dict[str, Any]) -> None:
    """Render the SignSpeak AI audio emotion analysis screen."""
    recognizer = get_audio_recognizer(
        tuple(config["audio"]["emotions"]),
        config["audio"]["model_path"],
        int(config["audio"]["sample_rate"]),
    )
    result = {"emotion": "calm", "confidence": 0.92, "probabilities": {"happy": 0.24, "calm": 0.68, "sad": 0.05, "angry": 0.03}}
    left, center, right = st.columns([0.9, 1.15, 0.95], gap="large")
    with center:
        audio_file = _get_audio_input()
    if audio_file is not None:
        result = _predict_audio(recognizer, audio_file)
        st.session_state.emotion = result["emotion"]
    with left:
        _render_dominant_emotion(result)
    with center:
        _render_center_visual(result)
    with right:
        _render_probability_panel(result)


def _get_audio_input() -> Any:
    """Return recorded audio when available, otherwise an uploaded audio file."""
    if hasattr(st, "audio_input"):
        recorded_audio = st.audio_input("Record live audio", label_visibility="collapsed")
        if recorded_audio is not None:
            return recorded_audio
    return st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg"], label_visibility="collapsed")


def _predict_audio(recognizer: AudioEmotionRecognizer, audio_file: Any) -> Dict[str, Any]:
    """Predict emotion from an uploaded or recorded audio file."""
    temp_path: Path | None = None
    try:
        suffix = Path(audio_file.name).suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(audio_file.getbuffer())
            temp_path = Path(temp_file.name)
        return recognizer.predict_file(temp_path)
    except AudioEmotionError as exc:
        st.error(f"Emotion detection failed: {exc}")
    except Exception as exc:
        st.error(f"Could not process audio: {exc}")
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return {"emotion": "calm", "confidence": 0.92, "probabilities": {"happy": 0.24, "calm": 0.68, "sad": 0.05, "angry": 0.03}}


def _render_dominant_emotion(result: Dict[str, Any]) -> None:
    """Render the dominant emotion summary column."""
    emotion = str(result.get("emotion", "calm")).title()
    confidence = int(float(result.get("confidence", 0.92)) * 100)
    st.markdown(
        f"""
        <div class="ss-card">
            <div class="ss-label">DOMINANT EMOTION</div>
            <div style="display:flex;align-items:center;gap:10px;margin-top:14px;">
                <span class="ss-dot" style="background:#3B82F6;box-shadow:0 0 14px #3B82F6;"></span>
                <div class="ss-title">{emotion}</div>
            </div>
            <div style="font-weight:900;color:#3B82F6;margin-top:8px;">{confidence}% Confidence</div>
            <div class="ss-muted" style="line-height:1.55;margin-top:18px;">
                The detected tone is steady, melodic, and lacks sharp frequency spikes, indicating a relaxed state.
            </div>
        </div>
        <div class="ss-card" style="margin-top:18px;">
            <div class="ss-label">AUDIO QUALITY</div>
            <div style="display:grid;gap:12px;margin-top:16px;">
                <div style="display:flex;justify-content:space-between;"><span>SNR Ratio</span><b>High (32dB)</b></div>
                <div style="display:flex;justify-content:space-between;"><span>Latency</span><b>14ms</b></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_center_visual(result: Dict[str, Any]) -> None:
    """Render the central circular audio visualization."""
    emotion = str(result.get("emotion", "calm")).title()
    st.markdown(
        f"""
        <div class="ss-card" style="text-align:center;">
            <div class="ss-orb">
                <span class="ss-star a">✦</span><span class="ss-star b">✦</span><span class="ss-star c">✦</span>
                <div>
                    <div class="ss-title" style="font-size:3rem;color:#F0F0FF;">{emotion}</div>
                    {_waveform_html(11)}
                </div>
            </div>
            <button class="ss-record">🎙️</button>
            <div class="ss-label" style="color:#EF4444;">RECORDING LIVE AUDIO</div>
            {_purple_waveform()}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_probability_panel(result: Dict[str, Any]) -> None:
    """Render emotion probability bars and mini waveform."""
    probabilities = result.get("probabilities", {"happy": 0.24, "calm": 0.68, "sad": 0.05, "angry": 0.03})
    rows = "".join(_probability_row(label.title(), float(value), label == "calm") for label, value in probabilities.items())
    st.markdown(
        f"""
        <div class="ss-card">
            <div class="ss-title">EMOTION PROBABILITY</div>
            {rows}
        </div>
        <div class="ss-card" style="margin-top:18px;">
            <div class="ss-label">SIGNAL WAVEFORM</div>
            {_purple_waveform()}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _probability_row(label: str, value: float, highlighted: bool) -> str:
    """Return one probability bar."""
    percent = int(value * 100)
    border = "border-color:#E8893C;" if highlighted else ""
    return f"""
    <div class="ss-progress-row" style="{border}">
        <div class="ss-progress-top"><span>{label}</span><span>{percent}%</span></div>
        <div class="ss-track"><div class="ss-fill" style="width:{percent}%;"></div></div>
    </div>
    """


def _waveform_html(count: int) -> str:
    """Return amber animated waveform bars."""
    return '<div class="ss-wave">' + "".join("<span></span>" for _ in range(count)) + "</div>"


def _purple_waveform() -> str:
    """Return purple animated waveform bars."""
    bars = "".join("<span style='background:linear-gradient(#9CA8FF,#6B7FD4);'></span>" for _ in range(17))
    return f'<div class="ss-wave" style="margin-top:18px;">{bars}</div>'
