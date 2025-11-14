import cv2
import numpy as np
import time
from threading import Thread
import winsound  # For Windows beep sound

class ImprovedDrowsinessDetector:
    def __init__(self, closed_eye_time_thresh=2.0, ear_thresh=0.15):
        """
        Improved drowsiness detector that detects closed eyes for 2+ seconds
        """
        self.CLOSED_EYE_TIME_THRESH = closed_eye_time_thresh  # 2 seconds
        self.EYE_AR_THRESH = ear_thresh  # Lower threshold for better detection
        
        # Time tracking
        self.eyes_closed_start_time = None
        self.ALARM_ON = False
        self.last_alarm_time = 0
        
        # Load OpenCV's pre-trained classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        print(f"[INFO] Drowsiness detector initialized!")
        print(f"[INFO] Will alert if eyes closed for {self.CLOSED_EYE_TIME_THRESH} seconds")
        print(f"[INFO] Eye aspect ratio threshold: {self.EYE_AR_THRESH}")
    
    def are_eyes_closed(self, eyes, face_roi):
        """Determine if eyes are closed based on detection and analysis"""
        if len(eyes) == 0:
            # No eyes detected - likely closed
            return True, 0.0
        
        if len(eyes) < 2:
            # Only one eye detected - might be closed or poor detection
            return True, 0.1
        
        # Sort eyes by x-coordinate to get left and right
        eyes = sorted(eyes, key=lambda x: x[0])
        
        # Calculate aspect ratio for detected eyes
        total_ear = 0
        valid_eyes = 0
        
        for (ex, ey, ew, eh) in eyes[:2]:  # Take first two eyes
            if ew > 10 and eh > 5:  # Minimum size check
                ear = eh / ew
                total_ear += ear
                valid_eyes += 1
        
        if valid_eyes == 0:
            return True, 0.0
        
        avg_ear = total_ear / valid_eyes
        eyes_closed = avg_ear < self.EYE_AR_THRESH
        
        return eyes_closed, avg_ear
    
    def sound_alarm(self):
        """Sound alarm with beep and message"""
        current_time = time.time()
        # Prevent alarm spam - only beep every 2 seconds
        if current_time - self.last_alarm_time > 2.0:
            print("🚨 DROWSINESS ALERT! WAKE UP! 🚨")
            try:
                # Windows system beep
                winsound.Beep(1000, 500)  # 1000Hz for 500ms
            except:
                print("\a")  # Fallback system bell
            self.last_alarm_time = current_time
    
    def detect_drowsiness(self, frame):
        """Process a single frame for drowsiness detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        current_time = time.time()
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        ear = 0.3  # Default EAR
        is_drowsy = False
        eyes_closed = False
        closed_duration = 0
        
        if len(faces) > 0:
            # Process the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Focus on upper half of face for better eye detection
            eye_region_y = y + int(h * 0.2)
            eye_region_h = int(h * 0.4)
            
            roi_gray = gray[eye_region_y:eye_region_y + eye_region_h, x:x+w]
            roi_color = frame[eye_region_y:eye_region_y + eye_region_h, x:x+w]
            
            # Detect eyes within the eye region
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3, minSize=(10, 10))
            
            # Draw rectangles around detected eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Check if eyes are closed
            eyes_closed, ear = self.are_eyes_closed(eyes, roi_gray)
            
            # Time-based drowsiness detection
            if eyes_closed:
                if self.eyes_closed_start_time is None:
                    self.eyes_closed_start_time = current_time
                
                closed_duration = current_time - self.eyes_closed_start_time
                
                # Check if eyes have been closed for threshold time
                if closed_duration >= self.CLOSED_EYE_TIME_THRESH:
                    if not self.ALARM_ON:
                        self.ALARM_ON = True
                        is_drowsy = True
                        
                        # Start alarm in separate thread
                        alarm_thread = Thread(target=self.sound_alarm)
                        alarm_thread.daemon = True
                        alarm_thread.start()
            else:
                # Eyes are open - reset timer
                self.eyes_closed_start_time = None
                self.ALARM_ON = False
        else:
            # No face detected - reset timer
            self.eyes_closed_start_time = None
            self.ALARM_ON = False
        
        # Display information
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        status = "CLOSED" if eyes_closed else "OPEN"
        color = (0, 0, 255) if eyes_closed else (0, 255, 0)
        cv2.putText(frame, f"Eyes: {status}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        if eyes_closed and closed_duration > 0:
            cv2.putText(frame, f"Closed: {closed_duration:.1f}s", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        if self.ALARM_ON:
            cv2.putText(frame, "DROWSINESS ALERT!", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
            # Flash effect
            if int(current_time * 4) % 2:
                cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 10)
        
        return frame, ear, is_drowsy
    
    def run_detection(self, source=0):
        """Run real-time drowsiness detection"""
        print("[INFO] Starting video stream...")
        print("[INFO] Press 'q' to quit, 'r' to reset alarm")
        
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            print("[ERROR] Could not open video source")
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[ERROR] Failed to read frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                processed_frame, ear, is_drowsy = self.detect_drowsiness(frame)
                
                # Add instructions
                cv2.putText(processed_frame, "Press 'q' to quit, 'r' to reset", 
                           (10, processed_frame.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow("Drowsiness Detection - Eyes Closed Alert", processed_frame)
                
                if is_drowsy:
                    print(f"[ALERT] Eyes closed for 2+ seconds! EAR: {ear:.2f}")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Reset alarm state
                    self.eyes_closed_start_time = None
                    self.ALARM_ON = False
                    print("[INFO] Alarm reset")
                    
        except KeyboardInterrupt:
            print("\n[INFO] Detection stopped by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("[INFO] Cleanup completed")