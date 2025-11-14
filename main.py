import argparse
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

try:
    from drowsiness_detector_mediapipe import DrowsinessDetectorMediaPipe
    USE_MEDIAPIPE = True
except ImportError:
    USE_MEDIAPIPE = False
    print("MediaPipe not available, trying dlib...")
    try:
        from drowsiness_detector import DrowsinessDetector
        USE_DLIB = True
    except ImportError:
        USE_DLIB = False
        print("dlib not available, using simple OpenCV detector...")
        try:
            from improved_detector import ImprovedDrowsinessDetector
            USE_IMPROVED = True
            USE_SIMPLE = False
        except ImportError:
            try:
                from simple_detector import SimpleDrowsinessDetector
                USE_SIMPLE = True
                USE_IMPROVED = False
            except ImportError:
                print("No detector available!")
                sys.exit(1)

def main():
    ap = argparse.ArgumentParser(description="Real-time Drowsiness Detection System")
    ap.add_argument("-w", "--webcam", type=int, default=0, help="Webcam index")
    ap.add_argument("-t", "--threshold", type=float, default=0.25, help="EAR threshold")
    ap.add_argument("-f", "--frames", type=int, default=20, help="Frame threshold")
    ap.add_argument("-a", "--alarm", type=str, default="data/sounds/alarm.wav", help="Alarm sound path")
    
    args = vars(ap.parse_args())
    
    try:
        if USE_MEDIAPIPE:
            print("[INFO] Using MediaPipe-based detection")
            detector = DrowsinessDetectorMediaPipe(
                alarm_path=args["alarm"],
                ear_thresh=args["threshold"],
                ear_consec_frames=args["frames"]
            )
        elif 'USE_DLIB' in locals() and USE_DLIB:
            print("[INFO] Using dlib-based detection")
            detector = DrowsinessDetector(
                shape_predictor_path="data/models/shape_predictor_68_face_landmarks.dat",
                alarm_path=args["alarm"],
                ear_thresh=args["threshold"],
                ear_consec_frames=args["frames"]
            )
        elif USE_IMPROVED:
            print("[INFO] Using improved time-based detection")
            detector = ImprovedDrowsinessDetector(
                closed_eye_time_thresh=2.0,  # 2 seconds
                ear_thresh=0.15  # Lower threshold for better detection
            )
        elif USE_SIMPLE:
            print("[INFO] Using simple OpenCV-based detection")
            detector = SimpleDrowsinessDetector(
                ear_thresh=args["threshold"],
                ear_consec_frames=args["frames"]
            )
        else:
            print("[ERROR] No detector available")
            sys.exit(1)
        
        print(f"[INFO] Using video source: {args['webcam']}")
        print("[INFO] Press 'q' to quit the detection")
        
        detector.run_detection(args["webcam"])
        
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
