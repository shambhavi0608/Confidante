from __future__ import annotations

from typing import Any, Dict

import streamlit as st


def render_page(config: Dict[str, Any]) -> None:
    col1, col2, col3 = st.columns([1.5, 1.2, 1.0])

    with col1:
        st.caption("📸 Position hand clearly → click Take Photo")
        frame = st.camera_input("", label_visibility="collapsed", key="main_cam")
        
        current_gesture = st.session_state.get("current_gesture", "READY")
        detected_hand = False
        
        if frame is not None:
            try:
                from PIL import Image
                import io, numpy as np, mediapipe as mp
                img = Image.open(io.BytesIO(frame.getvalue())).convert("RGB")
                frame_rgb = np.array(img)
                with mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.45) as hands:
                    results = hands.process(frame_rgb)
                if results.multi_hand_landmarks:
                    detected_hand = True
                    lm = results.multi_hand_landmarks[0].landmark
                    tips = [8,12,16,20]; pips = [6,10,14,18]
                    fu = [lm[t].y < lm[p].y for t,p in zip(tips,pips)]
                    thumb = lm[4].x < lm[3].x
                    n = sum(fu)
                    if all(fu) and thumb: g = "HELLO"
                    elif n==0 and not thumb: g = "FIST"
                    elif n==0 and thumb: g = "A"
                    elif n==1 and fu[0]: g = "D"
                    elif n==2 and fu[0] and fu[1]: g = "V"
                    elif n==3: g = "W"
                    elif n==4: g = "B"
                    else: g = str(n)
                    st.session_state["current_gesture"] = g
                    current_gesture = g
                    st.success(f"Hand detected → {g}")
                else:
                    st.session_state["current_gesture"] = "NO HAND"
                    current_gesture = "NO HAND"
                    st.info("No hand found. Try better lighting.")
            except Exception as e:
                st.error(f"Detection error: {e}")
        
        st.markdown(f"""
        <div class='ss-card ss-gesture-card' style='margin-top:14px;'>
            <div style='text-align:center;'>
                <div class='ss-label'>Detected</div>
                <div class='ss-gesture-word'>{current_gesture}</div>
                <div class='ss-label' style='margin-top:6px;'>GESTURE</div>
                <div class='ss-wave' style='justify-content:center;margin-top:10px;'>
                    <span></span><span></span><span></span><span></span><span></span>
                </div>
            </div>
        </div>
        <div class='ss-card' style='margin-top:12px;'>
            <div class='ss-label'>Gestures Per Minute</div>
            <div style='font-size:2rem;font-weight:900;margin-top:6px;color:#F0F0FF;'>42 <span style='font-size:.85rem;color:#8888AA;'>gpm</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Add to Sentence", use_container_width=True):
            g = st.session_state.get("current_gesture","")
            if g not in ("NO HAND","NOTHING","READY",""):
                st.session_state["current_sentence"] = st.session_state.get("current_sentence","") + g
                st.rerun()

    with col2:
        sentence = st.session_state.get("current_sentence","")
        st.markdown(f"""
        <div style='margin-bottom:12px;'><span class='ss-badge ss-badge-amber'>LIVE TRANSCRIPTION</span></div>
        <div class='ss-transcript'>
            {sentence if sentence else "<span style='color:#8888AA;'>Start signing to build your sentence...</span>"}
            <span class='ss-cursor'></span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        b1,b2,b3 = st.columns(3)
        with b1:
            if st.button("Space", use_container_width=True): st.session_state["current_sentence"] = st.session_state.get("current_sentence","") + " "; st.rerun()
        with b2:
            if st.button("⌫ Del", use_container_width=True): st.session_state["current_sentence"] = sentence[:-1]; st.rerun()
        with b3:
            if st.button("Clear", use_container_width=True): st.session_state["current_sentence"] = ""; st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔊 Speak", use_container_width=True, type="primary"):
            if sentence.strip():
                try:
                    from src.tts_module import TTSEngine
                    from utils.session import add_to_history
                    emotion = st.session_state.get("detected_emotion","neutral")
                    lang = st.session_state.get("output_language","en")
                    audio = TTSEngine().generate_speech(sentence, emotion, lang)
                    if audio: st.audio(audio, format="audio/mp3"); add_to_history(sentence, emotion)
                except Exception as e: st.error(f"Speech error: {e}")
            else: st.warning("Sign some gestures first!")

    with col3:
        emotion = st.session_state.get("detected_emotion","neutral")
        ec = {"happy":"#22C55E","calm":"#3B82F6","neutral":"#8B5CF6","sad":"#60A5FA","angry":"#EF4444","fearful":"#F59E0B"}.get(emotion,"#8B5CF6")
        st.markdown("<div class='ss-card' style='margin-bottom:16px;'><div style='font-weight:900;margin-bottom:16px;'>Detection Confidence</div>", unsafe_allow_html=True)
        for label, val in [("Spatial Accuracy",92),("Temporal Fluidity",86),("Contextual Match",82)]:
            st.markdown(f"<div class='ss-progress-row'><div class='ss-progress-top'><span>{label}</span><span>{val}%</span></div><div class='ss-track'><div class='ss-fill' style='width:{val}%;'></div></div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ss-card'><div style='font-weight:900;margin-bottom:12px;'>Detected Emotion</div><span class='ss-badge' style='background:{ec};color:white;'>{emotion.title()}</span>&nbsp;<span class='ss-badge ss-badge-blue'>Formal</span>&nbsp;<span class='ss-badge ss-badge-purple'>Inquisitive</span></div>", unsafe_allow_html=True)
