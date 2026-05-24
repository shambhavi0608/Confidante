"""Gesture recognition using MediaPipe hand landmarks and a TensorFlow classifier."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np
import yaml

LOGGER = logging.getLogger(__name__)


class GestureDetectionError(RuntimeError):
    """Raised when gesture detection cannot process an input frame."""


class GestureRecognizer:
    """Detect 21-point hand landmarks and classify them into ASL gesture classes."""

    def __init__(
        self,
        classes: Sequence[str] | None = None,
        model_path: str | Path = "models/gesture_cnn.keras",
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        """Initialize MediaPipe Hands and load a TensorFlow model when available."""
        self.classes: List[str] = list(classes) if classes is not None else self._load_config_classes()
        self.model_path = Path(model_path)
        self.model: Optional[Any] = self._load_model(self.model_path)
        self.hands: Optional[Any] = self._create_hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def _create_hands(
        self,
        max_num_hands: int,
        min_detection_confidence: float,
        min_tracking_confidence: float,
    ) -> Optional[Any]:
        """Create the MediaPipe Hands graph with defensive import handling."""
        try:
            import mediapipe as mp

            return mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=max_num_hands,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )
        except Exception:
            return None

    def _load_model(self, model_path: Path) -> Optional[Any]:
        """Load the gesture CNN from disk, returning None when it is unavailable."""
        candidates = [model_path, Path("models/gesture_cnn"), Path("models/gesture_cnn.keras")]
        existing = next((path for path in candidates if path.exists()), None)
        if existing is None:
            return None
        try:
            from tensorflow.keras.models import load_model

            return load_model(existing)
        except Exception:
            return None

    def _load_config_classes(self) -> List[str]:
        """Load gesture class names from config.yaml without surfacing import errors."""
        try:
            config_path = Path(__file__).resolve().parents[1] / "config.yaml"
            with config_path.open("r", encoding="utf-8") as file:
                config = yaml.safe_load(file) or {}
            classes = config.get("gesture", {}).get("classes", [])
            if classes:
                return [str(label) for label in classes]
        except Exception:
            pass
        return ["0", "1", "2", "3", "4", "5", "THUMBS UP", "HELLO", "STOP", "NOTHING"]

    def close(self) -> None:
        """Release MediaPipe resources held by the recognizer."""
        if self.hands is not None:
            self.hands.close()

    def detect_landmarks(self, frame_bgr: np.ndarray) -> Tuple[Optional[np.ndarray], np.ndarray]:
        """Return normalized 21x3 landmarks and an annotated BGR frame."""
        if frame_bgr is None or frame_bgr.size == 0:
            raise GestureDetectionError("A non-empty webcam frame is required.")
        annotated = frame_bgr.copy()
        if self.hands is None:
            return None, annotated
        try:
            import mediapipe as mp

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            result = self.hands.process(frame_rgb)
            if not result.multi_hand_landmarks:
                return None, annotated
            hand_landmarks = result.multi_hand_landmarks[0]
            mp.solutions.drawing_utils.draw_landmarks(
                annotated,
                hand_landmarks,
                mp.solutions.hands.HAND_CONNECTIONS,
            )
            landmarks = np.array(
                [[point.x, point.y, point.z] for point in hand_landmarks.landmark],
                dtype=np.float32,
            )
            return self.normalize_landmarks(landmarks), annotated
        except Exception as exc:
            LOGGER.exception("Gesture landmark detection failed: %s", exc)
            raise GestureDetectionError(str(exc)) from exc

    def normalize_landmarks(self, landmarks: np.ndarray) -> np.ndarray:
        """Normalize landmarks relative to the wrist and scale by max distance."""
        if landmarks.shape != (21, 3):
            raise GestureDetectionError(f"Expected landmarks shape (21, 3), got {landmarks.shape}.")
        centered = landmarks - landmarks[0]
        scale = float(np.max(np.linalg.norm(centered[:, :2], axis=1)))
        if scale <= 1e-6:
            return centered
        return centered / scale

    def predict_from_landmarks(self, landmarks: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """Predict an ASL class and confidence from normalized landmarks."""
        if self.model is not None:
            try:
                model_input = landmarks.reshape(1, 21, 3, 1).astype(np.float32)
                probabilities = np.asarray(self.model.predict(model_input, verbose=0)[0], dtype=float)
                probabilities = self._fit_probability_vector(probabilities)
                best_index = int(np.argmax(probabilities))
                return self.classes[best_index], float(probabilities[best_index]), self._probability_map(probabilities)
            except Exception:
                pass
        probabilities = self._heuristic_probabilities(landmarks)
        best_index = int(np.argmax(probabilities))
        return self.classes[best_index], float(probabilities[best_index]), self._probability_map(probabilities)

    def predict_frame(self, frame_bgr: np.ndarray) -> Dict[str, Any]:
        """Detect hand landmarks from a frame and return prediction metadata."""
        landmarks, annotated = self.detect_landmarks(frame_bgr)
        if landmarks is None:
            probabilities = np.zeros(len(self.classes), dtype=float)
            if "NOTHING" in self.classes:
                probabilities[self.classes.index("NOTHING")] = 1.0
            return {
                "label": "NOTHING",
                "confidence": 1.0,
                "probabilities": self._probability_map(probabilities),
                "landmarks": None,
                "frame": annotated,
                "model_loaded": self.model is not None,
            }
        label, confidence, probability_map = self.predict_from_landmarks(landmarks)
        return {
            "label": label,
            "confidence": confidence,
            "probabilities": probability_map,
            "landmarks": landmarks,
            "frame": annotated,
            "model_loaded": self.model is not None,
        }

    def _fit_probability_vector(self, probabilities: np.ndarray) -> np.ndarray:
        """Resize and normalize model probabilities to match configured classes."""
        fitted = np.zeros(len(self.classes), dtype=float)
        count = min(len(fitted), len(probabilities))
        fitted[:count] = probabilities[:count]
        total = float(fitted.sum())
        return fitted / total if total > 0 else np.ones(len(self.classes), dtype=float) / len(self.classes)

    def _probability_map(self, probabilities: np.ndarray) -> Dict[str, float]:
        """Convert a probability vector into a class keyed dictionary."""
        return {label: float(probabilities[index]) for index, label in enumerate(self.classes)}

    def _heuristic_probabilities(self, landmarks: np.ndarray) -> np.ndarray:
        """Produce rule-based gesture probabilities from MediaPipe hand landmarks."""
        probabilities = np.full(len(self.classes), 0.01, dtype=float)
        fallback_label = self._rule_based_label(landmarks)
        if fallback_label in self.classes:
            probabilities[self.classes.index(fallback_label)] = 0.86
        else:
            probabilities = np.append(probabilities, 0.86)
            self.classes.append(fallback_label)
        probabilities = probabilities / float(probabilities.sum())
        return probabilities

    def _rule_based_label(self, landmarks: np.ndarray) -> str:
        """Classify simple gestures from extended finger rules."""
        extended = self._extended_fingers(landmarks)
        extended_count = int(np.sum(extended))
        thumb, index, middle, ring, pinky = [bool(value) for value in extended]
        if thumb and not any([index, middle, ring, pinky]):
            return "THUMBS UP"
        if extended_count == 5:
            return "HELLO"
        if extended_count == 0:
            return "STOP"
        if str(extended_count) in self.classes or extended_count <= 5:
            return str(extended_count)
        return "NOTHING"

    def _extended_fingers(self, landmarks: np.ndarray) -> np.ndarray:
        """Return booleans for thumb, index, middle, ring, and pinky extension."""
        wrist = landmarks[0, :2]
        tips = landmarks[[4, 8, 12, 16, 20], :2]
        pips = landmarks[[3, 6, 10, 14, 18], :2]
        mcps = landmarks[[2, 5, 9, 13, 17], :2]
        distance_tip = np.linalg.norm(tips - wrist, axis=1)
        distance_pip = np.linalg.norm(pips - wrist, axis=1)
        distance_mcp = np.linalg.norm(mcps - wrist, axis=1)
        extended = distance_tip > np.maximum(distance_pip, distance_mcp) + 0.08
        vertical_extended = tips[1:, 1] < pips[1:, 1]
        extended[1:] = np.logical_or(extended[1:], vertical_extended)
        return extended

    def _finger_openness(self, landmarks: np.ndarray) -> np.ndarray:
        """Estimate openness for thumb and four fingers from landmark geometry."""
        tips = landmarks[[4, 8, 12, 16, 20], :2]
        bases = landmarks[[2, 5, 9, 13, 17], :2]
        wrist = landmarks[0, :2]
        return np.linalg.norm(tips - wrist, axis=1) - np.linalg.norm(bases - wrist, axis=1)


GestureClassifier = GestureRecognizer
