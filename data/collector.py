"""
Data Collector Script - Collect hand landmark data for model training.

This script opens a webcam and collects 21-point hand landmarks for each
gesture class (A-Z, 0-9, SPACE, CLEAR, NOTHING) for training data.
"""

import cv2
import mediapipe as mp
import numpy as np
import os
from tqdm import tqdm


def collect_gesture_data(samples_per_class=200):
    """
    Collect hand landmark data for all gesture classes.
    
    Args:
        samples_per_class (int): Number of samples to collect per gesture
        
    Example:
        collect_gesture_data(samples_per_class=300)
    """
    print("\n" + "="*60)
    print("GESTURE DATA COLLECTOR")
    print("="*60 + "\n")
    
    # Define gesture labels
    labels = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
        'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'SPACE', 'CLEAR', 'NOTHING'
    ]
    
    # Create data directory structure
    data_dir = 'data/gesture_dataset'
    os.makedirs(data_dir, exist_ok=True)
    for label in labels:
        os.makedirs(os.path.join(data_dir, label), exist_ok=True)
    
    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    mp_draw = mp.solutions.drawing_utils
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✗ Error: Could not open webcam")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("Webcam opened successfully!")
    print("\nKEYBOARD CONTROLS:")
    print("  SPACE - Start collecting for current gesture")
    print("  N     - Move to next gesture")
    print("  P     - Move to previous gesture")
    print("  Q     - Quit\n")
    
    # Collection loop
    label_idx = 0
    samples_collected = {label: 0 for label in labels}
    all_landmarks = []
    all_labels = []
    
    while label_idx < len(labels):
        current_label = labels[label_idx]
        
        # Display instructions
        ret, frame = cap.read()
        if not ret:
            print("✗ Error: Could not read frame")
            break
        
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        
        # Draw instruction text
        cv2.putText(frame, f"Gesture: {current_label}", (20, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
        cv2.putText(frame, f"Progress: {label_idx + 1}/{len(labels)}", (20, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        samples_done = samples_collected[current_label]
        cv2.putText(frame, f"Samples: {samples_done}/{samples_per_class}", (20, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        if samples_done < samples_per_class:
            cv2.putText(frame, "Press SPACE to start collecting", (20, 450),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            cv2.putText(frame, "Press N for next gesture", (20, 450),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw progress bar
        bar_width = 200
        bar_height = 25
        filled = int((samples_done / samples_per_class) * bar_width)
        cv2.rectangle(frame, (20, 200), (20 + bar_width, 200 + bar_height), (200, 200, 200), 2)
        cv2.rectangle(frame, (20, 200), (20 + filled, 200 + bar_height), (0, 255, 0), -1)
        
        cv2.imshow('Data Collector', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Handle keyboard input
        if key == ord('q'):
            print("\n✓ Quitting...")
            break
        elif key == ord(' ') and samples_done < samples_per_class:
            # Start collecting samples
            collected = 0
            pbar = tqdm(total=samples_per_class - samples_done, 
                       desc=f"Collecting {current_label}", 
                       position=0, leave=True)
            
            while collected < (samples_per_class - samples_done):
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect hand
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    # Extract landmarks
                    hand_landmarks = results.multi_hand_landmarks[0]
                    landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
                    
                    # Normalize
                    wrist_pos = landmarks[0]
                    landmarks_normalized = landmarks - wrist_pos
                    max_distance = np.max(np.linalg.norm(landmarks_normalized, axis=1))
                    if max_distance > 0:
                        landmarks_normalized = landmarks_normalized / max_distance
                    
                    # Save landmark
                    landmarks_flat = landmarks_normalized.flatten()
                    
                    # Save to file
                    filepath = os.path.join(data_dir, current_label, 
                                          f"landmarks_{samples_collected[current_label] + collected}.npy")
                    np.save(filepath, landmarks_flat)
                    
                    # Add to batch
                    all_landmarks.append(landmarks_flat)
                    all_labels.append(current_label)
                    
                    collected += 1
                    pbar.update(1)
                    
                    # Draw feedback
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    cv2.putText(frame, f"Collected: {collected}/{samples_per_class - samples_done}",
                               (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "No hand detected! Show your hand.",
                               (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                cv2.imshow('Data Collector', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            pbar.close()
            samples_collected[current_label] += collected
            print(f"✓ Collected {collected} samples for {current_label}")
            
            # Move to next gesture if done
            if samples_collected[current_label] >= samples_per_class:
                label_idx += 1
        
        elif key == ord('n'):
            label_idx += 1
        elif key == ord('p') and label_idx > 0:
            label_idx -= 1
    
    # Save combined data
    if all_landmarks:
        X_data = np.array(all_landmarks, dtype=np.float32)
        y_data = np.array(all_labels)
        
        np.save(os.path.join(data_dir, 'X_data.npy'), X_data)
        np.save(os.path.join(data_dir, 'y_data.npy'), y_data)
        
        print(f"\n✓ Saved combined data:")
        print(f"  X_data.npy: {X_data.shape}")
        print(f"  y_data.npy: {y_data.shape}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    
    # Print summary
    print("\n" + "="*60)
    print("COLLECTION SUMMARY")
    print("="*60)
    print(f"Total samples collected: {sum(samples_collected.values())}")
    print(f"Target samples: {len(labels) * samples_per_class}")
    print(f"Data saved to: {data_dir}")
    print("\nNext step: Train the model")
    print("  python model/train_model.py")


if __name__ == '__main__':
    collect_gesture_data(samples_per_class=200)
