import cv2
import numpy as np
from flask import Flask, Response, render_template_string, jsonify
import time
import threading

app = Flask(__name__)

class EyeDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.closed_start = None
        self.is_drowsy = False
        self.camera = None
        self.camera_active = False
        
    def start_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_active = True
        return self.camera.isOpened()
        
    def detect_drowsiness(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        eyes_open = False
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 182, 193), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                eyes_open = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (173, 216, 230), 2)
        
        current_time = time.time()
        
        if not eyes_open and len(faces) > 0:
            if self.closed_start is None:
                self.closed_start = current_time
            elif current_time - self.closed_start >= 2.0:
                self.is_drowsy = True
        else:
            self.closed_start = None
            self.is_drowsy = False
        
        if self.is_drowsy:
            cv2.putText(frame, "DROWSY! WAKE UP!", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
        return frame

detector = EyeDetector()

def generate_frames():
    if not detector.start_camera():
        return
        
    while detector.camera_active:
        success, frame = detector.camera.read()
        if not success:
            break
        
        frame = detector.detect_drowsiness(frame)
        
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
    <title>BlinkSense - Driver Drowsiness Detection</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ffeef8 0%, #e8f4fd 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .navbar {
            background: linear-gradient(90deg, #ffb3d9 0%, #b3d9ff 100%);
            padding: 1rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .nav-brand {
            font-size: 1.8rem;
            font-weight: bold;
            color: #4a4a4a;
            text-align: center;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255,255,255,0.9);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .video-container {
            margin: 2rem 0;
            position: relative;
        }
        
        .video-feed {
            border-radius: 15px;
            max-width: 100%;
            height: auto;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        
        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 18px;
            background: #d4edda;
            color: #155724;
        }
        
        .controls {
            margin: 20px 0;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #ff69b4, #87ceeb);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .instructions {
            margin-top: 20px;
            color: #666;
            line-height: 1.6;
            text-align: left;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .feature-card {
            background: rgba(255,255,255,0.7);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            .feature-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">🚗 BlinkSense - Driver Drowsiness Detection</div>
    </nav>

    <div class="container">
        <h2>Real-Time Eye Monitoring System</h2>
        
        <div class="video-container">
            <img src="/video_feed" class="video-feed" alt="Live Camera Feed" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjQ4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkNhbWVyYSBOb3QgQWNjZXNzaWJsZTwvdGV4dD48L3N2Zz4=';">
        </div>
        
        <div class="status" id="status">
            📹 Camera Loading... Please allow camera access when prompted
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="location.reload()">🔄 Restart Detection</button>
            <button class="btn btn-primary" onclick="testCamera()">📷 Test Camera</button>
        </div>
        
        <div class="feature-grid">
            <div class="feature-card">
                <h3>👁️ Eye Detection</h3>
                <p>Advanced computer vision algorithms detect your eyes in real-time using facial recognition technology.</p>
            </div>
            
            <div class="feature-card">
                <h3>⏱️ 2-Second Alert</h3>
                <p>System triggers an alert when eyes are closed for more than 2 seconds, indicating potential drowsiness.</p>
            </div>
            
            <div class="feature-card">
                <h3>🎨 Responsive Design</h3>
                <p>Beautiful pastel interface that works perfectly on desktop, tablet, and mobile devices.</p>
            </div>
            
            <div class="feature-card">
                <h3>🔧 Easy Setup</h3>
                <p>No complex configuration required. Just allow camera access and start monitoring immediately.</p>
            </div>
        </div>
        
        <div class="instructions">
            <h3>📋 Instructions:</h3>
            <ul>
                <li><strong>Camera Access:</strong> Allow camera permissions when prompted by your browser</li>
                <li><strong>Positioning:</strong> Keep your face visible and well-lit for best detection</li>
                <li><strong>Detection:</strong> Pink rectangles show face detection, blue rectangles show eye detection</li>
                <li><strong>Alert:</strong> Red "DROWSY! WAKE UP!" message appears when eyes close for 2+ seconds</li>
                <li><strong>Troubleshooting:</strong> If camera doesn't work, try the "Test Camera" button or refresh the page</li>
            </ul>
        </div>
    </div>

    <script>
        function testCamera() {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(stream) {
                    alert('Camera access successful! The detection should work now.');
                    stream.getTracks().forEach(track => track.stop());
                    location.reload();
                })
                .catch(function(err) {
                    alert('Camera access denied or not available. Please check your camera settings and permissions.');
                });
        }
        
        // Auto-update status
        setInterval(function() {
            const img = document.querySelector('.video-feed');
            const status = document.getElementById('status');
            
            if (img.complete && img.naturalWidth > 0) {
                status.innerHTML = '👁️ Monitoring Active - Eyes being tracked for drowsiness';
                status.style.background = '#d4edda';
                status.style.color = '#155724';
            } else {
                status.innerHTML = '⚠️ Camera not accessible - Please allow camera permissions';
                status.style.background = '#f8d7da';
                status.style.color = '#721c24';
            }
        }, 2000);
    </script>
</body>
</html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_status')
def camera_status():
    return jsonify({'camera_active': detector.camera_active})

if __name__ == '__main__':
    print("Starting BlinkSense...")
    print("Open your browser and go to: http://localhost:5000")
    print("Make sure to allow camera access when prompted!")
    app.run(debug=False, host='0.0.0.0', port=5000)