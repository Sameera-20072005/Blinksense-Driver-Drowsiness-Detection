import cv2
import numpy as np
import time
from threading import Thread

class SimpleDrowsinessDetector:
    def __init__(self, ear_thresh=0.25, ear_consec_frames=20):
        """
        Simple drowsiness detector using OpenCV's built-in face detection
        """
        self.EYE_AR_THRESH = ear_thresh
        self.EYE_AR_CONSEC_FRAMES = ear_consec_frames
        
        # Initialize counters
        self.COUNTER = 0
        self.ALARM_ON = False
        
        # Load OpenCV's pre-trained face and eye cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        print("[INFO] Simple Drowsiness detector initialized successfully!")
    
    def calculate_ear_from_eyes(self, eyes, face_roi):
        """Calculate a simple EAR approximation from detected eyes"""
        if len(eyes) < 2:
            return 0.3  # Default value when eyes not detected properly
        
        # Sort eyes by x-coordinate to get left and right
        eyes = sorted(eyes, key=lambda x: x[0])
        
        # Calculate aspect ratio for each eye
        ears = []
        for (ex, ey, ew, eh) in eyes[:2]:  # Take first two eyes
            # Simple approximation: height/width ratio
            ear = eh / ew if ew > 0 else 0.3
            ears.append(ear)
        
        # Return average EAR
        return sum(ears) / len(ears) if ears else 0.3
    
    def sound_alarm(self):
        """Print alarm message (since playsound might not work)"""
        print("🚨 DROWSINESS ALERT! WAKE UP! 🚨")
        # You could add system beep here if needed
        # import winsound; winsound.Beep(1000, 1000)  # Windows only
    
    def detect_drowsiness(self, frame):
        """Process a single frame for drowsiness detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        ear = 0.3  # Default EAR
        is_drowsy = False
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Region of interest for eyes
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Detect eyes within the face
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            # Draw rectangles around eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Calculate EAR approximation
            ear = self.calculate_ear_from_eyes(eyes, roi_gray)
            
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
            
            break  # Process only first face
        
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
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            print("[ERROR] Could not open video source")
            return
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.resize(frame, (640, 480))
                processed_frame, ear, is_drowsy = self.detect_drowsiness(frame)
                
                cv2.imshow("Simple Drowsiness Detection", processed_frame)
                
                if is_drowsy:
                    print(f"[ALERT] Drowsiness detected! EAR: {ear:.2f}")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n[INFO] Detection stopped by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("[INFO] Cleanup completed")