import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
from PIL import Image
import threading

st.title("🚗 Simple Camera Drowsiness Detection")

# Initialize MediaPipe
@st.cache_resource
def load_mediapipe():
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.3,
        min_tracking_confidence=0.3
    )
    return face_mesh, mp_face_mesh

def process_frame(frame, face_mesh, ear_threshold=0.25):
    """Process single frame for drowsiness detection"""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    ear = 0.0
    face_detected = False
    
    if results.multi_face_landmarks:
        face_detected = True
        for landmarks in results.multi_face_landmarks:
            # Simple EAR calculation
            h, w = frame.shape[:2]
            
            # Left eye landmarks
            left_eye = [362, 385, 387, 263, 373, 380]
            right_eye = [33, 160, 158, 133, 153, 144]
            
            # Calculate EAR
            left_coords = [(landmarks.landmark[i].x * w, landmarks.landmark[i].y * h) for i in left_eye]
            right_coords = [(landmarks.landmark[i].x * w, landmarks.landmark[i].y * h) for i in right_eye]
            
            # Draw landmarks
            for x, y in left_coords + right_coords:
                cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)
            
            # Simple EAR calculation
            def eye_aspect_ratio(coords):
                coords = np.array(coords)
                A = np.linalg.norm(coords[1] - coords[5])
                B = np.linalg.norm(coords[2] - coords[4])
                C = np.linalg.norm(coords[0] - coords[3])
                return (A + B) / (2.0 * C) if C > 0 else 0
            
            left_ear = eye_aspect_ratio(left_coords)
            right_ear = eye_aspect_ratio(right_coords)
            ear = (left_ear + right_ear) / 2.0
    
    # Add text overlay
    cv2.putText(frame, f"EAR: {ear:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Face: {'DETECTED' if face_detected else 'NOT FOUND'}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if face_detected else (0, 0, 255), 2)
    
    if ear < ear_threshold and ear > 0:
        cv2.putText(frame, "DROWSY!", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    return frame, ear, face_detected

# Streamlit interface
face_mesh, mp_face_mesh = load_mediapipe()

ear_threshold = st.sidebar.slider("EAR Threshold", 0.15, 0.35, 0.25, 0.01)

# Camera input
run = st.checkbox('Run Detection')
FRAME_WINDOW = st.image([])

if run:
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("Cannot open camera. Please check camera permissions.")
    else:
        st.success("Camera opened successfully!")
        
        while run:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read from camera")
                break
            
            # Process frame
            processed_frame, ear, face_detected = process_frame(frame, face_mesh, ear_threshold)
            
            # Convert to RGB for Streamlit
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            # Display
            FRAME_WINDOW.image(processed_frame)
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("EAR", f"{ear:.4f}")
            with col2:
                st.metric("Status", "ALERT" if face_detected else "NO FACE")
            
            time.sleep(0.1)
        
        cap.release()
