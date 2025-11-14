import cv2
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_opencv():
    """Test basic OpenCV functionality"""
    print("Testing OpenCV installation...")
    print(f"OpenCV version: {cv2.__version__}")
    
    # Test face cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    if face_cascade.empty():
        print("ERROR: Face cascade not loaded")
        return False
    
    if eye_cascade.empty():
        print("ERROR: Eye cascade not loaded")
        return False
    
    print("Face and eye cascades loaded successfully!")
    return True

def test_camera():
    """Simple camera test"""
    print("Testing camera...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not available - trying DirectShow backend...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("No camera available")
        return False
    
    print("Camera opened successfully!")
    
    # Try to read a frame
    ret, frame = cap.read()
    if ret:
        print("Frame read successfully!")
        print(f"Frame shape: {frame.shape}")
    else:
        print("Failed to read frame")
        cap.release()
        return False
    
    cap.release()
    return True

def run_simple_detection():
    """Run a simple face detection test"""
    print("\nStarting simple face detection...")
    print("Press 'q' to quit")
    
    # Load cascades
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    # Open camera with DirectShow backend for Windows
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("Failed to open camera")
        return
    
    # Set properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    eyes_closed_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Eye region
            roi_gray = gray[y:y+h//2, x:x+w]
            roi_color = frame[y:y+h//2, x:x+w]
            
            # Detect eyes
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
            
            # Draw eye rectangles
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Simple drowsiness logic
            if len(eyes) < 2:
                eyes_closed_count += 1
                cv2.putText(frame, f"Eyes closed count: {eyes_closed_count}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                if eyes_closed_count > 60:  # About 2 seconds at 30fps
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    print("DROWSINESS ALERT!")
            else:
                eyes_closed_count = 0
                cv2.putText(frame, "Eyes open", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Simple Drowsiness Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def main():
    print("=== Drowsiness Detection System Test ===")
    
    # Test OpenCV
    if not test_basic_opencv():
        return
    
    # Test camera
    if not test_camera():
        print("Camera test failed. Please check your camera connection.")
        return
    
    print("\nAll tests passed! Starting detection...")
    input("Press Enter to continue...")
    
    # Run detection
    run_simple_detection()

if __name__ == "__main__":
    main()