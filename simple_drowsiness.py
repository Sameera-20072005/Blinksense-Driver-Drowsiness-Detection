import cv2
import time
import winsound

def main():
    print("Starting BlinkSense - Driver Drowsiness Detection")
    print("Press 'q' to quit")
    
    # Load face and eye cascades
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Variables for drowsiness detection
    closed_start = None
    drowsy_threshold = 2.0  # seconds
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        eyes_open = False
        
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 182, 193), 2)
            
            # Region of interest for eyes
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Detect eyes
            eyes = eye_cascade.detectMultiScale(roi_gray)
            
            if len(eyes) >= 2:
                eyes_open = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (173, 216, 230), 2)
        
        # Drowsiness detection logic
        current_time = time.time()
        
        if not eyes_open and len(faces) > 0:
            if closed_start is None:
                closed_start = current_time
            elif current_time - closed_start >= drowsy_threshold:
                # Alert for drowsiness
                cv2.putText(frame, "DROWSY! WAKE UP!", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                cv2.putText(frame, "ALERT!", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                # Play alarm sound
                winsound.Beep(1000, 500)  # 1000Hz for 500ms
        else:
            closed_start = None
        
        # Status display
        if len(faces) == 0:
            cv2.putText(frame, "No face detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        elif eyes_open:
            cv2.putText(frame, "Eyes Open - Safe", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Eyes Closed", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Instructions
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show frame
        cv2.imshow('BlinkSense - Driver Drowsiness Detection', frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("BlinkSense stopped")

if __name__ == "__main__":
    main()