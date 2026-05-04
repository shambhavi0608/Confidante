"""
Helper Functions - Utility functions for the Sign Language project.

Contains common utilities for frame manipulation, visualization,
logging, and data management.
"""

import cv2
import numpy as np
import csv
import os
from datetime import datetime


def resize_frame(frame, width=640):
    """
    Resize a frame maintaining aspect ratio.
    
    Args:
        frame (np.ndarray): Input frame to resize
        width (int): Target width in pixels
        
    Returns:
        np.ndarray: Resized frame
        
    Example:
        resized = resize_frame(frame, width=480)
        print(resized.shape)  # (height, 480, 3)
    """
    if frame is None:
        return None
    
    height, orig_width = frame.shape[:2]
    ratio = width / float(orig_width)
    new_height = int(height * ratio)
    
    resized = cv2.resize(frame, (width, new_height), interpolation=cv2.INTER_AREA)
    return resized


def draw_info_panel(frame, info_dict, position='top-left', bg_color=(0, 0, 0), text_color=(255, 255, 255)):
    """
    Draw a semi-transparent information panel on a frame.
    
    Args:
        frame (np.ndarray): Input frame to draw on
        info_dict (dict): Information to display as key:value pairs
        position (str): Panel position ('top-left', 'top-right', 'bottom-left', 'bottom-right')
        bg_color (tuple): Background color in BGR
        text_color (tuple): Text color in BGR
        
    Returns:
        np.ndarray: Frame with drawn panel
        
    Example:
        info = {'Gesture': 'A', 'Confidence': '92%'}
        annotated = draw_info_panel(frame, info)
    """
    if frame is None:
        return None
    
    # Create copy to avoid modifying original
    annotated = frame.copy()
    height, width = frame.shape[:2]
    
    # Prepare text lines
    lines = [f"{k}: {v}" for k, v in info_dict.items()]
    
    # Calculate panel size
    line_height = 25
    panel_height = len(lines) * line_height + 20
    max_text_width = max([len(line) for line in lines]) * 12
    panel_width = max_text_width + 20
    
    # Determine panel position
    if position == 'top-left':
        x, y = 10, 10
    elif position == 'top-right':
        x, y = width - panel_width - 10, 10
    elif position == 'bottom-left':
        x, y = 10, height - panel_height - 10
    else:  # bottom-right
        x, y = width - panel_width - 10, height - panel_height - 10
    
    # Draw semi-transparent background
    overlay = annotated.copy()
    cv2.rectangle(overlay, (x, y), (x + panel_width, y + panel_height), bg_color, -1)
    cv2.addWeighted(overlay, 0.6, annotated, 0.4, 0, annotated)
    
    # Draw text
    for i, line in enumerate(lines):
        cv2.putText(annotated, line, 
                   (x + 10, y + 25 + i * line_height),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
    
    return annotated


def get_confidence_color(confidence):
    """
    Get BGR color based on confidence level.
    
    Args:
        confidence (float): Confidence score (0-1)
        
    Returns:
        tuple: BGR color (B, G, R)
        
    Example:
        color = get_confidence_color(0.85)  # Returns (0, 255, 0) - Green
    """
    if confidence > 0.8:
        return (0, 255, 0)      # Green - High confidence
    elif confidence > 0.6:
        return (0, 165, 255)    # Orange - Medium confidence
    else:
        return (0, 0, 255)      # Red - Low confidence


def format_confidence_display(confidence):
    """
    Format confidence score as percentage string.
    
    Args:
        confidence (float): Confidence score (0-1)
        
    Returns:
        str: Formatted confidence string (e.g., "94.2%")
        
    Example:
        conf_str = format_confidence_display(0.942)
        print(conf_str)  # "94.2%"
    """
    return f"{confidence * 100:.1f}%"


def save_conversation_log(sentences, emotions=None, filename='conversation_log.csv'):
    """
    Save conversation sentences to CSV file.
    
    Args:
        sentences (list): List of sentence strings
        emotions (list): List of emotion strings (optional)
        filename (str): Output CSV filename
        
    Example:
        save_conversation_log(['Hello', 'How are you'], 
                             ['happy', 'neutral'],
                             'my_conversation.csv')
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            if emotions:
                writer.writerow(['Timestamp', 'Sentence', 'Emotion'])
            else:
                writer.writerow(['Timestamp', 'Sentence'])
            
            # Write data
            for i, sentence in enumerate(sentences):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                emotion = emotions[i] if emotions and i < len(emotions) else ''
                
                if emotions:
                    writer.writerow([timestamp, sentence, emotion])
                else:
                    writer.writerow([timestamp, sentence])
        
        print(f"✓ Conversation saved to {filename}")
        return True
        
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return False


def load_conversation_log(filename='conversation_log.csv'):
    """
    Load conversation from CSV file.
    
    Args:
        filename (str): Input CSV filename
        
    Returns:
        tuple: (sentences, emotions) or (None, None) if file doesn't exist
        
    Example:
        sentences, emotions = load_conversation_log('my_conversation.csv')
        print(f"Loaded {len(sentences)} sentences")
    """
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return None, None
    
    try:
        sentences = []
        emotions = []
        
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            
            for row in reader:
                if len(row) >= 2:
                    sentences.append(row[1])  # Sentence is second column
                    if len(row) >= 3 and len(header) >= 3:
                        emotions.append(row[2])  # Emotion is third column
        
        print(f"✓ Loaded {len(sentences)} sentences from {filename}")
        return sentences, emotions if emotions else None
        
    except Exception as e:
        print(f"Error loading conversation: {e}")
        return None, None


def get_frame_info(frame):
    """
    Get information about a frame.
    
    Args:
        frame (np.ndarray): Input frame
        
    Returns:
        dict: Frame information (height, width, channels)
        
    Example:
        info = get_frame_info(frame)
        print(f"Frame size: {info['width']}x{info['height']}")
    """
    if frame is None:
        return {'width': 0, 'height': 0, 'channels': 0}
    
    height, width = frame.shape[:2]
    channels = frame.shape[2] if len(frame.shape) > 2 else 1
    
    return {
        'height': height,
        'width': width,
        'channels': channels,
        'size': height * width
    }


def create_blank_frame(width=640, height=480, color=(0, 0, 0)):
    """
    Create a blank frame with specified dimensions and color.
    
    Args:
        width (int): Frame width
        height (int): Frame height
        color (tuple): BGR color
        
    Returns:
        np.ndarray: Blank frame
        
    Example:
        blank = create_blank_frame(640, 480, color=(255, 255, 255))
    """
    return np.full((height, width, 3), color, dtype=np.uint8)


def draw_centered_text(frame, text, font_scale=1.5, color=(255, 255, 255)):
    """
    Draw text centered on a frame.
    
    Args:
        frame (np.ndarray): Frame to draw on
        text (str): Text to display
        font_scale (float): Font size scale
        color (tuple): Text color in BGR
        
    Returns:
        np.ndarray: Frame with centered text
        
    Example:
        frame = draw_centered_text(frame, "Press SPACE to start")
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
    
    height, width = frame.shape[:2]
    x = (width - text_size[0]) // 2
    y = (height + text_size[1]) // 2
    
    cv2.putText(frame, text, (x, y), font, font_scale, color, 2)
    return frame
