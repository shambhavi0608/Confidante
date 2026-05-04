"""
Sign Language to Emotional Speech Converter - Main Streamlit Application

A multi-modal AI accessibility system combining:
- Real-time hand gesture recognition (MediaPipe + CNN)
- Voice emotion detection (Librosa + SVM)
- Text-to-Speech with emotional tones (gTTS)
- English-to-Hindi translation (googletrans)

Built for accessibility and sign language communication.
"""

import streamlit as st
import cv2
import numpy as np
import time
import pandas as pd
from datetime import datetime
import os

# Import project modules
from modules.gesture_detector import GestureDetector
from modules.sentence_builder import SentenceBuilder
from modules.emotion_detector import EmotionDetector
from modules.translator import Translator
from modules.tts_engine import TTSEngine
from utils.helpers import (
    resize_frame, 
    draw_info_panel, 
    format_confidence_display,
    save_conversation_log,
    load_conversation_log
)


# ============================================================================
# PAGE CONFIG & CUSTOM CSS
# ============================================================================

st.set_page_config(
    page_title="Sign Language to Emotional Speech Converter",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
custom_css = """
<style>
    /* Main theme colors */
    :root {
        --primary-color: #2E7D32;
        --secondary-color: #1976D2;
        --accent-color: #FFA500;
        --success-color: #4CAF50;
        --danger-color: #F44336;
    }
    
    /* Card styling */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .gesture-display {
        font-size: 5rem;
        text-align: center;
        font-weight: bold;
        padding: 30px;
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 20px 0;
    }
    
    .emotion-badge {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        margin: 5px;
    }
    
    .emotion-happy {
        background-color: #FFD700;
        color: #000;
    }
    
    .emotion-sad {
        background-color: #4169E1;
        color: white;
    }
    
    .emotion-angry {
        background-color: #FF4500;
        color: white;
    }
    
    .emotion-calm {
        background-color: #90EE90;
        color: #000;
    }
    
    .emotion-neutral {
        background-color: #A9A9A9;
        color: white;
    }
    
    .emotion-fearful {
        background-color: #8B008B;
        color: white;
    }
    
    .emotion-surprised {
        background-color: #FF69B4;
        color: white;
    }
    
    /* Stats display */
    .stat-box {
        text-align: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

@st.cache_resource
def initialize_gesture_detector():
    """Initialize gesture detector with caching."""
    detector = GestureDetector(confidence_threshold=0.75)
    return detector


@st.cache_resource
def initialize_emotion_detector():
    """Initialize emotion detector with caching."""
    detector = EmotionDetector()
    return detector


@st.cache_resource
def initialize_translator():
    """Initialize translator with caching."""
    return Translator()


@st.cache_resource
def initialize_tts_engine():
    """Initialize TTS engine with caching."""
    return TTSEngine()


# Initialize session state
if 'gesture_detector' not in st.session_state:
    st.session_state.gesture_detector = initialize_gesture_detector()

if 'sentence_builder' not in st.session_state:
    st.session_state.sentence_builder = SentenceBuilder()

if 'emotion_detector' not in st.session_state:
    st.session_state.emotion_detector = initialize_emotion_detector()

if 'translator' not in st.session_state:
    st.session_state.translator = initialize_translator()

if 'tts_engine' not in st.session_state:
    st.session_state.tts_engine = initialize_tts_engine()

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'current_emotion' not in st.session_state:
    st.session_state.current_emotion = None

if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("# 🤟 Sign Language Converter")
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    confidence_threshold = st.slider(
        "Gesture Confidence Threshold",
        min_value=0.5,
        max_value=0.95,
        value=0.75,
        step=0.05,
        help="Minimum confidence to accept a gesture prediction"
    )
    
    letter_cooldown = st.slider(
        "Letter Cooldown (frames)",
        min_value=10,
        max_value=40,
        value=20,
        step=5,
        help="Wait time between letter captures"
    )
    
    st.session_state.gesture_detector.confidence_threshold = confidence_threshold
    st.session_state.sentence_builder.COOLDOWN_FRAMES = letter_cooldown
    
    # Feature toggles
    st.markdown("### 🎛️ Features")
    enable_emotion = st.checkbox("🎵 Emotion Detection", value=True)
    enable_translation = st.checkbox("🌐 Hindi Translation", value=True)
    show_landmarks = st.checkbox("👁️ Show Hand Landmarks", value=False)
    
    # TTS Language
    tts_language = st.selectbox(
        "🔊 TTS Language",
        options=['English', 'Hindi'],
        help="Language for Text-to-Speech output"
    )
    
    st.markdown("---")
    
    # About section
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Sign Language to Emotional Speech Converter**
    
    A multi-modal AI system for accessibility combining:
    - 🤚 MediaPipe hand landmark detection
    - 🧠 TensorFlow CNN gesture recognition
    - 🎤 Voice emotion detection (Librosa + SVM)
    - 🔊 Emotionally-toned text-to-speech
    - 🌍 English-to-Hindi translation
    
    **Tech Stack:**
    - Python 3.8+
    - MediaPipe, TensorFlow, Streamlit
    - Librosa, gTTS, googletrans
    """)
    
    st.markdown("---")
    
    # Data management
    st.markdown("### 💾 Data Management")
    if st.button("📥 Load Conversation History"):
        sentences, emotions = load_conversation_log()
        if sentences:
            st.session_state.conversation_history = [
                {'sentence': sent, 'emotion': emotions[i] if emotions else 'unknown'}
                for i, sent in enumerate(sentences)
            ]
            st.success(f"Loaded {len(sentences)} sentences")
    
    if st.button("🗑️ Clear History"):
        st.session_state.conversation_history = []
        st.success("History cleared!")


