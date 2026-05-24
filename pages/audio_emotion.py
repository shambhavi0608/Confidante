"""Audio emotion detection page."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import streamlit as st

from src.audio_module import AudioEmotionError, AudioEmotionRecognizer


@st.cache_resource(show_spinner=False)
def get_audio_recognizer(emotions: tuple[str, ...], model_path: str, sample_rate: int) -> AudioEmotionRecognizer:
    """Return a cached audio emotion recognizer."""
    return AudioEmotionRecognizer(emotions=emotions, model_path=model_path, sample_rate=sample_rate)


def render_page(config: Dict[str, Any]) -> None:
    """Render audio upload, emotion classification, and probability chart."""
    st.title("Audio Emotion")
    audio_config = config["audio"]
    recognizer = get_audio_recognizer(
        tuple(audio_config["emotions"]),
        audio_config["model_path"],
        int(audio_config["sample_rate"]),
    )
    if not recognizer.model:
        st.warning("Emotion model file is missing. Heuristic fallback is active.")
    audio_file = _get_audio_input()
    if audio_file is None:
        st.info("Upload a short speech clip to detect emotion.")
        return
    st.audio(audio_file)
    temp_path: Path | None = None
    try:
        suffix = Path(audio_file.name).suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(audio_file.getbuffer())
            temp_path = Path(temp_file.name)
        result = recognizer.predict_file(temp_path)
        st.session_state.emotion = result["emotion"]
        st.metric("Detected emotion", result["emotion"].title())
        st.metric("Confidence", f"{result['confidence']:.0%}")
        probabilities = pd.DataFrame(result["probabilities"].items(), columns=["emotion", "probability"])
        fig = px.bar(probabilities, x="emotion", y="probability", range_y=[0, 1], color_discrete_sequence=["#059669"])
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0D1117", plot_bgcolor="#0D1117")
        st.plotly_chart(fig, use_container_width=True)
    except AudioEmotionError as exc:
        st.error(f"Emotion detection failed: {exc}")
    except Exception as exc:
        st.error(f"Could not process audio: {exc}")
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _get_audio_input() -> Any:
    """Return recorded audio when available, otherwise return an uploaded audio file."""
    if hasattr(st, "audio_input"):
        recorded_audio = st.audio_input("Record audio")
        if recorded_audio is not None:
            return recorded_audio
    return st.file_uploader("Upload WAV/MP3 audio", type=["wav", "mp3", "m4a", "ogg"])
