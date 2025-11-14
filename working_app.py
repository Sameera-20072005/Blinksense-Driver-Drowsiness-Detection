import cv2
import time
from flask import Flask, Response, render_template_string

app = Flask(__name__)

# Global variables
camera = None
closed_start = None

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    return camera

def generate_frames():
    global closed_start
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    while True:
        cam = get_camera()
        success, frame = cam.read()
        if not success:
            break
            
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        eyes_open = False
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 182, 193), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            eyes = eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                eyes_open = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (173, 216, 230), 2)
        
        current_time = time.time()
        
        if not eyes_open and len(faces) > 0:
            if closed_start is None:
                closed_start = current_time
            elif current_time - closed_start >= 2.0:
                cv2.putText(frame, "DROWSY! WAKE UP!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        else:
            closed_start = None
        
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>BlinkSense - Driver Drowsiness Detection</title>
    <style>
        body { 
            background: linear-gradient(135deg, #ffeef8, #e8f4fd);
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255,255,255,0.9);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #ff69b4; 
            margin-bottom: 20px;
        }
        .video-feed { 
            border-radius: 15px; 
            max-width: 100%; 
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        .status {
            margin: 20px 0;
            padding: 15px;
            background: #d4edda;
            color: #155724;
            border-radius: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>BlinkSense - Driver Drowsiness Detection</h1>
        <img src="/video_feed" class="video-feed" alt="Camera Feed">
        <div class="status">
            System Active: Monitoring eyes for drowsiness detection
        </div>
        <p><strong>Features:</strong> Real-time eye tracking | 2-second alert system | Simple UI</p>
    </div>
</body>
</html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("BlinkSense starting on http://localhost:5000")
    print("Make sure your camera is connected!")
    app.run(host='127.0.0.1', port=5000, debug=False)