import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
from PIL import Image
import threading
import queue

# Page configuration
st.set_page_config(
    page_title="Working Camera Drowsiness Detection",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .alert-danger {
        background: #fee;
        border: 2px solid #f56565;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        color: #c53030;
        font-weight: bold;
        animation: pulse 1s infinite;
    }
    
    .alert-success {
        background: #f0fff4;
        border: 2px solid #48bb78;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        color: #2f855a;
        font-weight: bold;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

class CameraManager:
    def __init__(self):
        self.cap = None
        self.camera_index = 0
        self.is_running = False
        
    def find_working_camera(self):
        """Find the first working camera"""
        for i in range(3):  # Check cameras 0, 1, 2
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cap.release()
                    return i
            cap.release()
        return None
    
    def initialize_camera(self):
        """Initialize camera with best settings"""
        camera_idx = self.find_working_camera()
        
        if camera_idx is None:
            return False, "No working camera found"
        
        self.camera_index = camera_idx
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            return False, f"Cannot open camera {self.camera_index}"
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
        self.cap.set(cv2.CAP_PROP_CONTRAST, 0.5)
        
        return True, f"Camera {self.camera_index} initialized successfully"
    
    def read_frame(self):
        """Read frame from camera"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return cv2.flip(frame, 1)  # Mirror effect
        return None
    
    def release(self):
        """Release camera"""
        if self.cap:
            self.cap.release()

class DrowsinessDetector:
    def __init__(self):
        # Initialize MediaPipe with optimized settings
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.3,  # Lower for better detection
            min_tracking_confidence=0.3    # Lower for better tracking
        )
        
        # Eye landmarks (6 points each for EAR calculation)
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        # Additional eye points for better visualization
        self.LEFT_EYE_FULL = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        self.RIGHT_EYE_FULL = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # Detection parameters
        self.ear_threshold = 0.25
        self.frame_threshold = 20
        self.counter = 0
        self.total_alerts = 0
        self.alert_history = []
        
        # Metrics
        self.current_ear = 0.0
        self.avg_ear = 0.0
        self.ear_history = []
        
    def eye_aspect_ratio(self, landmarks, eye_points, frame_shape):
        """Calculate Eye Aspect Ratio with improved accuracy"""
        h, w = frame_shape[:2]
        
        # Get eye coordinates
        coords = []
        for point in eye_points:
            x = landmarks.landmark[point].x * w
            y = landmarks.landmark[point].y * h
            coords.append([x, y])
        
        coords = np.array(coords)
        
        # Calculate EAR using the standard formula
        # Vertical distances
        A = np.linalg.norm(coords[1] - coords[5])  # Top outer to bottom outer
        B = np.linalg.norm(coords[2] - coords[4])  # Top inner to bottom inner
        
        # Horizontal distance
        C = np.linalg.norm(coords[0] - coords[3])  # Left corner to right corner
        
        # EAR calculation with error handling
        if C > 0:
            ear = (A + B) / (2.0 * C)
        else:
            ear = 0.0
        
        return max(0.0, min(1.0, ear))  # Clamp between 0 and 1
    
    def draw_enhanced_landmarks(self, frame, landmarks):
        """Draw enhanced eye landmarks"""
        h, w = frame.shape[:2]
        
        # Draw full eye contours
        for eye_points in [self.LEFT_EYE_FULL, self.RIGHT_EYE_FULL]:
            points = []
            for point in eye_points:
                x = int(landmarks.landmark[point].x * w)
                y = int(landmarks.landmark[point].y * h)
                points.append((x, y))
                # Draw individual points
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
            # Draw eye outline
            if len(points) > 6:
                eye_hull = cv2.convexHull(np.array(points, dtype=np.int32))
                cv2.drawContours(frame, [eye_hull], -1, (0, 255, 0), 2)
    
    def process_frame(self, frame):
        """Process frame for drowsiness detection"""
        if frame is None:
            return None, 0.0, False, "No frame"
        
        h, w = frame.shape[:2]
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.face_mesh.process(rgb_frame)
        
        ear = 0.0
        face_detected = False
        status = "No face detected"
        
        if results.multi_face_landmarks:
            face_detected = True
            
            for landmarks in results.multi_face_landmarks:
                # Calculate EAR for both eyes
                left_ear = self.eye_aspect_ratio(landmarks, self.LEFT_EYE, frame.shape)
                right_ear = self.eye_aspect_ratio(landmarks, self.RIGHT_EYE, frame.shape)
                
                # Average EAR
                ear = (left_ear + right_ear) / 2.0
                
                # Draw enhanced landmarks
                self.draw_enhanced_landmarks(frame, landmarks)
                
                # Update EAR history
                self.ear_history.append(ear)
                if len(self.ear_history) > 50:  # Keep last 50 values
                    self.ear_history.pop(0)
                
                self.avg_ear = np.mean(self.ear_history) if self.ear_history else 0.0
                
                # Drowsiness detection logic
                if ear < self.ear_threshold:
                    self.counter += 1
                    status = f"Eyes closing... ({self.counter}/{self.frame_threshold})"
                    
                    if self.counter >= self.frame_threshold:
                        self.total_alerts += 1
                        self.alert_history.append({
                            'timestamp': time.strftime("%H:%M:%S"),
                            'ear': ear
                        })
                        if len(self.alert_history) > 10:
                            self.alert_history.pop(0)
                        
                        status = "DROWSINESS ALERT!"
                else:
                    self.counter = 0
                    status = "Driver alert"
        
        self.current_ear = ear
        
        # Add text overlays
        self.draw_ui_overlay(frame, ear, face_detected, status)
        
        return frame, ear, face_detected, status
    
    def draw_ui_overlay(self, frame, ear, face_detected, status):
        """Draw comprehensive UI overlay"""
        h, w = frame.shape[:2]
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (450, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Main metrics
        cv2.putText(frame, f"EAR: {ear:.4f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Threshold: {self.ear_threshold:.3f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Counter: {self.counter}/{self.frame_threshold}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Avg EAR: {self.avg_ear:.3f}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Face detection status
        status_color = (0, 255, 0) if face_detected else (0, 0, 255)
        cv2.putText(frame, f"Face: {'DETECTED' if face_detected else 'NOT FOUND'}", 
                   (250, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # EAR visualization bar
        bar_x, bar_y = 20, h - 50
        bar_w, bar_h = 400, 25
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
        
        # EAR level
        if ear > 0:
            fill_w = int(min(ear / 0.5, 1.0) * bar_w)
            color = (0, 255, 0) if ear > self.ear_threshold else (0, 100, 255)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), color, -1)
        
        # Threshold marker
        thresh_x = bar_x + int((self.ear_threshold / 0.5) * bar_w)
        cv2.line(frame, (thresh_x, bar_y - 10), (thresh_x, bar_y + bar_h + 10), (255, 255, 255), 3)
        cv2.putText(frame, f"{self.ear_threshold:.2f}", (thresh_x - 25, bar_y - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Alert overlay
        if self.counter >= self.frame_threshold:
            # Pulsing red overlay
            pulse = int(abs(np.sin(time.time() * 8)) * 100)
            alert_overlay = frame.copy()
            cv2.rectangle(alert_overlay, (0, 0), (w, h), (0, 0, 255), -1)
            cv2.addWeighted(alert_overlay, pulse/255.0 * 0.4, frame, 1 - pulse/255.0 * 0.4, 0, frame)
            
            # Alert text
            text = "DROWSINESS ALERT!"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            text_x = (w - text_size[0]) // 2
            text_y = h // 2
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

def main():
    st.title("🚗 Working Camera Drowsiness Detection")
    st.markdown("### Enhanced detection with direct camera access")
    
    # Sidebar controls
    st.sidebar.title("🎛️ Detection Settings")
    ear_threshold = st.sidebar.slider("EAR Threshold", 0.15, 0.40, 0.25, 0.01)
    frame_threshold = st.sidebar.slider("Alert Frame Count", 5, 50, 20, 1)
    
    # Camera controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("📹 Camera Controls")
    
    # Initialize session state
    if 'camera_manager' not in st.session_state:
        st.session_state.camera_manager = CameraManager()
        st.session_state.detector = DrowsinessDetector()
        st.session_state.is_running = False
    
    # Update detector settings
    st.session_state.detector.ear_threshold = ear_threshold
    st.session_state.detector.frame_threshold = frame_threshold
    
    # Camera initialization
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Find Camera"):
            camera_idx = st.session_state.camera_manager.find_working_camera()
            if camera_idx is not None:
                st.success(f"✅ Found working camera at index {camera_idx}")
            else:
                st.error("❌ No working camera found")
    
    with col2:
        if st.button("📷 Initialize Camera"):
            success, message = st.session_state.camera_manager.initialize_camera()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Live Camera Feed")
        
        # Start/Stop buttons
        col1a, col1b = st.columns(2)
        
        with col1a:
            if st.button("▶️ Start Detection", type="primary"):
                success, message = st.session_state.camera_manager.initialize_camera()
                if success:
                    st.session_state.is_running = True
                    st.success("Detection started!")
                else:
                    st.error(f"Failed to start: {message}")
        
        with col1b:
            if st.button("⏹️ Stop Detection"):
                st.session_state.is_running = False
                st.session_state.camera_manager.release()
                st.info("Detection stopped")
        
        # Video display
        frame_placeholder = st.empty()
        
    with col2:
        st.subheader("📊 Detection Metrics")
        
        # Metrics placeholders
        status_placeholder = st.empty()
        ear_metric = st.empty()
        counter_metric = st.empty()
        alerts_metric = st.empty()
        
        # Alert history
        st.subheader("📋 Alert History")
        alert_placeholder = st.empty()
    
    # Main detection loop
    if st.session_state.is_running:
        detector = st.session_state.detector
        
        while st.session_state.is_running:
            frame = st.session_state.camera_manager.read_frame()
            
            if frame is not None:
                # Process frame
                processed_frame, ear, face_detected, status = detector.process_frame(frame)
                
                if processed_frame is not None:
                    # Convert BGR to RGB for Streamlit
                    rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(rgb_frame, channels="RGB", use_column_width=True)
                    
                    # Update metrics
                    if detector.counter >= detector.frame_threshold:
                        status_placeholder.markdown("""
                        <div class="alert-danger">
                            🚨 DROWSINESS DETECTED!
                        </div>
                        """, unsafe_allow_html=True)
                    elif face_detected:
                        status_placeholder.markdown("""
                        <div class="alert-success">
                            ✅ Driver Alert - Face Detected
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        status_placeholder.error("❌ No Face Detected")
                    
                    # Update metrics
                    ear_metric.metric("Current EAR", f"{ear:.4f}", 
                                     delta=f"{ear - ear_threshold:.3f}")
                    counter_metric.metric("Frame Counter", 
                                         f"{detector.counter}/{frame_threshold}")
                    alerts_metric.metric("Total Alerts", detector.total_alerts)
                    
                    # Alert history
                    if detector.alert_history:
                        alert_text = "\n".join([
                            f"🚨 {alert['timestamp']}: EAR {alert['ear']:.3f}"
                            for alert in detector.alert_history[-5:]
                        ])
                        alert_placeholder.text(alert_text)
                    else:
                        alert_placeholder.info("No alerts yet")
            
            else:
                frame_placeholder.error("❌ Cannot read from camera")
                st.session_state.is_running = False
            
            # Small delay to prevent overwhelming
            time.sleep(0.033)  # ~30 FPS
    
    # Instructions
    st.markdown("---")
    st.subheader("📋 Instructions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔧 Setup:**
        1. Click "Find Camera"
        2. Click "Initialize Camera"
        3. Click "Start Detection"
        4. Ensure good lighting
        """)
    
    with col2:
        st.markdown("""
        **⚙️ Settings:**
        - Lower EAR threshold = more sensitive
        - Higher frame count = fewer false alarms
        - Adjust based on your face and lighting
        """)
    
    with col3:
        st.markdown("""
        **📈 Monitoring:**
        - Green dots = eye landmarks detected
        - EAR bar shows eye openness
        - Red flash = drowsiness alert
        """)

if __name__ == "__main__":
    main()
