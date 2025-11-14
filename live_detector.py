import cv2
import time
import winsound
from threading import Thread

class LiveDrowsinessDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.eyes_closed_start = None
        self.alarm_active = False
        self.alarm_thread = None
        self.stop_alarm = False
        
    def detect_and_alert(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("Camera not found!")
            return
            
        print("Live detection started. Press 'q' to quit.")
        print("Alarm will sound if eyes closed for 2+ seconds.")
        print("EAR threshold: 0.2 (below = closed eyes)")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    # Focus on eye region (upper 40% of face)
                    eye_y = y + int(h * 0.15)
                    eye_h = int(h * 0.4)
                    roi_gray = gray[eye_y:eye_y+eye_h, x:x+w]
                    roi_color = frame[eye_y:eye_y+eye_h, x:x+w]
                    
                    # Draw eye region rectangle
                    cv2.rectangle(frame, (x, eye_y), (x+w, eye_y+eye_h), (0, 255, 255), 2)
                    
                    eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3, minSize=(15, 10))
                    
                    # Draw detected eyes
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                        cv2.circle(roi_color, (ex + ew//2, ey + eh//2), 3, (255, 0, 0), -1)
                    
                    current_time = time.time()
                    
                    # Calculate EAR
                    ear = self.calculate_ear(eyes)
                    
                    # Check if eyes are closed (EAR < 0.2 OR less than 2 eyes detected)
                    eyes_closed = (ear < 0.2) or (len(eyes) < 2)
                    
                    if eyes_closed:
                        if self.eyes_closed_start is None:
                            self.eyes_closed_start = current_time
                        
                        closed_duration = current_time - self.eyes_closed_start
                        
                        if closed_duration >= 2.0 and not self.alarm_active:
                            self.alarm_active = True
                            self.start_continuous_alarm()
                            print(f"DROWSINESS ALERT! Eyes closed for {closed_duration:.1f}s")
                        
                        cv2.putText(frame, f"EYES CLOSED: {closed_duration:.1f}s", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, f"EAR: {ear:.3f}", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                        cv2.putText(frame, f"Eyes detected: {len(eyes)}", 
                                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        
                        # Show countdown to alarm
                        if closed_duration < 2.0:
                            remaining = 2.0 - closed_duration
                            cv2.putText(frame, f"Alarm in: {remaining:.1f}s", 
                                       (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                        
                        if self.alarm_active:
                            cv2.putText(frame, "WAKE UP!", (10, 90), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    else:
                        self.eyes_closed_start = None
                        if self.alarm_active:
                            self.stop_continuous_alarm()
                        self.alarm_active = False
                        cv2.putText(frame, "Eyes open", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"EAR: {ear:.3f}", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"Eyes detected: {len(eyes)}", 
                                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Add status bar
                status = "MONITORING" if not self.alarm_active else "ALARM ACTIVE"
                color = (0, 255, 0) if not self.alarm_active else (0, 0, 255)
                cv2.putText(frame, f"Status: {status}", (frame.shape[1] - 200, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                cv2.imshow('Live Drowsiness Detection', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            if self.alarm_active:
                self.stop_continuous_alarm()
            cap.release()
            cv2.destroyAllWindows()
            print("Camera closed automatically.")
    
    def calculate_ear(self, eyes):
        """Calculate Eye Aspect Ratio"""
        if len(eyes) == 0:
            return 0.05  # Very low EAR for no eyes detected
        elif len(eyes) == 1:
            return 0.1   # Low EAR for one eye detected
        
        total_ear = 0
        valid_eyes = 0
        
        for (ex, ey, ew, eh) in eyes[:2]:
            if ew > 10 and eh > 5:  # Valid eye size
                ear = eh / ew
                total_ear += ear
                valid_eyes += 1
        
        if valid_eyes == 0:
            return 0.1
        
        avg_ear = total_ear / valid_eyes
        return avg_ear
    
    def continuous_alarm(self):
        """Play alarm continuously until stopped"""
        while not self.stop_alarm:
            try:
                winsound.Beep(1000, 300)
                time.sleep(0.5)
            except:
                break
    
    def start_continuous_alarm(self):
        """Start continuous alarm in separate thread"""
        if self.alarm_thread is None or not self.alarm_thread.is_alive():
            self.stop_alarm = False
            self.alarm_thread = Thread(target=self.continuous_alarm)
            self.alarm_thread.daemon = True
            self.alarm_thread.start()
    
    def stop_continuous_alarm(self):
        """Stop continuous alarm"""
        self.stop_alarm = True
        if self.alarm_thread and self.alarm_thread.is_alive():
            self.alarm_thread.join(timeout=1)

if __name__ == "__main__":
    detector = LiveDrowsinessDetector()
    detector.detect_and_alert()