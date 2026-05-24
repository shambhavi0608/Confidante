"""Audio emotion detection page."""

from __future__ import annotations

from html import escape
import tempfile
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    input_column, result_column = st.columns([1.1, 1], gap="large")
    with input_column:
        st.markdown(
            """
            <div class="ssc-card">
                <div class="ssc-card-label">Voice capture</div>
                <div style="font-size:1.35rem;font-weight:900;color:#F5F0FF;">Emotion sensor</div>
                <div class="ssc-muted" style="margin-top:0.45rem;">Record or upload a short speech sample.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        audio_file = _get_audio_input()
        if audio_file is not None:
            st.audio(audio_file)
    if audio_file is None:
        with result_column:
            _render_emotion_card("neutral", 0.0)
        return
    temp_path: Path | None = None
    try:
        suffix = Path(audio_file.name).suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(audio_file.getbuffer())
            temp_path = Path(temp_file.name)
        result = recognizer.predict_file(temp_path)
        st.session_state.emotion = result["emotion"]
        with result_column:
            _render_emotion_card(result["emotion"], result["confidence"])
            st.plotly_chart(_build_emotion_chart(result["probabilities"]), use_container_width=True)
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


def _render_emotion_card(emotion: str, confidence: float) -> None:
    """Render the current emotion as a color-coded badge card."""
    badge_class = f"ssc-badge-{emotion.lower()}"
    safe_emotion = escape(emotion.title())
    st.markdown(
        f"""
        <div class="ssc-card">
            <div class="ssc-card-label">Emotion aura</div>
            <div class="ssc-emotion-orb ssc-emotion-{emotion.lower()}">
                <div>
                    <span class="ssc-badge {badge_class}">{safe_emotion}</span>
                    <div style="font-size:2.4rem;font-weight:950;margin-top:0.8rem;color:#F5F0FF;">{confidence:.0%}</div>
                    <div class="ssc-muted" style="font-weight:800;">confidence</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_emotion_chart(probabilities: Dict[str, float]) -> go.Figure:
    """Build an animated-style emotion probability chart using Plotly transitions."""
    emotion_colors = {
        "happy": "#39D98A",
        "sad": "#5AA7FF",
        "angry": "#FF5E6C",
        "neutral": "#8B8494",
    }
    frame = pd.DataFrame(probabilities.items(), columns=["emotion", "probability"])
    colors = [emotion_colors.get(emotion, "#9B6DFF") for emotion in frame["emotion"]]
    fig = px.bar(frame, x="emotion", y="probability", range_y=[0, 1])
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="%{x}: %{y:.0%}<extra></extra>",
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font={"color": "#F5F0FF"},
        margin={"l": 10, "r": 10, "t": 28, "b": 10},
        title={"text": "Probability spectrum", "font": {"size": 16, "color": "#F5F0FF"}},
        transition={"duration": 650, "easing": "cubic-in-out"},
        bargap=0.32,
    )
    return fig
