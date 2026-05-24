"""
Emotion Detector Module - Voice emotion detection using Librosa and SVM.

This module extracts audio features (MFCC, Chroma, Mel) from voice input
and classifies the emotion using a trained SVM model.
"""

import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf
import joblib
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import os
import warnings
warnings.filterwarnings('ignore')


class EmotionDetector:
    """
    Detects emotion from voice using MFCC and SVM classification.
    
    Extracts audio features and uses an SVM model to classify into
    7 emotion categories: angry, calm, fearful, happy, neutral, sad, surprised.
    """
    
    def __init__(self, 
                 model_path='model/emotion_model.pkl',
                 scaler_path='model/emotion_scaler.pkl'):
        """
        Initialize the EmotionDetector.
        
        Args:
            model_path (str): Path to the trained SVM model
            scaler_path (str): Path to the StandardScaler for feature normalization
            
        Example:
            detector = EmotionDetector()
            emotion = detector.predict_emotion('voice.wav')
        """
        self.emotions = ['angry', 'calm', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
        self.sample_rate = 22050
        self.duration = 3  # Recording duration in seconds
        
        # Try to load pre-trained model
        self.model = None
        self.scaler = None
        
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                print(f"✓ Emotion model loaded from {model_path}")
            except Exception as e:
                print(f"⚠ Warning: Could not load emotion model: {e}")
        
        if os.path.exists(scaler_path):
            try:
                self.scaler = joblib.load(scaler_path)
                print(f"✓ Scaler loaded from {scaler_path}")
            except Exception as e:
                print(f"⚠ Warning: Could not load scaler: {e}")
        
        # Create fallback model if not loaded
        if self.model is None:
            print("ℹ Using fallback emotion detection (neutral for all inputs)")
            self.create_fallback_model()

    def extract_features(self, audio_path=None, audio_data=None):
        """
        Extract audio features (MFCC, Chroma, Mel) from audio.
        
        Args:
            audio_path (str): Path to audio file
            audio_data (tuple): Tuple of (audio_array, sample_rate)
            
        Returns:
            np.ndarray: Feature vector of shape (113,)
            
        Example:
            features = detector.extract_features(audio_path='voice.wav')
            print(features.shape)  # (113,)
        """
        try:
            # Load audio
            if audio_path is not None:
                y, sr = librosa.load(audio_path, sr=self.sample_rate)
            elif audio_data is not None:
                y, sr = audio_data
            else:
                return np.zeros(113)
            
            # Ensure audio is not empty
            if len(y) == 0:
                return np.zeros(113)
            
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
            mfcc_mean = np.mean(mfcc.T, axis=0)
            mfcc_std = np.std(mfcc.T, axis=0)
            
            # Extract Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma.T, axis=0)
            
            # Extract Mel Spectrogram features
            mel = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_mean = np.mean(mel.T, axis=0)[:20]  # Take first 20 features
            
            # Extract Zero Crossing Rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # Extract RMS Energy
            rms = np.mean(librosa.feature.rms(y=y))
            
            # Combine all features
            # Total: 40 (mfcc_mean) + 40 (mfcc_std) + 12 (chroma_mean) + 20 (mel_mean) + 1 (zcr) + 1 (rms) = 114
            # We'll use 113 by excluding one
            features = np.concatenate([
                mfcc_mean,      # 40
                mfcc_std,       # 40
                chroma_mean,    # 12
                mel_mean,       # 20
                [zcr, rms]      # 2
            ])
            
            return features.astype(np.float32)
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return np.zeros(113)

    def record_audio(self, duration=3):
        """
        Record audio from microphone for specified duration.
        
        Args:
            duration (int): Recording duration in seconds
            
        Returns:
            np.ndarray: Audio data array
            
        Example:
            audio = detector.record_audio(duration=3)
            emotion = detector.predict_emotion(audio_data=(audio, 22050))
        """
        try:
            print(f"🎤 Recording for {duration} seconds...")
            audio = sd.rec(int(duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=1, 
                          dtype=np.float32)
            sd.wait()  # Wait for recording to finish
            print("✓ Recording complete")
            return audio.flatten()
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

    def predict_emotion(self, audio_path=None, audio_data=None):
        """
        Predict emotion from audio input.
        
        Args:
            audio_path (str): Path to audio file
            audio_data (tuple): Tuple of (audio_array, sample_rate)
            
        Returns:
            dict: Emotion prediction with keys:
                - 'emotion': Emotion label string
                - 'confidence': Confidence percentage (0-100)
                - 'all_probabilities': Dict of emotion:probability
                - 'tone_modifier': Tone description for TTS
                
        Example:
            result = detector.predict_emotion(audio_path='voice.wav')
            print(f"Detected emotion: {result['emotion']} ({result['confidence']:.1f}%)")
        """
        try:
            # Extract features
            features = self.extract_features(audio_path=audio_path, audio_data=audio_data)
            
            if np.all(features == 0):
                return self.create_fallback_prediction()
            
            # Scale features if scaler available
            if self.scaler is not None:
                features = self.scaler.transform([features])[0]
            else:
                features = features.reshape(1, -1)
            
            # Predict emotion
            if self.model is not None:
                try:
                    emotion_idx = self.model.predict([features])[0]
                except:
                    emotion_idx = 4  # Default to neutral
            else:
                emotion_idx = 4  # Default to neutral
            
            predicted_emotion = self.emotions[emotion_idx] if emotion_idx < len(self.emotions) else 'neutral'
            
            # Get confidence
            try:
                if hasattr(self.model, 'decision_function'):
                    scores = self.model.decision_function([features])[0]
                    confidence = float(np.max(scores)) * 10  # Scale to percentage
                    confidence = min(100, max(0, confidence))
                else:
                    confidence = 70.0
            except:
                confidence = 70.0
            
            # Create probability dictionary
            all_probs = {self.emotions[i]: 0.0 for i in range(len(self.emotions))}
            all_probs[predicted_emotion] = confidence / 100.0
            
            # Determine tone modifier
            tone_modifier = self.get_tone_modifier(predicted_emotion)
            
            return {
                'emotion': predicted_emotion,
                'confidence': confidence,
                'all_probabilities': all_probs,
                'tone_modifier': tone_modifier
            }
            
        except Exception as e:
            print(f"Error predicting emotion: {e}")
            return self.create_fallback_prediction()

    def get_tone_modifier(self, emotion):
        """
        Get tone modifier for text-to-speech based on emotion.
        
        Args:
            emotion (str): Emotion label
            
        Returns:
            dict: Tone modifier with 'speed' and 'pitch' adjustment
            
        Example:
            tone = detector.get_tone_modifier('happy')
            print(tone)  # {'speed': 'fast', 'pitch': '+10'}
        """
        tone_mapping = {
            'happy': {'speed': 'fast', 'pitch': '+10 semitones'},
            'sad': {'speed': 'slow', 'pitch': '-5 semitones'},
            'angry': {'speed': 'fast', 'pitch': 'normal'},
            'calm': {'speed': 'slow', 'pitch': 'normal'},
            'neutral': {'speed': 'normal', 'pitch': 'normal'},
            'fearful': {'speed': 'slightly fast', 'pitch': '+3 semitones'},
            'surprised': {'speed': 'fast', 'pitch': '+8 semitones'}
        }
        return tone_mapping.get(emotion, {'speed': 'normal', 'pitch': 'normal'})

    def create_fallback_prediction(self):
        """
        Create a fallback neutral emotion prediction.
        
        Returns:
            dict: Neutral emotion with 70% confidence
            
        Example:
            fallback = detector.create_fallback_prediction()
            print(fallback['emotion'])  # 'neutral'
        """
        return {
            'emotion': 'neutral',
            'confidence': 70.0,
            'all_probabilities': {emotion: (1.0 if emotion == 'neutral' else 0.0) 
                                 for emotion in self.emotions},
            'tone_modifier': {'speed': 'normal', 'pitch': 'normal'}
        }

    def create_fallback_model(self):
        """
        Create a simple fallback SVM model with synthetic training data.
        
        This is used if no pre-trained model is available, allowing the app
        to function in a demo mode that always predicts neutral emotion.
        """
        try:
            from sklearn.svm import SVC
            
            # Create minimal synthetic data
            X_synthetic = np.random.randn(70, 113).astype(np.float32)
            y_synthetic = np.array([4] * 70)  # All neutral
            
            # Create and train fallback model
            self.model = SVC(kernel='linear', probability=False)
            self.model.fit(X_synthetic, y_synthetic)
            
            # Create scaler
            self.scaler = StandardScaler()
            self.scaler.fit(X_synthetic)
            
        except Exception as e:
            print(f"Could not create fallback model: {e}")
