from flask import Flask, render_template_string, Response
import cv2
import time
import winsound
import threading

app = Flask(__name__)

class BlinkSenseDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.closed_start = None
        self.is_drowsy = False
        self.alert_active = False
        
    def play_alarm(self):
        if not self.alert_active:
            self.alert_active = True
            def alarm_thread():
                for _ in range(3):  # Play 3 beeps
                    winsound.Beep(1000, 300)  # 1000Hz for 300ms
                    time.sleep(0.2)
                self.alert_active = False
            threading.Thread(target=alarm_thread, daemon=True).start()
    
    def detect_drowsiness(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        eyes_open = False
        current_time = time.time()
        
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 182, 193), 2)
            
            # Eye detection region
            roi_gray = gray[y:y+h//2, x:x+w]  # Upper half of face
            roi_color = frame[y:y+h//2, x:x+w]
            
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
            
            if len(eyes) >= 2:
                eyes_open = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (173, 216, 230), 2)
        
        # Drowsiness logic
        if not eyes_open and len(faces) > 0:
            if self.closed_start is None:
                self.closed_start = current_time
            elif current_time - self.closed_start >= 3.0:  # 3 seconds
                if not self.is_drowsy:
                    self.is_drowsy = True
                    self.play_alarm()  # Play alarm sound
                    print("DROWSINESS ALERT TRIGGERED!")
        else:
            self.closed_start = None
            self.is_drowsy = False
        
        # Add status text
        if len(faces) == 0:
            cv2.putText(frame, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        elif self.is_drowsy:
            cv2.putText(frame, "DROWSY! WAKE UP!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv2.putText(frame, "ALERT!", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        elif eyes_open:
            cv2.putText(frame, "Eyes Open - Safe", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Eyes Closed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Show closure duration
        if self.closed_start:
            duration = current_time - self.closed_start
            cv2.putText(frame, f"Closed: {duration:.1f}s", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return frame

detector = BlinkSenseDetector()

def generate_frames():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Process frame for drowsiness detection
        frame = detector.detect_drowsiness(frame)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>BlinkSense - Advanced Drowsiness Detection</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ffeef8, #e8f4fd);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #ff69b4;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }
        .video-container {
            text-align: center;
            margin-bottom: 30px;
            position: relative;
        }
        .video-feed {
            border-radius: 15px;
            max-width: 100%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 3px solid #ff69b4;
        }
        .status-bar {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        .status-card {
            background: linear-gradient(45deg, #ff69b4, #87ceeb);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            min-width: 200px;
            margin: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .status-card h3 {
            margin: 0 0 10px 0;
            font-size: 1.2rem;
        }
        .status-card p {
            margin: 0;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .features {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
        }
        .features h3 {
            color: #333;
            margin-bottom: 15px;
        }
        .features ul {
            list-style: none;
            padding: 0;
        }
        .features li {
            padding: 8px 0;
            color: #555;
        }
        .features li:before {
            content: "✓ ";
            color: #28a745;
            font-weight: bold;
            margin-right: 10px;
        }
        .alert-info {
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        .live-indicator {
            position: absolute;
            top: 15px;
            right: 15px;
            background: #ff4757;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>BlinkSense - Advanced Driver Drowsiness Detection</h1>
        
        <div class="alert-info">
            <h3>🚨 REAL-TIME MONITORING ACTIVE 🚨</h3>
            <p>System will alert you if eyes remain closed for more than 3 seconds</p>
        </div>
        
        <div class="video-container">
            <div class="live-indicator">🔴 LIVE</div>
            <img src="/video_feed" class="video-feed" alt="Live Camera Feed">
        </div>
        
        <div class="status-bar">
            <div class="status-card">
                <h3>🎯 Detection Status</h3>
                <p>ACTIVE</p>
            </div>
            <div class="status-card">
                <h3>⏱️ Alert Threshold</h3>
                <p>3 Seconds</p>
            </div>
            <div class="status-card">
                <h3>🔊 Audio Alerts</h3>
                <p>ENABLED</p>
            </div>
            <div class="status-card">
                <h3>👁️ Eye Tracking</h3>
                <p>REAL-TIME</p>
            </div>
        </div>
        
        <div class="features">
            <h3>🌟 Advanced Features:</h3>
            <ul>
                <li>Real-time face and eye detection using OpenCV</li>
                <li>Precise drowsiness detection with 3-second threshold</li>
                <li>Multi-tone audio alarm system</li>
                <li>Live video feed with detection overlays</li>
                <li>Mirror effect for natural user experience</li>
                <li>Automatic face tracking and eye state monitoring</li>
                <li>Visual alerts with colored rectangles</li>
                <li>Continuous monitoring with status updates</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p><strong>Privacy Protected:</strong> All processing happens locally on your device</p>
            <p><strong>Safety First:</strong> This system assists but does not replace proper rest</p>
        </div>
    </div>
    
    <script>
        // Add some interactivity
        setInterval(() => {
            const cards = document.querySelectorAll('.status-card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        card.style.transform = 'scale(1)';
                    }, 200);
                }, index * 100);
            });
        }, 5000);
    </script>
</body>
</html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("BlinkSense Advanced Drowsiness Detection System")
    print("=" * 50)
    print("Real-time face detection: ENABLED")
    print("Eye tracking: ENABLED") 
    print("Audio alerts: ENABLED")
    print("3-second threshold: CONFIGURED")
    print("=" * 50)
    print("Starting web server on http://localhost:5000")
    print("Make sure your camera is connected!")
    print("Close your eyes for 3+ seconds to test the alert")
    
    app.run(host='127.0.0.1', port=5000, debug=False)