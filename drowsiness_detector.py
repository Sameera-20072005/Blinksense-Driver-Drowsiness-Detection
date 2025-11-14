import cv2
import dlib
import numpy as np
from imutils import face_utils
from imutils.video import VideoStream
from threading import Thread
import playsound
import time
from .utils import eye_aspect_ratio, draw_eye_landmarks, display_info

class DrowsinessDetector:
    def __init__(self, 
                 shape_predictor_path="data/models/shape_predictor_68_face_landmarks.dat",
                 alarm_path="data/sounds/alarm.wav",
                 ear_thresh=0.25,
                 ear_consec_frames=20):
        """
        Initialize the Drowsiness Detector
        
        Args:
            shape_predictor_path: Path to dlib's facial landmark predictor
            alarm_path: Path to alarm sound file
            ear_thresh: Eye aspect ratio threshold for closed eyes
            ear_consec_frames: Number of consecutive frames for drowsiness alert
        """
        self.shape_predictor_path = shape_predictor_path
        self.alarm_path = alarm_path
        self.EYE_AR_THRESH = ear_thresh
        self.EYE_AR_CONSEC_FRAMES = ear_consec_frames
        
        # Initialize counters
        self.COUNTER = 0
        self.ALARM_ON = False
        
        # Initialize dlib's face detector and facial landmark predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.shape_predictor_path)
        
        # Get facial landmarks indexes for left and right eye
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        
        print("[INFO] Drowsiness detector initialized successfully!")
    
    def sound_alarm(self):
        """Play alarm sound in a separate thread"""
        try:
            playsound.playsound(self.alarm_path)
        except Exception as e:
            print(f"[ERROR] Could not play alarm: {e}")
    
    def detect_drowsiness(self, frame):
        """
        Process a single frame for drowsiness detection
        
        Args:
            frame: Input video frame
            
        Returns:
            processed_frame: Frame with annotations
            ear: Current eye aspect ratio
            is_drowsy: Boolean indicating drowsiness state
        """
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the grayscale frame
        rects = self.detector(gray, 0)
        
        ear = 0.0
        is_drowsy = False
        
        # Process each detected face
        for rect in rects:
            # Get facial landmarks
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            
            # Extract left and right eye coordinates
            leftEye = shape[self.lStart:self.lEnd]
            rightEye = shape[self.rStart:self.rEnd]
            
            # Calculate eye aspect ratio for both eyes
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            
            # Average the eye aspect ratio for both eyes
            ear = (leftEAR + rightEAR) / 2.0
            
            # Draw eye landmarks
            draw_eye_landmarks(frame, leftEye)
            draw_eye_landmarks(frame, rightEye)
            
            # Check if EAR is below threshold
            if ear < self.EYE_AR_THRESH:
                self.COUNTER += 1
                
                # Check if eyes have been closed for sufficient time
                if self.COUNTER >= self.EYE_AR_CONSEC_FRAMES:
                    if not self.ALARM_ON:
                        self.ALARM_ON = True
                        is_drowsy = True
                        
                        # Start alarm in separate thread
                        if self.alarm_path:
                            alarm_thread = Thread(target=self.sound_alarm)
                            alarm_thread.daemon = True
                            alarm_thread.start()
            else:
                # Reset counter and alarm if eyes are open
                self.COUNTER = 0
                self.ALARM_ON = False
        
        # Display information on frame
        display_info(frame, ear, self.COUNTER, self.ALARM_ON)
        
        return frame, ear, is_drowsy
    
    def run_detection(self, source=0):
        """
        Run real-time drowsiness detection
        
        Args:
            source: Video source (0 for webcam, or path to video file)
        """
        print("[INFO] Starting video stream...")
        vs = VideoStream(src=source).start()
        time.sleep(2.0)  # Allow camera to warm up
        
        try:
            while True:
                # Read frame from video stream
                frame = vs.read()
                if frame is None:
                    break
                
                # Resize frame for better performance
                frame = cv2.resize(frame, (640, 480))
                
                # Process frame for drowsiness detection
                processed_frame, ear, is_drowsy = self.detect_drowsiness(frame)
                
                # Display the frame
                cv2.imshow("Drowsiness Detection", processed_frame)
                
                # Log drowsiness events
                if is_drowsy:
                    print(f"[ALERT] Drowsiness detected! EAR: {ear:.2f}")
                
                # Break on 'q' key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n[INFO] Detection stopped by user")
        
        finally:
            # Cleanup
            cv2.destroyAllWindows()
            vs.stop()
            print("[INFO] Cleanup completed")
