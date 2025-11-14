import cv2
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from improved_detector import ImprovedDrowsinessDetector

def test_camera_access():
    """Test different camera indices to find working camera"""
    print("Testing camera access...")
    
    for i in range(5):  # Test camera indices 0-4
        print(f"Testing camera index {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Camera {i} is working!")
                cap.release()
                return i
            else:
                print(f"✗ Camera {i} opened but can't read frames")
        else:
            print(f"✗ Camera {i} failed to open")
        
        cap.release()
    
    print("No working camera found!")
    return None

def main():
    print("=== Drowsiness Detection Test ===")
    
    # Test camera access
    camera_index = test_camera_access()
    
    if camera_index is None:
        print("\n[ERROR] No camera available!")
        print("Make sure:")
        print("1. Your camera is connected")
        print("2. No other application is using the camera")
        print("3. Camera drivers are installed")
        return
    
    print(f"\n[INFO] Using camera {camera_index}")
    print("[INFO] The system will:")
    print("- Detect your face and eyes")
    print("- Monitor if eyes are closed")
    print("- Alert if eyes closed for 2+ seconds")
    print("- Press 'q' to quit, 'r' to reset alarm")
    
    input("\nPress Enter to start detection...")
    
    # Initialize detector
    detector = ImprovedDrowsinessDetector(
        closed_eye_time_thresh=2.0,  # 2 seconds
        ear_thresh=0.15  # Threshold for closed eyes
    )
    
    # Run detection
    detector.run_detection(camera_index)

if __name__ == "__main__":
    main()