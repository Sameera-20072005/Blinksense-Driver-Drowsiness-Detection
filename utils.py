import numpy as np
from scipy.spatial import distance as dist
import cv2

def eye_aspect_ratio(eye):
    """
    Calculate the Eye Aspect Ratio (EAR) for drowsiness detection
    Args:
        eye: Array of (x,y) coordinates for eye landmarks
    Returns:
        EAR value
    """
    # Compute the euclidean distances between the vertical eye landmarks
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    
    # Compute the euclidean distance between the horizontal eye landmarks
    C = dist.euclidean(eye[0], eye[3])
    
    # Calculate the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    
    return ear

def draw_eye_landmarks(frame, eye, color=(0, 255, 0)):
    """
    Draw eye landmarks on the frame
    Args:
        frame: Video frame
        eye: Eye landmark coordinates
        color: BGR color tuple
    """
    eye_hull = cv2.convexHull(eye)
    cv2.drawContours(frame, [eye_hull], -1, color, 1)

def display_info(frame, ear, counter, alarm_on):
    """
    Display EAR value and status information on frame
    """
    cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    cv2.putText(frame, f"Counter: {counter}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    if alarm_on:
        cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
