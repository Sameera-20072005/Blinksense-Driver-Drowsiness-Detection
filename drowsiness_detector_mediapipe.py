import cv2
import mediapipe as mp
import numpy as np
from imutils.video import VideoStream
from threading import Thread
import time
try:
    import playsound
except ImportError:
    print("Warning: playsound not available. Using console alerts only.")
    playsound = None

class DrowsinessDetectorMediaPipe:
    def __init__(self, 
                 alarm_path="data/sounds/alarm.wav",
                 ear_thresh=0.25,
                 ear_consec_frames=20):
        """
        Initialize the Drowsiness Detector using MediaPipe
        """
        self.alarm_path = alarm_path
        self.EYE_AR_THRESH = ear_thresh
        self.EYE_AR_CONSEC_FRAMES = ear_consec_frames
        
        # Initialize counters
        self.COUNTER = 0
        self.ALARM_ON = False
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Eye landmark indices for MediaPipe (468 face landmarks)
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        print("[INFO] MediaPipe Drowsiness detector initialized successfully!")
    
    def eye_aspect_ratio(self, landmarks, eye_points):
        """Calculate Eye Aspect Ratio using MediaPipe landmarks"""
        # Get coordinates
        coords = []
        for point in eye_points:
            x = landmarks[point].x
            y = landmarks[point].y
            coords.append([x, y])
        
        coords = np.array(coords)
        
        # Calculate EAR using simplified method for MediaPipe
        # Using 6 key points similar to dlib
        A = np.linalg.norm(coords[1] - coords[5])  # Vertical 1
        B = np.linalg.norm(coords[2] - coords[4])  # Vertical 2  
        C = np.linalg.norm(coords[0] - coords[3])  # Horizontal
        
        ear = (A + B) / (2.0 * C)
        return ear
    
    def sound_alarm(self):
        """Play alarm sound in a separate thread"""
        try:
            if self.alarm_path and playsound:
                playsound.playsound(self.alarm_path)
            else:
                print("🚨 DROWSINESS ALERT! 🚨")
        except Exception as e:
            print(f"[ALERT] Drowsiness detected! (Sound error: {e})")
    
    def detect_drowsiness(self, frame):
        """Process a single frame for drowsiness detection"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        ear = 0.0
        is_drowsy = False
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get landmarks
                landmarks = face_landmarks.landmark
                
                # Calculate EAR for both eyes
                left_ear = self.eye_aspect_ratio(landmarks, self.LEFT_EYE[:6])
                right_ear = self.eye_aspect_ratio(landmarks, self.RIGHT_EYE[:6])
                
                # Average EAR
                ear = (left_ear + right_ear) / 2.0
                
                # Draw eye landmarks
                for point in self.LEFT_EYE[:6]:
                    x = int(landmarks[point].x * frame.shape[1])
                    y = int(landmarks[point].y * frame.shape[0])
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                
                for point in self.RIGHT_EYE[:6]:
                    x = int(landmarks[point].x * frame.shape[1])
                    y = int(landmarks[point].y * frame.shape[0])
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                
                # Check for drowsiness
                if ear < self.EYE_AR_THRESH:
                    self.COUNTER += 1
                    
                    if self.COUNTER >= self.EYE_AR_CONSEC_FRAMES:
                        if not self.ALARM_ON:
                            self.ALARM_ON = True
                            is_drowsy = True
                            
                            # Start alarm in separate thread
                            alarm_thread = Thread(target=self.sound_alarm)
                            alarm_thread.daemon = True
                            alarm_thread.start()
                else:
                    self.COUNTER = 0
                    self.ALARM_ON = False
        
        # Display information
        cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Counter: {self.COUNTER}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        if self.ALARM_ON:
            cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame, ear, is_drowsy
    
    def run_detection(self, source=0):
        """Run real-time drowsiness detection"""
        print("[INFO] Starting video stream...")
        vs = VideoStream(src=source).start()
        time.sleep(2.0)
        
        try:
            while True:
                frame = vs.read()
                if frame is None:
                    break
                
                frame = cv2.resize(frame, (640, 480))
                processed_frame, ear, is_drowsy = self.detect_drowsiness(frame)
                
                cv2.imshow("MediaPipe Drowsiness Detection", processed_frame)
                
                if is_drowsy:
                    print(f"[ALERT] Drowsiness detected! EAR: {ear:.2f}")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n[INFO] Detection stopped by user")
        
        finally:
            cv2.destroyAllWindows()
            vs.stop()
            print("[INFO] Cleanup completed")
