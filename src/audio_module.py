"""Audio emotion recognition with Librosa features and an SVM classifier."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

import joblib
import numpy as np

LOGGER = logging.getLogger(__name__)


class AudioEmotionError(RuntimeError):
    """Raised when audio feature extraction or emotion prediction fails."""


class AudioEmotionRecognizer:
    """Extract MFCC, chroma, and mel features and classify speech emotion."""

    def __init__(
        self,
        emotions: Sequence[str],
        model_path: str | Path = "models/emotion_svm.joblib",
        sample_rate: int = 22050,
    ) -> None:
        """Initialize the recognizer and load an SVM model when present."""
        self.emotions = list(emotions)
        self.model_path = Path(model_path)
        self.sample_rate = sample_rate
        self.model: Optional[Any] = self._load_model(self.model_path)

    def _load_model(self, model_path: Path) -> Optional[Any]:
        """Load a scikit-learn SVM pipeline from disk with graceful fallback."""
        candidates = [model_path]
        if model_path.suffix != ".pkl":
            candidates.append(model_path.with_suffix(".pkl"))
        candidates.append(Path("models/emotion_svm.pkl"))
        existing = next((path for path in candidates if path.exists()), None)
        if existing is None:
            return None
        try:
            return joblib.load(existing)
        except Exception as exc:
            LOGGER.exception("Could not load emotion model %s: %s", existing, exc)
            return None

    def load_audio(self, audio_path: str | Path) -> Tuple[np.ndarray, int]:
        """Load an audio file as mono samples at the configured sample rate."""
        try:
            import librosa

            samples, sample_rate = librosa.load(str(audio_path), sr=self.sample_rate, mono=True)
            if samples.size == 0:
                raise AudioEmotionError("Audio file contains no samples.")
            return samples.astype(np.float32), int(sample_rate)
        except AudioEmotionError:
            raise
        except Exception as exc:
            LOGGER.exception("Audio loading failed: %s", exc)
            raise AudioEmotionError(str(exc)) from exc

    def extract_features(self, samples: np.ndarray, sample_rate: Optional[int] = None) -> np.ndarray:
        """Extract a fixed-length MFCC, chroma, and mel feature vector."""
        if samples is None or samples.size == 0:
            raise AudioEmotionError("A non-empty audio signal is required.")
        try:
            import librosa

            sr = sample_rate or self.sample_rate
            y = samples.astype(np.float32)
            min_length = max(2048, int(sr))
            if y.size < min_length:
                y = np.pad(y, (0, min_length - y.size), mode="constant")
            n_fft = min(2048, max(512, 2 ** int(np.floor(np.log2(max(2, y.size))))))
            hop_length = max(128, n_fft // 4)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40, n_fft=n_fft, hop_length=hop_length)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)
            mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=n_fft, hop_length=hop_length)
            features = np.concatenate(
                [
                    np.mean(mfcc, axis=1),
                    np.std(mfcc, axis=1),
                    np.mean(chroma, axis=1),
                    np.std(chroma, axis=1),
                    np.mean(librosa.power_to_db(mel), axis=1),
                ]
            )
            return features.reshape(1, -1).astype(np.float32)
        except Exception as exc:
            LOGGER.exception("Feature extraction failed: %s", exc)
            raise AudioEmotionError(str(exc)) from exc

    def predict_file(self, audio_path: str | Path) -> Dict[str, Any]:
        """Predict emotion probabilities from an audio file."""
        samples, sample_rate = self.load_audio(audio_path)
        return self.predict_samples(samples, sample_rate)

    def predict_samples(self, samples: np.ndarray, sample_rate: Optional[int] = None) -> Dict[str, Any]:
        """Predict emotion probabilities from an in-memory audio signal."""
        if self.model is not None:
            try:
                features = self.extract_features(samples, sample_rate)
                probabilities = self._model_probabilities(features)
                best_index = int(np.argmax(probabilities))
                return {
                    "emotion": self.emotions[best_index],
                    "confidence": float(probabilities[best_index]),
                    "probabilities": self._probability_map(probabilities),
                    "model_loaded": True,
                }
            except Exception as exc:
                LOGGER.exception("Emotion model prediction failed; using fallback: %s", exc)
        probabilities = self._heuristic_probabilities(samples, sample_rate)
        best_index = int(np.argmax(probabilities))
        return {
            "emotion": self.emotions[best_index],
            "confidence": float(probabilities[best_index]),
            "probabilities": self._probability_map(probabilities),
            "model_loaded": False,
        }

    def _model_probabilities(self, features: np.ndarray) -> np.ndarray:
        """Return normalized probabilities from a model with or without predict_proba."""
        if hasattr(self.model, "predict_proba"):
            raw = np.asarray(self.model.predict_proba(features)[0], dtype=float)
        else:
            predicted = str(self.model.predict(features)[0])
            raw = np.zeros(len(self.emotions), dtype=float)
            raw[self.emotions.index(predicted) if predicted in self.emotions else 0] = 1.0
        fitted = np.zeros(len(self.emotions), dtype=float)
        count = min(len(fitted), len(raw))
        fitted[:count] = raw[:count]
        total = float(fitted.sum())
        return fitted / total if total > 0 else np.ones(len(self.emotions), dtype=float) / len(self.emotions)

    def _probability_map(self, probabilities: np.ndarray) -> Dict[str, float]:
        """Convert a probability vector into an emotion keyed dictionary."""
        return {emotion: float(probabilities[index]) for index, emotion in enumerate(self.emotions)}

    def _heuristic_probabilities(self, samples: np.ndarray, sample_rate: Optional[int] = None) -> np.ndarray:
        """Infer emotion probabilities from RMS energy, tempo, and zero crossing rate."""
        y = samples.astype(np.float32)
        sr = sample_rate or self.sample_rate
        if y.size < max(512, sr // 2):
            y = np.pad(y, (0, max(512, sr // 2) - y.size), mode="constant")
        rms = float(np.sqrt(np.mean(np.square(y))) + 1e-8)
        zcr = float(np.mean(np.abs(np.diff(np.signbit(y).astype(np.int8)))) + 1e-8)
        tempo = self._estimate_tempo(y, sr)
        label = "neutral"
        if rms > 0.10 and tempo > 115 and zcr > 0.08:
            label = "angry"
        elif rms > 0.075 and tempo > 95:
            label = "happy"
        elif rms < 0.025 and tempo < 85:
            label = "sad"
        elif zcr > 0.16 and "fearful" in self.emotions:
            label = "fearful"
        probabilities = np.full(len(self.emotions), 0.03, dtype=float)
        probabilities[self.emotions.index(label) if label in self.emotions else 0] = 0.82
        return probabilities / float(probabilities.sum())

    def _estimate_tempo(self, samples: np.ndarray, sample_rate: int) -> float:
        """Estimate tempo quickly from an RMS envelope without model dependencies."""
        frame_length = max(256, int(sample_rate * 0.046))
        hop_length = max(128, frame_length // 2)
        if samples.size < frame_length * 2:
            return 60.0
        frame_count = 1 + (samples.size - frame_length) // hop_length
        if frame_count < 3:
            return 60.0
        envelope = np.array(
            [
                np.sqrt(np.mean(np.square(samples[index * hop_length : index * hop_length + frame_length])))
                for index in range(frame_count)
            ],
            dtype=float,
        )
        envelope = envelope - float(np.mean(envelope))
        if np.max(np.abs(envelope)) <= 1e-8:
            return 60.0
        autocorrelation = np.correlate(envelope, envelope, mode="full")[len(envelope) - 1 :]
        min_bpm, max_bpm = 50.0, 180.0
        min_lag = max(1, int((60.0 / max_bpm) * sample_rate / hop_length))
        max_lag = min(len(autocorrelation) - 1, int((60.0 / min_bpm) * sample_rate / hop_length))
        if max_lag <= min_lag:
            return 60.0
        lag = int(np.argmax(autocorrelation[min_lag : max_lag + 1]) + min_lag)
        return float(60.0 * sample_rate / (lag * hop_length))


class FeatureExtractor:
    """Standalone short-clip-safe Librosa feature extractor."""

    def __init__(self, sample_rate: int = 22050) -> None:
        """Create a feature extractor with a target sample rate."""
        self.sample_rate = sample_rate

    def extract(self, samples: np.ndarray, sample_rate: Optional[int] = None) -> np.ndarray:
        """Extract MFCC, chroma, and mel features from audio samples."""
        recognizer = AudioEmotionRecognizer(emotions=["neutral"], sample_rate=sample_rate or self.sample_rate)
        return recognizer.extract_features(samples, sample_rate or self.sample_rate)
