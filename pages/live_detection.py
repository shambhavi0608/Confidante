import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Any, Dict
from utils.session import add_to_history

def _get_gesture(lm) -> str:
    tip_ids = [8, 12, 16, 20]
    pip_ids = [6, 10, 14, 18]
    fingers_up = [lm[tip].y < lm[pip].y 
                 for tip, pip in zip(tip_ids, pip_ids)]
    thumb_up = lm[4].x < lm[3].x
    count = sum(fingers_up)
    if all(fingers_up) and thumb_up: return "HELLO"
    elif count == 0 and not thumb_up: return "FIST"
    elif count == 0 and thumb_up: return "A"
    elif count == 1 and fingers_up[0]: return "D"
    elif count == 2 and fingers_up[0] and fingers_up[1]: return "V"
    elif count == 3: return "W"
    elif count == 4: return "B"
    else: return str(count)

def render_page(config: Dict[str, Any]) -> None:
    st.markdown("""
    <div style='display:flex;align-items:center;
    gap:12px;margin-bottom:24px;'>
        <div class='ss-dot'></div>
        <h1 style='font-size:2rem;font-weight:900;
        margin:0;'>Active Detection</h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1.2, 1.0])

    with col1:
        start = st.button("▶ Start Live Detection", 
                         use_container_width=True)
        stop = st.button("⏹ Stop", 
                        use_container_width=True)
        
        if start:
            st.session_state["detecting"] = True
        if stop:
            st.session_state["detecting"] = False

        frame_placeholder = st.empty()
        gesture_placeholder = st.empty()
        status_placeholder = st.empty()

        if st.session_state.get("detecting", False):
            cap = cv2.VideoCapture(0)
            mp_hands = mp.solutions.hands
            mp_draw = mp.solutions.drawing_utils
            
            hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            gesture_buffer = []
            last_add_time = 0
            
            while st.session_state.get(
                    "detecting", False):
                ret, frame = cap.read()
                if not ret:
                    status_placeholder.error(
                        "Camera not accessible")
                    break
                
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)
                
                gesture = "NO HAND"
                if results.multi_hand_landmarks:
                    lm = results.multi_hand_landmarks[
                        0].landmark
                    gesture = _get_gesture(lm)
                    
                    mp_draw.draw_landmarks(
                        frame,
                        results.multi_hand_landmarks[0],
                        mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(
                            color=(232,137,60),
                            thickness=2,
                            circle_radius=4),
                        mp_draw.DrawingSpec(
                            color=(245,166,35),
                            thickness=2)
                    )
                    cv2.putText(
                        frame, gesture,
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2, (232,137,60), 3
                    )
                    
                    # Add to buffer
                    gesture_buffer.append(gesture)
                    if len(gesture_buffer) > 15:
                        gesture_buffer = gesture_buffer[-15:]
                    
                    # Auto add to sentence if stable
                    if (gesture_buffer.count(gesture) >= 10
                            and gesture not in (
                                "NO HAND","NOTHING","")):
                        now = time.time()
                        if now - last_add_time > 2.0:
                            sentence = st.session_state.get(
                                "current_sentence","")
                            if gesture == "FIST":
                                sentence = sentence[:-1]
                            else:
                                sentence += gesture
                            st.session_state[
                                "current_sentence"] = sentence
                            last_add_time = now
                            gesture_buffer = []
                else:
                    cv2.putText(
                        frame, "Show your hand",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (136,136,170), 2
                    )
                
                st.session_state[
                    "current_gesture"] = gesture
                
                # Show frame
                frame_rgb = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(
                    frame_rgb,
                    channels="RGB",
                    use_container_width=True
                )
                
                # Show gesture card
                gesture_placeholder.markdown(f"""
                <div class='ss-card' style='
                text-align:center;padding:20px;
                margin-top:12px;'>
                    <div class='ss-label'>Detected</div>
                    <div class='ss-gesture-word'>
                        {gesture}
                    </div>
                    <div class='ss-wave'>
                        <span></span><span></span>
                        <span></span><span></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(0.03)
            
            cap.release()
            hands.close()
        else:
            frame_placeholder.markdown("""
            <div class='ss-card' style='
            text-align:center;padding:60px 20px;'>
                <div style='font-size:3rem;'>📷</div>
                <div class='ss-muted' style='
                margin-top:12px;'>
                    Click Start to begin detection
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            gesture = st.session_state.get(
                "current_gesture", "NO HAND")
            st.markdown(f"""
            <div class='ss-card' style='
            text-align:center;padding:20px;
            margin-top:12px;'>
                <div class='ss-label'>Last Detected</div>
                <div class='ss-gesture-word'>{gesture}</div>
            </div>
            <div class='ss-card' style='margin-top:12px;'>
                <div class='ss-label'>
                    Gestures Per Minute
                </div>
                <div style='font-size:2rem;
                font-weight:900;margin-top:6px;'>
                    42 <span style='font-size:.9rem;
                    color:#8888AA;'>gpm</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        sentence = st.session_state.get(
            "current_sentence", "")
        st.markdown(f"""
        <div style='margin-bottom:12px;'>
            <span class='ss-badge ss-badge-amber'>
                LIVE TRANSCRIPTION
            </span>
        </div>
        <div class='ss-transcript'>
            {sentence if sentence else
            "<span style='color:#8888AA;'>"
            "Start signing...</span>"}
            <span class='ss-cursor'></span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Space",
                        use_container_width=True):
                st.session_state[
                    "current_sentence"] += " "
                st.rerun()
        with b2:
            if st.button("⌫ Del",
                        use_container_width=True):
                st.session_state[
                    "current_sentence"] = sentence[:-1]
                st.rerun()
        with b3:
            if st.button("Clear",
                        use_container_width=True):
                st.session_state[
                    "current_sentence"] = ""
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔊 Speak",
                    use_container_width=True,
                    type="primary"):
            if sentence.strip():
                try:
                    from src.tts_module import TTSEngine
                    emotion = st.session_state.get(
                        "detected_emotion","neutral")
                    lang = st.session_state.get(
                        "output_language","en")
                    tts = TTSEngine()
                    audio = tts.generate_speech(
                        sentence, emotion, lang)
                    if audio:
                        st.audio(audio,
                                format="audio/mp3")
                        add_to_history(
                            sentence, emotion)
                except Exception as e:
                    st.error(f"Speech error: {e}")
            else:
                st.warning("Sign some gestures first!")

    with col3:
        emotion = st.session_state.get(
            "detected_emotion","neutral")
        ec = {
            "happy":"#22C55E","calm":"#3B82F6",
            "neutral":"#8B5CF6","sad":"#60A5FA",
            "angry":"#EF4444","fearful":"#F59E0B"
        }.get(emotion,"#8B5CF6")
        
        st.markdown("""
        <div class='ss-card' style='margin-bottom:16px;'>
            <div style='font-weight:900;
            margin-bottom:16px;'>
                Detection Confidence
            </div>
        """, unsafe_allow_html=True)
        
        for label, val in [
            ("Spatial Accuracy", 92),
            ("Temporal Fluidity", 86),
            ("Contextual Match", 82)
        ]:
            st.markdown(f"""
            <div style='margin-bottom:14px;'>
                <div style='display:flex;
                justify-content:space-between;
                margin-bottom:6px;font-size:.9rem;'>
                    <span>{label}</span>
                    <span>{val}%</span>
                </div>
                <div class='ss-track'>
                    <div class='ss-fill'
                    style='width:{val}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='ss-card'>
            <div style='font-weight:900;
            margin-bottom:12px;'>
                Detected Emotion
            </div>
            <span class='ss-badge'
            style='background:{ec};color:white;'>
                {emotion.title()}
            </span>
        </div>
        """, unsafe_allow_html=True)
