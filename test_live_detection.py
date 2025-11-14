import cv2
from flask import Flask, Response
import time

app = Flask(__name__)

def generate_frames():
    print("Starting camera...")
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("Camera 0 failed, trying DirectShow...")
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not camera.isOpened():
        print("No camera available!")
        return
    
    print("Camera opened successfully!")
    
    frame_count = 0
    while True:
        success, frame = camera.read()
        if not success:
            print("Failed to read frame")
            break
        
        frame_count += 1
        
        # Add simple text overlay
        cv2.putText(frame, f"LIVE FEED - Frame {frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, time.strftime("%H:%M:%S"), (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return '''
    <html>
    <body>
        <h1>Live Detection Test</h1>
        <img src="/video_feed" width="640" height="480">
    </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Starting test server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)