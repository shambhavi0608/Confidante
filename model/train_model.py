"""
Model Training Script - CNN training for gesture recognition.

This script trains a TensorFlow CNN model to classify hand gestures
from landmark data extracted by MediaPipe.
"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json
import matplotlib.pyplot as plt


def build_model(input_shape, num_classes):
    """
    Build a CNN model for gesture classification.
    
    Args:
        input_shape (int): Input feature size (63 landmarks)
        num_classes (int): Number of gesture classes (39)
        
    Returns:
        tf.keras.Model: Compiled Keras model
        
    Example:
        model = build_model(input_shape=63, num_classes=39)
        model.summary()
    """
    model = Sequential([
        # Input layer
        Dense(512, activation='relu', input_shape=(input_shape,)),
        BatchNormalization(),
        Dropout(0.4),
        
        # Hidden layers
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        
        Dense(128, activation='relu'),
        Dropout(0.2),
        
        Dense(64, activation='relu'),
        
        # Output layer
        Dense(num_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def load_dataset(data_dir='data/gesture_dataset'):
    """
    Load gesture dataset from directory.
    
    Args:
        data_dir (str): Directory containing gesture data
        
    Returns:
        tuple: (X, y) - Features and labels numpy arrays
        
    Example:
        X, y = load_dataset('data/gesture_dataset')
        print(f"Loaded {X.shape[0]} samples")
    """
    # Define gesture labels
    labels = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
        'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'SPACE', 'CLEAR', 'NOTHING'
    ]
    
    X_data = []
    y_data = []
    
    # Try to load from individual class directories
    if os.path.exists(data_dir):
        for class_idx, label in enumerate(labels):
            class_dir = os.path.join(data_dir, label)
            if os.path.exists(class_dir):
                # Load all .npy files from this class directory
                for file in os.listdir(class_dir):
                    if file.endswith('.npy'):
                        try:
                            landmarks = np.load(os.path.join(class_dir, file))
                            if landmarks.shape == (63,):  # Valid landmark shape
                                X_data.append(landmarks)
                                y_data.append(class_idx)
                        except Exception as e:
                            print(f"Error loading {file}: {e}")
    
    # If data collected, use it
    if len(X_data) > 0:
        X = np.array(X_data, dtype=np.float32)
        y = np.array(y_data, dtype=np.int32)
        print(f"✓ Loaded {len(X)} real samples from {data_dir}")
        return X, y
    
    # Fallback: Generate synthetic data for demonstration
    print("⚠ No real data found. Generating synthetic data for demonstration...")
    X_synthetic = np.random.randn(2000, 63).astype(np.float32)
    y_synthetic = np.random.randint(0, 39, 2000)
    
    print(f"✓ Generated {len(X_synthetic)} synthetic samples")
    print("  NOTE: Train a real model by collecting gesture data:")
    print("  python data/collector.py")
    
    return X_synthetic, y_synthetic


def train_and_save_model():
    """
    Train CNN model and save weights, encoder, and history.
    
    Creates model/gesture_model.h5, model/label_encoder.pkl,
    and model/training_history.png
    
    Example:
        train_and_save_model()
    """
    print("\n" + "="*60)
    print("GESTURE RECOGNITION MODEL TRAINING")
    print("="*60 + "\n")
    
    # Create model directory if it doesn't exist
    os.makedirs('model', exist_ok=True)
    
    # Load dataset
    print("[1/5] Loading dataset...")
    X, y = load_dataset('data/gesture_dataset')
    print(f"Dataset shape: X={X.shape}, y={y.shape}")
    
    # Encode labels
    print("\n[2/5] Encoding labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Convert to categorical
    y_categorical = tf.keras.utils.to_categorical(y_encoded, num_classes=39)
    
    # Train-test split
    print("\n[3/5] Splitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_categorical, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Normalize features
    print("\n[4/5] Normalizing features...")
    X_train = (X_train - X_train.mean(axis=0)) / (X_train.std(axis=0) + 1e-8)
    X_test = (X_test - X_test.mean(axis=0)) / (X_test.std(axis=0) + 1e-8)
    
    # Build model
    print("\n[5/5] Building and training model...")
    model = build_model(input_shape=63, num_classes=39)
    print(f"\nModel architecture:")
    model.summary()
    
    # Define callbacks
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True
    )
    
    checkpoint = ModelCheckpoint(
        'model/gesture_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max'
    )
    
    # Train model
    print("\nTraining...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=32,
        callbacks=[early_stop, checkpoint],
        verbose=1
    )
    
    # Evaluate on test set
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {loss:.4f}")
    print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Save label encoder
    with open('model/label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    print("\n✓ Saved label encoder to model/label_encoder.pkl")
    
    # Save training history
    try:
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'], label='Training')
        plt.plot(history.history['val_accuracy'], label='Validation')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'], label='Training')
        plt.plot(history.history['val_loss'], label='Validation')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('model/training_history.png', dpi=100)
        print("✓ Saved training history plot to model/training_history.png")
        plt.close()
    except Exception as e:
        print(f"Warning: Could not save plot: {e}")
    
    # Save training info
    info = {
        'model_type': 'CNN',
        'input_shape': 63,
        'num_classes': 39,
        'training_samples': X_train.shape[0],
        'test_samples': X_test.shape[0],
        'test_accuracy': float(accuracy),
        'test_loss': float(loss),
        'epochs_trained': len(history.history['accuracy']),
        'labels': label_encoder.classes_.tolist()
    }
    
    with open('model/model_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    print("✓ Saved model info to model/model_info.json")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"Model saved to: model/gesture_model.h5")
    print(f"Test Accuracy: {accuracy*100:.2f}%")
    print("\nTo use the model in the app:")
    print("  streamlit run app.py")


if __name__ == '__main__':
    train_and_save_model()
