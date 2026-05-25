"""Translation History page for SignSpeak AI."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from typing import Any, Dict


def render_page(config: Dict[str, Any]) -> None:
    history = st.session_state.get("conversation_history", [])
    count = len(history)

    st.markdown(f"""
    <h1 style='font-size:2.2rem;font-weight:900;margin-bottom:4px;'>Translation History</h1>
    <p class='ss-muted' style='margin-bottom:24px;'>{count} saved records</p>
    """, unsafe_allow_html=True)

    search = st.text_input("", placeholder="Search across transcripts, dates, or emotions...")

    if count == 0:
        st.markdown("""
        <div class='ss-card' style='text-align:center;padding:60px 20px;'>
            <div style='font-size:3rem;margin-bottom:16px;'>🤟</div>
            <div class='ss-title'>No conversations yet</div>
            <div class='ss-muted' style='margin-top:8px;'>Start detecting gestures to build your history</div>
        </div>
        """, unsafe_allow_html=True)
        return

    emotion_colors = {
        "happy": "#22C55E", "calm": "#3B82F6", "neutral": "#8B5CF6",
        "sad": "#60A5FA", "angry": "#EF4444", "fearful": "#F59E0B",
        "disgust": "#EC4899", "focused": "#8B5CF6", "determined": "#E8893C",
    }

    filtered = [
        e for e in history
        if search.lower() in e.get("original_text", "").lower()
        or search.lower() in e.get("detected_emotion", "").lower()
        or search.lower() in e.get("timestamp", "").lower()
    ] if search else history

    for i, entry in enumerate(filtered):
        emotion = entry.get("detected_emotion", "neutral").lower()
        color = emotion_colors.get(emotion, "#8B5CF6")
        timestamp = entry.get("timestamp", "")
        text = entry.get("original_text", "")
        hindi = entry.get("hindi_translation", "")

        st.markdown(f"""
        <div class='ss-card' style='margin-bottom:12px;'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>
                <span class='ss-muted' style='font-size:.82rem;'>{timestamp}</span>
                <span class='ss-badge' style='background:{color};color:white;'>{emotion.title()}</span>
            </div>
            <div class='ss-quote'>"{text}"</div>
            {f'<div class="ss-muted" style="font-size:.9rem;margin-top:6px;">🇮🇳 {hindi}</div>' if hindi else ''}
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("▶ Play Audio", key=f"play_{i}"):
                try:
                    from src.tts_module import TTSEngine
                    tts = TTSEngine()
                    audio = tts.generate_speech(text, emotion, "en")
                    if audio:
                        st.audio(audio, format="audio/mp3")
                except Exception as e:
                    st.error(f"Audio error: {e}")
        with col2:
            st.code(text, language=None)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if filtered:
            df = pd.DataFrame(filtered)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ Export CSV",
                data=csv,
                file_name="signspeak_history.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with col2:
        if st.button("🗑 Clear History", use_container_width=True):
            st.session_state["conversation_history"] = []
            st.rerun()