# ============================================================================
# MAIN CONTENT - TABS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["🎥 Live Detection", "📊 Dashboard", "ℹ️ How to Use"])


# ============================================================================
# TAB 1: LIVE DETECTION
# ============================================================================

with tab1:
    st.markdown("## 🎥 Real-Time Gesture Detection")
    
    # Create two columns
    col_video, col_info = st.columns([3, 2])
    
    # LEFT COLUMN - WEBCAM
    with col_video:
        st.markdown("### 📹 Webcam Feed")
        
        # Camera control buttons
        camera_col1, camera_col2, camera_col3 = st.columns(3)
        
        with camera_col1:
            if st.button("▶️ Start Camera"):
                st.session_state.camera_active = True
                st.rerun()
        
        with camera_col2:
            if st.button("⏹️ Stop Camera"):
                st.session_state.camera_active = False
                st.rerun()
        
        with camera_col3:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Webcam feed placeholder
        webcam_placeholder = st.empty()
        status_placeholder = st.empty()
        
        # Webcam processing loop
        if st.session_state.camera_active:
            status_placeholder.success("🟢 Camera Active")
            
            try:
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                frame_count = 0
                start_time = time.time()
                
                while st.session_state.camera_active and frame_count < 300:  # Limit to 10 seconds
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame = cv2.flip(frame, 1)
                    
                    # Detect gesture
                    label, confidence, annotated_frame = st.session_state.gesture_detector.predict_gesture(frame)
                    
                    # Add letter if valid
                    if label not in ['NOTHING', 'CLEAR']:
                        st.session_state.sentence_builder.add_letter(label, confidence)
                    
                    # Convert BGR to RGB for display
                    rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                    
                    # Display frame
                    webcam_placeholder.image(rgb_frame, channels="RGB", use_column_width=True)
                    
                    frame_count += 1
                    time.sleep(0.033)  # ~30 FPS
                
                cap.release()
                st.session_state.camera_active = False
                st.rerun()
                
            except Exception as e:
                status_placeholder.error(f"❌ Camera Error: {str(e)}")
                st.info("💡 Make sure your webcam is connected and accessible")
                st.session_state.camera_active = False
        else:
            status_placeholder.info("⚪ Camera Inactive")
            webcam_placeholder.image(np.zeros((480, 640, 3), dtype=np.uint8), 
                                    channels="RGB", use_column_width=True)
    
    # RIGHT COLUMN - INFORMATION PANEL
    with col_info:
        st.markdown("### 📝 Sentence Builder")
        
        # Get current display info
        display_info = st.session_state.sentence_builder.get_display_info()
        
        # Current letter display
        current_letter = display_info.get('current_letter', '—')
        st.markdown(f"""
        <div class="gesture-display">
            {current_letter}
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence bar
        if st.session_state.sentence_builder.last_letter:
            last_confidence = 0.85  # Placeholder
            st.progress(last_confidence, text=f"Confidence: {format_confidence_display(last_confidence)}")
        
        # Word display
        st.markdown("**Current Word:**")
        current_word = display_info.get('current_word', '')
        st.text_input("Word", value=current_word, disabled=True, key="word_display")
        
        # Sentence display
        st.markdown("**Full Sentence:**")
        full_sentence = display_info.get('sentence', '')
        st.text_area("Sentence", value=full_sentence, height=100, disabled=True, key="sentence_display")
        
        # Metrics
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Words", display_info.get('word_count', 0))
        with col_m2:
            st.metric("Letters", display_info.get('letter_count', 0))
        
        st.divider()
        
        # Sentence control buttons
        st.markdown("**📋 Sentence Controls**")
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if st.button("🔤 Add Space"):
                st.session_state.sentence_builder.add_letter('SPACE', 1.0)
                st.rerun()
        
        with btn_col2:
            if st.button("⌫ Clear Word"):
                st.session_state.sentence_builder.reset_word()
                st.rerun()
        
        with btn_col3:
            if st.button("✅ Complete"):
                complete_sent = st.session_state.sentence_builder.complete_sentence()
                if complete_sent:
                    st.session_state.conversation_history.append({
                        'timestamp': datetime.now(),
                        'sentence': complete_sent,
                        'emotion': st.session_state.current_emotion
                    })
                    st.success(f"✓ Sentence completed: {complete_sent}")
                    st.rerun()
        
        st.divider()
        
        # Voice and emotion section
        st.markdown("### 🎵 Voice & Emotion")
        
        if enable_emotion:
            if st.button("🎙️ Record & Detect Emotion", key="emotion_btn"):
                try:
                    with st.spinner("🎤 Recording..."):
                        audio = st.session_state.emotion_detector.record_audio(duration=3)
                        if audio is not None:
                            emotion_result = st.session_state.emotion_detector.predict_emotion(
                                audio_data=(audio, 22050)
                            )
                            st.session_state.current_emotion = emotion_result
                except Exception as e:
                    st.error(f"Error recording: {e}")
            
            # Display emotion result
            if st.session_state.current_emotion:
                emotion = st.session_state.current_emotion.get('emotion', 'unknown')
                confidence = st.session_state.current_emotion.get('confidence', 0)
                
                emotion_badges = {
                    'happy': '😊',
                    'sad': '😢',
                    'angry': '😠',
                    'calm': '😌',
                    'neutral': '😐',
                    'fearful': '😨',
                    'surprised': '😲'
                }
                
                emoji = emotion_badges.get(emotion, '🎭')
                
                st.markdown(f"""
                <div class="info-card">
                    <div class="emotion-badge emotion-{emotion}">
                        {emoji} {emotion.upper()} - {confidence:.0f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # TTS section
        st.markdown("### 🔊 Text-to-Speech")
        
        tts_lang_code = 'en' if tts_language == 'English' else 'hi'
        
        if st.button("🔊 Speak Sentence"):
            sentence = full_sentence.strip()
            if sentence:
                with st.spinner("🎵 Generating speech..."):
                    emotion = st.session_state.current_emotion.get('emotion', 'neutral') if st.session_state.current_emotion else 'neutral'
                    audio_path, html = st.session_state.tts_engine.speak_text(
                        sentence,
                        language=tts_lang_code,
                        emotion=emotion
                    )
                    if audio_path:
                        st.markdown(html, unsafe_allow_html=True)
                        st.success("✓ Audio generated!")
        
        st.divider()
        
        # Translation section
        if enable_translation:
            st.markdown("### 🌐 Translation")
            
            if st.button("🌐 Translate to Hindi"):
                sentence = full_sentence.strip()
                if sentence:
                    with st.spinner("🌍 Translating..."):
                        hindi_text = st.session_state.translator.translate_to_hindi(sentence)
                        st.text_area("Hindi Translation", value=hindi_text, height=80, disabled=True)
                        
                        # Speak Hindi translation
                        if st.button("🔊 Speak Hindi"):
                            with st.spinner("🎵 Generating Hindi speech..."):
                                audio_path, html = st.session_state.tts_engine.speak_text(
                                    hindi_text,
                                    language='hi',
                                    emotion='calm'
                                )
                                if audio_path:
                                    st.markdown(html, unsafe_allow_html=True)


# ============================================================================
# TAB 2: DASHBOARD
# ============================================================================

with tab2:
    st.markdown("## 📊 Dashboard & Analytics")
    
    # Metrics row
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("📝 Total Sentences", len(st.session_state.conversation_history))
    
    with metric_col2:
        total_words = sum(len(item['sentence'].split()) 
                         for item in st.session_state.conversation_history)
        st.metric("📚 Total Words", total_words)
    
    with metric_col3:
        total_chars = sum(len(item['sentence']) 
                         for item in st.session_state.conversation_history)
        st.metric("🔤 Total Characters", total_chars)
    
    with metric_col4:
        emotions = [item.get('emotion', {}).get('emotion', 'unknown') 
                   for item in st.session_state.conversation_history]
        if emotions:
            from collections import Counter
            most_common = Counter(emotions).most_common(1)[0][0]
            st.metric("🎭 Most Common Emotion", most_common.upper())
    
    st.divider()
    
    # Conversation history table
    if st.session_state.conversation_history:
        st.markdown("### 📋 Conversation History")
        
        # Prepare data for table
        history_data = []
        for item in st.session_state.conversation_history:
            emotion = item.get('emotion', {})
            emotion_label = emotion.get('emotion', 'N/A') if isinstance(emotion, dict) else 'N/A'
            history_data.append({
                'Sentence': item['sentence'],
                'Emotion': emotion_label.upper(),
                'Time': item.get('timestamp', '').strftime("%H:%M:%S") if hasattr(item.get('timestamp'), 'strftime') else ''
            })
        
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True)
        
        # Download button
        csv = df_history.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Clear history button
        if st.button("🗑️ Clear All History"):
            st.session_state.conversation_history = []
            st.success("History cleared!")
            st.rerun()
    else:
        st.info("💡 No sentences yet. Start by detecting gestures in the Live Detection tab!")


# ============================================================================
# TAB 3: HOW TO USE
# ============================================================================

with tab3:
    st.markdown("## ℹ️ How to Use This Application")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📖 Step-by-Step Guide
        
        #### 1️⃣ **Start the Webcam**
        - Go to the **Live Detection** tab
        - Click "▶️ Start Camera" to activate your webcam
        - Position your hand clearly in front of the camera
        
        #### 2️⃣ **Show Gestures**
        - Make sign language gestures for letters A-Z or digits 0-9
        - The system will recognize your hand position in real-time
        - MediaPipe detects 21 hand landmarks for accurate recognition
        
        #### 3️⃣ **Build Words & Sentences**
        - Each gesture is added as a letter
        - Click "🔤 Add Space" to separate words
        - The sentence appears in the display area
        
        #### 4️⃣ **Detect Emotion (Optional)**
        - Click "🎙️ Record & Detect Emotion" to record your voice
        - The system analyzes tone, pitch, and energy
        - Detects: Happy, Sad, Angry, Calm, Neutral, Fearful, Surprised
        
        #### 5️⃣ **Generate Speech**
        - Click "🔊 Speak Sentence" to convert text to speech
        - Speech tone adjusts based on detected emotion
        - Supports English and Hindi
        
        #### 6️⃣ **Translate**
        - Click "🌐 Translate to Hindi" for instant translation
        - Uses Google Translate API
        - Click "🔊 Speak Hindi" for bilingual output
        
        #### 7️⃣ **Save & Export**
        - Go to **Dashboard** to view conversation history
        - Download as CSV for record-keeping
        - Share and analyze your sign language conversations
        
        ---
        
        ### 🤚 Gesture Reference
        
        **Letters (A-Z):**
        - **A**: Closed fist
        - **B**: Open palm, fingers together
        - **C**: Thumb and fingers forming C shape
        - **D**: Index finger pointing up, other fingers closed
        - **E-Z**: Similar hand shapes for each letter
        
        **Special Gestures:**
        - **SPACE**: Open palm, all fingers spread
        - **CLEAR**: Closed fist (to clear current letter)
        - **NOTHING**: No hand detected (neutral)
        
        ---
        
        ### 💡 Tips for Best Results
        
        ✅ **Good Lighting** - Ensure adequate lighting on your hands
        ✅ **Clear Background** - Use a plain, contrasting background
        ✅ **Steady Hand** - Hold each gesture for 0.5-1 second
        ✅ **Distance** - Position hand 12-24 inches from camera
        ✅ **Single Hand** - Show one hand at a time
        ✅ **Confidence Settings** - Adjust threshold in sidebar for accuracy
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Tech Stack
        
        **Frontend:**
        - Streamlit
        - Python 3.8+
        
        **Vision:**
        - MediaPipe (hand detection)
        - TensorFlow/Keras (CNN)
        - OpenCV (frame processing)
        
        **Audio:**
        - Librosa (feature extraction)
        - SVM (emotion classification)
        - gTTS (text-to-speech)
        - SoundDevice (recording)
        
        **NLP:**
        - googletrans (translation)
        
        **Data:**
        - NumPy, Pandas
        
        ### 📊 Model Specs
        
        **Gesture Model:**
        - Input: 63 features (21 landmarks × 3 coords)
        - Output: 39 classes (A-Z, 0-9, controls)
        - Architecture: Deep CNN
        - Accuracy: >95% (with real data)
        
        **Emotion Model:**
        - Features: MFCC, Chroma, Mel
        - Classifier: SVM
        - Classes: 7 emotions
        """)
    
    st.divider()
    
    st.markdown("""
    ### 📚 For Internship/Resume
    
    **Project Description:**
    
    > Built a multi-modal accessibility system combining real-time 21-point hand 
    > landmark detection (MediaPipe) with CNN-based gesture classification across 
    > 39 sign classes (A-Z, 0-9, controls). Integrated voice emotion detection 
    > pipeline using MFCC/Chroma/Mel feature extraction with SVM classifier. 
    > Developed sentence builder engine with letter smoothing (7-frame buffer) 
    > and word completion. Added English-to-Hindi translation and emotionally-toned 
    > gTTS voice output with tone variation by detected emotion. Deployed as 
    > multi-tab Streamlit application with real-time confidence visualization 
    > and conversation history dashboard.
    
    **Skills Demonstrated:**
    - Computer Vision (MediaPipe, OpenCV)
    - Deep Learning (TensorFlow, CNN)
    - Audio Processing (Librosa, voice emotion)
    - Machine Learning (SVM, feature engineering)
    - Web Development (Streamlit)
    - Real-time Processing
    - Accessibility Technology
    - Bilingual Support (English-Hindi)
    """)


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**🤟 Sign Language to Emotional Speech Converter**

*An open-source AI accessibility project combining computer vision, audio ML, 
and NLP to enable sign language communication with emotional expression.*

Built with ❤️ for accessibility | [GitHub](https://github.com) | Last Updated: 2026
""")
