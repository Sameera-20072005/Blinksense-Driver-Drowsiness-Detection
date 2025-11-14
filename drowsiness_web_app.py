import cv2
import numpy as np
from flask import Flask, render_template_string, Response, jsonify, request
import json
import time
from datetime import datetime
import threading
import queue
import winsound

app = Flask(__name__)

class EyeDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.closed_eye_start_time = None
        self.is_drowsy = False
        self.drowsy_threshold = 2.0
        self.sensitivity = 100
        self.detection_data = []
        self.alerts = []
        
    def detect_eyes(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        eyes_detected = False
        
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 182, 193), 2)
            cv2.putText(frame, "FACE", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 182, 193), 2)
            
            # Focus on upper half of face for better eye detection
            roi_gray = gray[y:y+h//2, x:x+w]
            roi_color = frame[y:y+h//2, x:x+w]
            
            # Detect eyes with better parameters
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3, minSize=(15, 15))
            
            # Always assume we can detect eye state if we have a face
            eyes_found = True
            eyes_open_count = 0
            total_eyes = max(len(eyes), 2)  # Assume 2 eyes even if we detect fewer
            
            if len(eyes) >= 2:
                # Sort eyes by x-coordinate (left to right)
                eyes = sorted(eyes, key=lambda e: e[0])[:2]  # Take only first 2
                
                for i, (ex, ey, ew, eh) in enumerate(eyes):
                    eye_roi = roi_gray[ey:ey+eh, ex:ex+ew]
                    
                    # Determine if eye is open or closed
                    eye_open = True
                    if eye_roi.size > 0:
                        # Use height-to-width ratio as primary indicator
                        aspect_ratio = eh / ew if ew > 0 else 0
                        avg_brightness = np.mean(eye_roi)
                        
                        # More sensitive detection for closed eyes
                        if aspect_ratio < 0.25 or avg_brightness < 40:
                            eye_open = False
                    
                    if eye_open:
                        eyes_open_count += 1
                    
                    # Draw eye rectangle with color based on state
                    color = (0, 255, 0) if eye_open else (0, 0, 255)
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), color, 3)
                    
                    # Add eye label
                    label = "L" if i == 0 else "R"
                    state = "OPEN" if eye_open else "CLOSED"
                    cv2.putText(roi_color, f"{label}-{state}", (ex, ey-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            elif len(eyes) == 1:
                # Only one eye detected - check its state
                ex, ey, ew, eh = eyes[0]
                eye_roi = roi_gray[ey:ey+eh, ex:ex+ew]
                
                eye_open = True
                if eye_roi.size > 0:
                    aspect_ratio = eh / ew if ew > 0 else 0
                    avg_brightness = np.mean(eye_roi)
                    if aspect_ratio < 0.25 or avg_brightness < 40:
                        eye_open = False
                
                if eye_open:
                    eyes_open_count = 1
                    # Assume both eyes are in similar state
                    total_eyes = 1
                
                color = (0, 255, 0) if eye_open else (0, 0, 255)
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), color, 3)
                state = "OPEN" if eye_open else "CLOSED"
                cv2.putText(roi_color, f"EYE-{state}", (ex, ey-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            else:
                # No eyes detected with cascade - assume closed based on face analysis
                eyes_open_count = 0
                cv2.putText(roi_color, "EYES CLOSED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Determine final eye state
            eyes_detected = eyes_open_count >= (total_eyes // 2 + 1)  # Majority of eyes must be open
        
        current_time = time.time()
        
        # Drowsiness detection logic
        if len(faces) > 0:  # Face detected
            if not eyes_detected:  # Eyes are closed
                if self.closed_eye_start_time is None:
                    self.closed_eye_start_time = current_time
                    print("👁️ EYES CLOSED - Starting drowsiness timer")
                else:
                    closed_duration = current_time - self.closed_eye_start_time
                    print(f"⏱️ Eyes closed for {closed_duration:.1f}s (threshold: {self.drowsy_threshold}s)")
                    
                    if closed_duration >= self.drowsy_threshold:
                        if not self.is_drowsy:
                            self.is_drowsy = True
                            self.add_alert("Drowsiness detected!")
                            print(f"🚨 DROWSINESS ALERT! Eyes closed for {closed_duration:.1f} seconds")
                            # Play alarm sound
                            threading.Thread(target=self.play_alarm, daemon=True).start()
            else:  # Eyes are open
                if self.closed_eye_start_time is not None:
                    print("👀 Eyes opened - resetting timer")
                self.closed_eye_start_time = None
                self.is_drowsy = False
        else:
            # No face detected - reset everything
            if self.closed_eye_start_time is not None:
                print("❌ No face detected - resetting")
            self.closed_eye_start_time = None
            self.is_drowsy = False
        
        self.detection_data.append({
            'timestamp': datetime.now().isoformat(),
            'eyes_open': eyes_detected,
            'drowsy': self.is_drowsy
        })
        
        if len(self.detection_data) > 100:
            self.detection_data.pop(0)
        
        return frame, eyes_detected  # Return true if eyes are open
    
    def add_alert(self, message):
        alert = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': message,
            'severity': 'high'
        }
        self.alerts.append(alert)
        if len(self.alerts) > 50:
            self.alerts.pop(0)
    
    def play_alarm(self):
        """Play alarm sound when drowsiness is detected"""
        try:
            # Play alarm sound file if exists, otherwise use beeps
            import os
            alarm_file = "sounds/alarm.wav"
            if os.path.exists(alarm_file):
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(alarm_file)
                pygame.mixer.music.play()
            else:
                # Fallback to system beeps
                for i in range(3):
                    winsound.Beep(1000, 400)
                    time.sleep(0.1)
        except Exception as e:
            # Final fallback to simple beeps
            try:
                for i in range(3):
                    winsound.Beep(1000, 400)
                    time.sleep(0.1)
            except:
                print(f"All alarm methods failed: {e}")

detector = EyeDetector()



def generate_frames():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        frame, eyes_open = detector.detect_eyes(frame)
        
        # Add status overlay with countdown
        if detector.is_drowsy:
            # Red overlay for drowsiness alert
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], 150), (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            
            cv2.putText(frame, "DROWSY! WAKE UP!", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(frame, "ALERT!", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        elif detector.closed_eye_start_time is not None:
            # Yellow warning with countdown when eyes are closed
            duration = time.time() - detector.closed_eye_start_time
            remaining = max(0, detector.drowsy_threshold - duration)
            cv2.putText(frame, f"EYES CLOSED: {duration:.1f}s", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, f"Alert in: {remaining:.1f}s", (50, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            # Green status when awake
            cv2.putText(frame, "EYES OPEN - SAFE", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Add live detection status
        cv2.putText(frame, "LIVE DETECTION", (frame.shape[1] - 200, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        cv2.putText(frame, timestamp, (frame.shape[1] - 100, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/detection_data')
def get_detection_data():
    return jsonify(detector.detection_data[-20:])

@app.route('/api/alerts')
def get_alerts():
    return jsonify(detector.alerts)

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        data = request.json
        detector.sensitivity = data.get('sensitivity', 100)
        detector.drowsy_threshold = data.get('threshold', 2.0)
        return jsonify({'status': 'success'})
    return jsonify({
        'sensitivity': detector.sensitivity,
        'threshold': detector.drowsy_threshold
    })

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlinkSense - Driver Drowsiness Detection</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff69b4 0%, #ffb3d9 50%, #ffc0cb 100%);
            min-height: 100vh;
        }
        
        .navbar {
            background: linear-gradient(90deg, #ff1493 0%, #ff69b4 100%);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(255,20,147,0.4);
        }
        
        .nav-brand {
            font-size: 1.8rem;
            font-weight: bold;
            color: #ffffff;
        }
        
        .nav-menu {
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .nav-item {
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            color: #ffffff;
        }
        
        .nav-item:hover, .nav-item.active {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
            color: #ffffff;
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .page {
            display: none;
            animation: fadeIn 0.5s ease-in;
        }
        
        .page.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .card {
            background: rgba(255,255,255,0.8);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .video-container {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .video-feed {
            border-radius: 15px;
            max-width: 100%;
            height: auto;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        
        .status-indicator {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            margin: 1rem;
            font-weight: bold;
        }
        
        .status-safe {
            background: #d4edda;
            color: #155724;
        }
        
        .status-drowsy {
            background: #f8d7da;
            color: #721c24;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin: 2rem 0;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .alert-item {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 5px;
        }
        
        .slider-container {
            margin: 1rem 0;
        }
        
        .slider {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }
        
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #ff69b4;
            cursor: pointer;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        .table th, .table td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .table th {
            background: #f8f9fa;
            font-weight: bold;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0.5rem;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #ff69b4, #87ceeb);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        @media (max-width: 768px) {
            .nav-menu {
                flex-wrap: wrap;
            }
            
            .container {
                padding: 0 1rem;
            }
            
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">🚗 BlinkSense</div>
        <div class="nav-menu">
            <button class="nav-item active" onclick="showPage('home')">🏠 Home</button>
            <button class="nav-item" onclick="showPage('dashboard')">📊 Dashboard</button>
            <button class="nav-item" onclick="showPage('alerts')">🚨 Alerts</button>
            <button class="nav-item" onclick="showPage('analytics')">📈 Analytics</button>
            <button class="nav-item" onclick="showPage('settings')">⚙️ Settings</button>
            <button class="nav-item" onclick="showPage('storage')">💾 Storage</button>
        </div>
    </nav>

    <div class="container">
        <!-- Home Page -->
        <div id="home" class="page active">
            <div class="card">
                <h2>🎯 Real-Time Drowsiness Detection</h2>
                <div class="video-container">
                    <img src="/video_feed" class="video-feed" alt="Live Camera Feed">
                </div>
                <div style="text-align: center;">
                    <div id="status" class="status-indicator status-safe">👁️ Eyes Open - Safe Driving</div>
                </div>
            </div>
        </div>

        <!-- Dashboard Page -->
        <div id="dashboard" class="page">
            <div class="card">
                <h2>📊 Real-Time Dashboard</h2>
                <div class="grid">
                    <div>
                        <h3>Eye State Timeline</h3>
                        <div class="chart-container">
                            <canvas id="eyeChart"></canvas>
                        </div>
                    </div>
                    <div>
                        <h3>Detection Statistics</h3>
                        <div class="chart-container">
                            <canvas id="statsChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alerts Page -->
        <div id="alerts" class="page">
            <div class="card">
                <h2>🚨 Alert History</h2>
                <div id="alertsList">
                    <div class="alert-item">
                        <strong>No alerts yet</strong><br>
                        System is monitoring for drowsiness...
                    </div>
                </div>
            </div>
        </div>

        <!-- Analytics Page -->
        <div id="analytics" class="page">
            <div class="card">
                <h2>📈 Detailed Analytics</h2>
                <div class="grid">
                    <div>
                        <h3>Daily Eye Activity</h3>
                        <div class="chart-container">
                            <canvas id="dailyChart"></canvas>
                        </div>
                    </div>
                    <div>
                        <h3>Drowsiness Patterns</h3>
                        <div class="chart-container">
                            <canvas id="patternChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Settings Page -->
        <div id="settings" class="page">
            <div class="card">
                <h2>⚙️ Detection Settings</h2>
                <div class="slider-container">
                    <label for="sensitivity">Eye Detection Sensitivity: <span id="sensitivityValue">100</span></label>
                    <input type="range" id="sensitivity" class="slider" min="50" max="150" value="100">
                </div>
                <div class="slider-container">
                    <label for="threshold">Drowsiness Threshold (seconds): <span id="thresholdValue">2.0</span></label>
                    <input type="range" id="threshold" class="slider" min="1" max="5" step="0.5" value="2.0">
                </div>
                <button class="btn btn-primary" onclick="saveSettings()">💾 Save Settings</button>
            </div>
        </div>

        <!-- Storage Page -->
        <div id="storage" class="page">
            <div class="card">
                <h2>💾 Data Management</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Session Duration</th>
                            <th>Alerts Count</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>2024-01-15</td>
                            <td>45 minutes</td>
                            <td>3 alerts</td>
                            <td><button class="btn btn-primary">📥 Download</button></td>
                        </tr>
                        <tr>
                            <td>2024-01-14</td>
                            <td>32 minutes</td>
                            <td>1 alert</td>
                            <td><button class="btn btn-primary">📥 Download</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let eyeChart, statsChart, dailyChart, patternChart;
        
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            
            document.getElementById(pageId).classList.add('active');
            event.target.classList.add('active');
            
            if (pageId === 'dashboard') {
                initDashboardCharts();
            } else if (pageId === 'analytics') {
                initAnalyticsCharts();
            }
        }
        
        function initDashboardCharts() {
            if (eyeChart) eyeChart.destroy();
            if (statsChart) statsChart.destroy();
            
            const ctx1 = document.getElementById('eyeChart').getContext('2d');
            eyeChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Eyes Open',
                        data: [],
                        borderColor: '#87ceeb',
                        backgroundColor: 'rgba(135, 206, 235, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1
                        }
                    }
                }
            });
            
            const ctx2 = document.getElementById('statsChart').getContext('2d');
            statsChart = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: ['Eyes Open', 'Eyes Closed'],
                    datasets: [{
                        data: [85, 15],
                        backgroundColor: ['#87ceeb', '#ffb3d9']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        function initAnalyticsCharts() {
            if (dailyChart) dailyChart.destroy();
            if (patternChart) patternChart.destroy();
            
            const ctx3 = document.getElementById('dailyChart').getContext('2d');
            dailyChart = new Chart(ctx3, {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Driving Hours',
                        data: [2, 3, 1, 4, 2, 5, 3],
                        backgroundColor: '#ffb3d9'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            
            const ctx4 = document.getElementById('patternChart').getContext('2d');
            patternChart = new Chart(ctx4, {
                type: 'line',
                data: {
                    labels: ['6AM', '9AM', '12PM', '3PM', '6PM', '9PM'],
                    datasets: [{
                        label: 'Drowsiness Events',
                        data: [1, 0, 2, 3, 1, 0],
                        borderColor: '#ff69b4',
                        backgroundColor: 'rgba(255, 105, 180, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        function updateStatus() {
            fetch('/api/detection_data')
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        const latest = data[data.length - 1];
                        const statusEl = document.getElementById('status');
                        
                        if (latest.drowsy) {
                            statusEl.className = 'status-indicator status-drowsy';
                            statusEl.textContent = '😴 DROWSY - WAKE UP!';
                        } else if (latest.eyes_open) {
                            statusEl.className = 'status-indicator status-safe';
                            statusEl.textContent = '👁️ Eyes Open - Safe Driving';
                        } else {
                            statusEl.className = 'status-indicator status-safe';
                            statusEl.textContent = '👀 Monitoring...';
                        }
                        
                        if (eyeChart && eyeChart.data) {
                            const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
                            const values = data.map(d => d.eyes_open ? 1 : 0);
                            
                            eyeChart.data.labels = labels;
                            eyeChart.data.datasets[0].data = values;
                            eyeChart.update('none');
                        }
                    }
                });
        }
        
        function updateAlerts() {
            fetch('/api/alerts')
                .then(response => response.json())
                .then(alerts => {
                    const alertsList = document.getElementById('alertsList');
                    if (alerts.length === 0) {
                        alertsList.innerHTML = '<div class="alert-item"><strong>No alerts yet</strong><br>System is monitoring for drowsiness...</div>';
                    } else {
                        alertsList.innerHTML = alerts.map(alert => 
                            `<div class="alert-item">
                                <strong>${alert.timestamp}</strong><br>
                                ${alert.message}
                            </div>`
                        ).join('');
                    }
                });
        }
        
        function saveSettings() {
            const sensitivity = document.getElementById('sensitivity').value;
            const threshold = document.getElementById('threshold').value;
            
            fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sensitivity: parseInt(sensitivity),
                    threshold: parseFloat(threshold)
                })
            })
            .then(response => response.json())
            .then(data => {
                alert('Settings saved successfully!');
            });
        }
        
        document.getElementById('sensitivity').addEventListener('input', function() {
            document.getElementById('sensitivityValue').textContent = this.value;
        });
        
        document.getElementById('threshold').addEventListener('input', function() {
            document.getElementById('thresholdValue').textContent = this.value;
        });
        
        setInterval(updateStatus, 1000);
        setInterval(updateAlerts, 5000);
        
        initDashboardCharts();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)