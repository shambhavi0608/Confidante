"""
Text-to-Speech Engine Module - Converts text to emotionally-toned audio.

This module uses Google TTS (gTTS) to generate speech with emotional
tone modulation based on detected emotions.
"""

from gtts import gTTS
import os
import tempfile
import base64


class TTSEngine:
    """
    Generates emotionally-toned speech from text using gTTS.
    
    Supports multiple languages and adjusts speed/tone based on emotion.
    """
    
    def __init__(self):
        """
        Initialize the TTS Engine.
        
        Example:
            tts = TTSEngine()
            audio_path, html = tts.speak_text("Hello world", emotion="happy")
        """
        self.supported_languages = {
            'English': 'en',
            'Hindi': 'hi',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de'
        }
        # Create temporary directory for audio files
        self.temp_dir = tempfile.mkdtemp()
        print(f"✓ TTS Engine initialized. Temp dir: {self.temp_dir}")

    def generate_speech(self, text, language='en', emotion='neutral'):
        """
        Generate speech audio from text.
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code (e.g., 'en', 'hi')
            emotion (str): Emotion for tone modulation (happy, sad, calm, etc.)
            
        Returns:
            str: Path to generated audio file or None if generation fails
            
        Example:
            audio_path = tts.generate_speech("Hello", language='en', emotion='happy')
            print(f"Audio saved to: {audio_path}")
        """
        if not text or text.strip() == "":
            return None
        
        try:
            # Determine speech speed based on emotion
            slow = emotion in ['sad', 'calm']
            
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=language,
                slow=slow,
                tld='com'
            )
            
            # Generate filename based on text hash
            text_hash = hash(text + language + emotion) % (10 ** 8)
            audio_filename = f"{self.temp_dir}/speech_{text_hash}.mp3"
            
            # Save audio file
            tts.save(audio_filename)
            
            return audio_filename
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None

    def get_audio_html(self, audio_path):
        """
        Convert audio file to HTML audio tag with base64 encoding.
        
        Args:
            audio_path (str): Path to audio file
            
        Returns:
            str: HTML audio tag string for Streamlit autoplay
            
        Example:
            html = tts.get_audio_html('speech_123.mp3')
            st.markdown(html, unsafe_allow_html=True)
        """
        if not audio_path or not os.path.exists(audio_path):
            return ""
        
        try:
            # Read audio file as bytes
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Convert to base64
            b64 = base64.b64encode(audio_bytes).decode()
            
            # Return HTML audio tag
            html = f'''
            <audio autoplay style="width: 100%;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            '''
            return html
            
        except Exception as e:
            print(f"Error generating audio HTML: {e}")
            return ""

    def speak_text(self, text, language='en', emotion='neutral'):
        """
        Generate speech and return audio file path with HTML tag.
        
        Args:
            text (str): Text to speak
            language (str): Language code
            emotion (str): Emotion for tone modulation
            
        Returns:
            tuple: (audio_path, html_string) or (None, "") if generation fails
            
        Example:
            audio_path, html = tts.speak_text("Hello world", emotion='happy')
            if audio_path:
                st.markdown(html, unsafe_allow_html=True)
        """
        # Generate speech audio
        audio_path = self.generate_speech(text, language, emotion)
        
        if audio_path is None:
            return None, ""
        
        # Get HTML representation
        html_string = self.get_audio_html(audio_path)
        
        return audio_path, html_string

    def get_supported_languages(self):
        """
        Get list of supported languages.
        
        Returns:
            dict: Language names mapped to codes
            
        Example:
            langs = tts.get_supported_languages()
            print(langs)  # {'English': 'en', 'Hindi': 'hi', ...}
        """
        return self.supported_languages

    def cleanup(self):
        """
        Clean up temporary audio files.
        
        Example:
            tts.cleanup()
        """
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"✓ Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"Warning: Could not cleanup temp directory: {e}")

    def __del__(self):
        """Cleanup on object deletion."""
        self.cleanup()
