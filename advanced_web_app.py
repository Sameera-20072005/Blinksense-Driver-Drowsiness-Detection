import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import time
import plotly.graph_objects as go
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av
from collections import deque

# Page config with custom CSS
st.set_page_config(
    page_title="Drowsy Driver Detection System",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .alert-box {
        background: #fee;
        border: 2px solid #f56565;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .status-normal {
        background: #f0fff4;
        border: 2px solid #48bb78;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .status-warning {
        background: #fffbf0;
        border: 2px solid #ed8936;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedDrowsinessDetector(VideoTransformerBase):
    def __init__(self):
        self.ear_thresh = 0.25
        self.ear_consec_frames = 20
        self.counter = 0
        self.alarm_on = False
        
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        # Data tracking
        self.current_ear = 0.0
        self.ear_history = deque(maxlen=100)  # Last 100 EAR values
        self.alert_history = []
        self.session_start = time.time()
        self.total_alerts = 0
        
    def eye_aspect_ratio(self, landmarks, eye_points):
        coords = []
        for point in eye_points:
            x = landmarks[point].x
            y = landmarks[point].y
            coords.append([x, y])
        
        coords = np.array(coords)
        A = np.linalg.norm(coords[1] - coords[5])
        B = np.linalg.norm(coords[2] - coords[4])
        C = np.linalg.norm(coords[0] - coords[3])
        
        ear = (A + B) / (2.0 * C) if C > 0 else 0
        return ear
    
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        ear = 0.0
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                
                left_ear = self.eye_aspect_ratio(landmarks, self.LEFT_EYE)
                right_ear = self.eye_aspect_ratio(landmarks, self.RIGHT_EYE)
                ear = (left_ear + right_ear) / 2.0
                
                h, w = img.shape[:2]
                
                # Enhanced eye visualization
                for point in self.LEFT_EYE:
                    x = int(landmarks[point].x * w)
                    y = int(landmarks[point].y * h)
                    cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
                
                for point in self.RIGHT_EYE:
                    x = int(landmarks[point].x * w)
                    y = int(landmarks[point].y * h)
                    cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
                
                # Drowsiness detection logic
                if ear < self.ear_thresh:
                    self.counter += 1
                    if self.counter >= self.ear_consec_frames:
                        if not self.alarm_on:
                            self.total_alerts += 1
                            self.alert_history.append({
                                'timestamp': time.strftime("%H:%M:%S"),
                                'ear_value': ear,
                                'duration': time.time() - self.session_start
                            })
                            if len(self.alert_history) > 10:
                                self.alert_history.pop(0)
                        self.alarm_on = True
                else:
                    self.counter = 0
                    self.alarm_on = False
        
        self.current_ear = ear
        self.ear_history.append(ear)
        
        # Enhanced UI overlays
        self.draw_ui_overlays(img, ear)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")
    
    def draw_ui_overlays(self, img, ear):
        h, w = img.shape[:2]
        
        # Semi-transparent overlay panel
        overlay = img.copy()
        cv2.rectangle(overlay, (10, 10), (400, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        
        # Text information
        cv2.putText(img, f"EAR: {ear:.3f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"Threshold: {self.ear_thresh:.3f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f"Counter: {self.counter}/{self.ear_consec_frames}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f"Total Alerts: {self.total_alerts}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # EAR visualization bar
        bar_width = 300
        bar_height = 20
        bar_x, bar_y = 20, h - 50
        
        # Background bar
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # EAR level bar
        if ear > 0:
            fill_width = int((ear / 0.5) * bar_width)  # Normalize to 0.5 max
            color = (0, 255, 0) if ear > self.ear_thresh else (0, 0, 255)
            cv2.rectangle(img, (bar_x, bar_y), (bar_x + min(fill_width, bar_width), bar_y + bar_height), color, -1)
        
        # Threshold line
        thresh_x = bar_x + int((self.ear_thresh / 0.5) * bar_width)
        cv2.line(img, (thresh_x, bar_y - 5), (thresh_x, bar_y + bar_height + 5), (255, 255, 255), 2)
        
        if self.alarm_on:
            # Pulsing alert overlay
            pulse = int(abs(np.sin(time.time() * 10)) * 100)
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), -1)
            cv2.addWeighted(overlay, pulse/255.0 * 0.3, img, 1 - pulse/255.0 * 0.3, 0, img)
            
            cv2.putText(img, "DROWSINESS ALERT!", (w//2 - 200, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚗 Advanced Drowsy Driver Detection System</h1>
        <p>Real-time monitoring with comprehensive analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    ear_threshold = st.sidebar.slider("EAR Threshold", 0.15, 0.35, 0.25, 0.01)
    frame_threshold = st.sidebar.slider("Alert Frame Count", 10, 40, 20, 1)
    
    # Add system info
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 System Info")
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
    
    elapsed_time = time.time() - st.session_state.start_time
    st.sidebar.info(f"⏱️ Session: {elapsed_time/60:.1f} min")
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Live Detection Feed")
        
        RTC_CONFIGURATION = RTCConfiguration({
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        })
        
        webrtc_ctx = webrtc_streamer(
            key="advanced-drowsiness",
            video_transformer_factory=lambda: AdvancedDrowsinessDetector(),
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        if webrtc_ctx.video_transformer:
            webrtc_ctx.video_transformer.ear_thresh = ear_threshold
            webrtc_ctx.video_transformer.ear_consec_frames = frame_threshold
    
    with col2:
        st.subheader("📈 Analytics Dashboard")
        
        if webrtc_ctx.video_transformer:
            detector = webrtc_ctx.video_transformer
            
            # Current status
            if detector.alarm_on:
                st.markdown("""
                <div class="alert-box">
                    <h3>🚨 DROWSINESS DETECTED!</h3>
                    <p>Driver appears to be falling asleep</p>
                </div>
                """, unsafe_allow_html=True)
            elif detector.counter > 0:
                st.markdown(f"""
                <div class="status-warning">
                    <h4>⚠️ Eyes Closing</h4>
                    <p>Frames: {detector.counter}/{frame_threshold}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="status-normal">
                    <h4>✅ Driver Alert</h4>
                    <p>Eyes are open and attentive</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Metrics
            col2a, col2b = st.columns(2)
            with col2a:
                st.metric("Current EAR", f"{detector.current_ear:.3f}")
                st.metric("Total Alerts", detector.total_alerts)
            
            with col2b:
                st.metric("Frame Counter", f"{detector.counter}/{frame_threshold}")
                avg_ear = np.mean(list(detector.ear_history)) if detector.ear_history else 0
                st.metric("Avg EAR", f"{avg_ear:.3f}")
            
            # EAR History Plot
            if len(detector.ear_history) > 10:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=list(detector.ear_history),
                    mode='lines',
                    name='EAR',
                    line=dict(color='blue')
                ))
                fig.add_hline(y=ear_threshold, line_dash="dash", line_color="red", annotation_text="Threshold")
                fig.update_layout(
                    title="EAR History",
                    xaxis_title="Frames",
                    yaxis_title="EAR Value",
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent alerts
            st.subheader("🚨 Recent Alerts")
            if detector.alert_history:
                for i, alert in enumerate(reversed(detector.alert_history[-5:])):
                    st.text(f"Alert {len(detector.alert_history)-i}: {alert['timestamp']} (EAR: {alert['ear_value']:.3f})")
            else:
                st.info("No alerts recorded yet")

if __name__ == "__main__":
    main()
