"""
Gesture Detector Module - Real-time hand gesture recognition using MediaPipe and CNN.

This module detects hand landmarks using MediaPipe and classifies them using
a trained CNN model to recognize sign language gestures (A-Z, 0-9, and controls).
"""

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import pickle
from collections import deque


class GestureDetector:
    """
    Real-time hand gesture detector using MediaPipe and TensorFlow CNN.
    
    Detects hand landmarks and classifies them into 39 gesture classes
    (A-Z, 0-9, SPACE, CLEAR, NOTHING) with confidence scoring.
    """
    
    def __init__(self, 
                 model_path='model/gesture_model.h5', 
                 encoder_path='model/label_encoder.pkl',
                 confidence_threshold=0.75):
        """
        Initialize the GestureDetector.
        
        Args:
            model_path (str): Path to the trained TensorFlow model
            encoder_path (str): Path to the label encoder pickle file
            confidence_threshold (float): Minimum confidence to accept a prediction (0-1)
            
        Example:
            detector = GestureDetector(confidence_threshold=0.8)
            label, conf, frame = detector.predict_gesture(frame)
        """
        # Initialize MediaPipe Hands detector with optimized settings
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(
            static_image_mode=False,  # Use video mode for better tracking
            max_num_hands=1,          # Detect only one hand
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_hands = mp_hands
        
        # Configuration
        self.confidence_threshold = confidence_threshold
        self.prediction_buffer = deque(maxlen=7)  # Smoothing buffer
        
        # Load trained model if it exists
        self.model = None
        if os.path.exists(model_path):
            try:
                self.model = load_model(model_path)
                print(f"✓ Model loaded successfully from {model_path}")
            except Exception as e:
                print(f"⚠ Warning: Could not load model from {model_path}: {e}")
        else:
            print(f"⚠ Warning: Gesture model file not found at {model_path}")

        # Load label encoder if it exists
        self.label_encoder = None
        if os.path.exists(encoder_path):
            try:
                with open(encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                print(f"✓ Label encoder loaded successfully from {encoder_path}")
            except Exception as e:
                print(f"⚠ Warning: Could not load label encoder from {encoder_path}: {e}")
        
        # Define gesture labels (39 classes)
        self.labels = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'SPACE', 'CLEAR', 'NOTHING'
        ]

    def extract_landmarks(self, frame):
        """
        Extract normalized hand landmarks from a frame using MediaPipe.
        
        Args:
            frame (np.ndarray): Input frame from webcam (BGR format)
            
        Returns:
            np.ndarray or None: Flattened normalized landmarks (63,) or None if no hand detected
            
        Example:
            landmarks = detector.extract_landmarks(frame)
            if landmarks is not None:
                print(f"Detected hand with {len(landmarks)} coordinates")
        """
        # Convert BGR to RGB for MediaPipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            # Extract first hand's landmarks
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Convert landmarks to numpy array
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            
            # Normalize: subtract wrist position (landmark 0)
            wrist_pos = landmarks[0]
            landmarks_normalized = landmarks - wrist_pos
            
            # Normalize by max distance for scale invariance
            max_distance = np.max(np.linalg.norm(landmarks_normalized, axis=1))
            if max_distance > 0:
                landmarks_normalized = landmarks_normalized / max_distance
            
            # Flatten to 1D array (63 = 21 landmarks * 3 coordinates)
            return landmarks_normalized.flatten().astype(np.float32)
        
        return None

    def predict_gesture(self, frame):
        """
        Predict the gesture shown in the frame using the trained model.
        
        Args:
            frame (np.ndarray): Input frame from webcam (BGR format)
            
        Returns:
            tuple: (predicted_label, confidence, annotated_frame)
                - predicted_label (str): Gesture class name
                - confidence (float): Prediction confidence (0-1)
                - annotated_frame (np.ndarray): Frame with visualization
                
        Example:
            label, conf, annotated_frame = detector.predict_gesture(frame)
            cv2.imshow('Gesture Detection', annotated_frame)
        """
        # Extract hand landmarks
        landmarks = self.extract_landmarks(frame)
        
        # Prepare frame for annotation
        annotated_frame = frame.copy()
        
        # Visualize hand landmarks
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        
        # If no hand detected, return NOTHING
        if landmarks is None:
            return ('NOTHING', 0.0, annotated_frame)
        
        # If model not available, return NOTHING
        if self.model is None:
            return ('NOTHING', 0.0, annotated_frame)
        
        try:
            # Reshape for model input (1, 63)
            landmarks_input = landmarks.reshape(1, 63)
            
            # Get model prediction
            predictions = self.model.predict(landmarks_input, verbose=0)
            class_idx = int(np.argmax(predictions[0]))
            confidence = float(predictions[0][class_idx])
            
            # Add to smoothing buffer
            predicted_label = self.labels[class_idx]
            self.prediction_buffer.append(predicted_label)
            
            # Use most common prediction in buffer for smoothing
            if len(self.prediction_buffer) > 0:
                from collections import Counter
                most_common = Counter(self.prediction_buffer).most_common(1)
                predicted_label = most_common[0][0]
            
            # Apply confidence threshold
            if confidence < self.confidence_threshold:
                confidence_filtered = confidence * 0.5  # Scale down confidence
                return ('NOTHING', confidence_filtered, self.annotate_frame(
                    annotated_frame, 'LOW CONFIDENCE', confidence
                ))
            
            # Annotate frame with prediction
            annotated_frame = self.annotate_frame(annotated_frame, predicted_label, confidence)
            
            return (predicted_label, confidence, annotated_frame)
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return ('NOTHING', 0.0, annotated_frame)

    def annotate_frame(self, frame, label, confidence):
        """
        Annotate frame with gesture label, confidence, and bounding box.
        
        Args:
            frame (np.ndarray): Input frame to annotate
            label (str): Gesture label to display
            confidence (float): Confidence score (0-1)
            
        Returns:
            np.ndarray: Annotated frame
            
        Example:
            annotated = detector.annotate_frame(frame, 'A', 0.92)
        """
        annotated = frame.copy()
        height, width = frame.shape[:2]
        
        # Get color based on confidence
        color = self.get_confidence_color(confidence)
        
        # Draw background panel for text
        text_size_label = cv2.getTextSize(f"Gesture: {label}", cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
        text_size_conf = cv2.getTextSize(f"Confidence: {confidence:.1%}", cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        
        panel_height = text_size_label[1] + text_size_conf[1] + 30
        panel_width = max(text_size_label[0], text_size_conf[0]) + 30
        
        # Draw semi-transparent panel
        overlay = annotated.copy()
        cv2.rectangle(overlay, (10, 10), (10 + panel_width, 10 + panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, annotated, 0.7, 0, annotated)
        
        # Draw text
        cv2.putText(annotated, f"Gesture: {label}", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
        cv2.putText(annotated, f"Confidence: {confidence:.1%}", (20, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        # Draw confidence bar
        bar_width = 300
        bar_height = 20
        bar_x, bar_y = 10, height - 40
        
        cv2.rectangle(annotated, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                     (200, 200, 200), 2)
        filled_width = int(bar_width * confidence)
        cv2.rectangle(annotated, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height),
                     color, -1)
        
        return annotated

    def get_confidence_color(self, confidence):
        """
        Get BGR color based on confidence level.
        
        Args:
            confidence (float): Confidence score (0-1)
            
        Returns:
            tuple: BGR color (B, G, R)
            
        Example:
            color = detector.get_confidence_color(0.85)  # Returns green
        """
        if confidence > 0.75:
            return (0, 255, 0)      # Green
        elif confidence > 0.5:
            return (0, 255, 255)    # Yellow
        else:
            return (0, 0, 255)      # Red
