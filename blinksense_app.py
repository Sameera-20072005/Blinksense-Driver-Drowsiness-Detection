import cv2
import numpy as np
from flask import Flask, Response, render_template_string
import time

app = Flask(__name__)

class EyeDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.closed_start = None
        self.is_drowsy = False
        
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
        
        if not eyes_open:
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
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
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
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #ffeef8 0%, #e8f4fd 100%);
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255,255,255,0.9);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            color: #ff69b4;
            margin-bottom: 30px;
        }
        .video-feed {
            border-radius: 15px;
            max-width: 100%;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 18px;
        }
        .instructions {
            margin-top: 20px;
            color: #666;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>BlinkSense - Driver Drowsiness Detection</h1>
        <img src="/video_feed" class="video-feed" alt="Live Camera Feed">
        <div class="status">
            Monitoring your eyes for drowsiness...
        </div>
        <div class="instructions">
            <p><strong>How it works:</strong></p>
            <p>The system monitors your eyes in real-time</p>
            <p>If you close your eyes for more than 2 seconds, it will alert you</p>
            <p>Keep your face visible to the camera for best results</p>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Starting BlinkSense...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)