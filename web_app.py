from flask import Flask, render_template, jsonify
import subprocess
import threading
import time
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variables to track detection state
detection_process = None
detection_active = False
alert_count = 0
current_ear = 0.0
last_alert_time = None

@app.route('/')
def index():
    return render_template('web_interface.html')

@app.route('/api/start_detection')
def start_detection():
    global detection_process, detection_active
    
    if not detection_active:
        try:
            # Start the detection script
            detection_process = subprocess.Popen(['python', 'live_detector.py'], 
                                               cwd=os.getcwd(),
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
            detection_active = True
            return jsonify({"status": "success", "message": "Detection started"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "already_running", "message": "Detection already active"})

@app.route('/api/stop_detection')
def stop_detection():
    global detection_process, detection_active
    
    if detection_active and detection_process:
        detection_process.terminate()
        detection_active = False
        return jsonify({"status": "success", "message": "Detection stopped"})
    else:
        return jsonify({"status": "not_running", "message": "Detection not active"})

@app.route('/api/status')
def get_status():
    global alert_count, current_ear, last_alert_time, detection_active
    
    # Simulate real-time data (in real implementation, this would read from detection output)
    if detection_active:
        import random
        current_ear = round(random.uniform(0.15, 0.35), 3)
        if current_ear < 0.2:
            alert_count += 1
            last_alert_time = time.strftime("%H:%M:%S")
    
    return jsonify({
        "detection_active": detection_active,
        "alert_count": alert_count,
        "current_ear": current_ear,
        "last_alert_time": last_alert_time,
        "system_status": "Active" if detection_active else "Standby"
    })

if __name__ == '__main__':
    print("Starting BlinkSense Web Server...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, port=5000, host='127.0.0.1')