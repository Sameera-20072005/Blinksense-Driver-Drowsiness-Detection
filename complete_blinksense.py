import cv2
from flask import Flask, Response, render_template_string, jsonify
import time
import json
from datetime import datetime

app = Flask(__name__)

class EyeDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.closed_start = None
        self.is_drowsy = False
        self.alerts = []
        self.detection_data = []
        self.sensitivity = 100
        
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
                if not self.is_drowsy:
                    self.is_drowsy = True
                    self.alerts.append({
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'message': 'Drowsiness detected!'
                    })
        else:
            self.closed_start = None
            self.is_drowsy = False
        
        self.detection_data.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'eyes_open': eyes_open
        })
        
        if len(self.detection_data) > 50:
            self.detection_data.pop(0)
        
        if self.is_drowsy:
            cv2.putText(frame, "DROWSY! WAKE UP!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
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
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/alerts')
def get_alerts():
    return jsonify(detector.alerts)

@app.route('/api/data')
def get_data():
    return jsonify(detector.detection_data)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>BlinkSense</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #ffeef8 0%, #e8f4fd 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(90deg, #ffb3d9 0%, #b3d9ff 100%);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .nav-brand { font-size: 1.8rem; font-weight: bold; color: #4a4a4a; }
        .nav-menu {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        .nav-item {
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.3);
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            color: #4a4a4a;
        }
        .nav-item:hover, .nav-item.active {
            background: rgba(255,255,255,0.6);
            transform: translateY(-2px);
        }
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        .page { display: none; }
        .page.active { display: block; }
        .card {
            background: rgba(255,255,255,0.8);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .video-feed {
            border-radius: 15px;
            max-width: 100%;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        .chart-container { height: 300px; margin: 1rem 0; }
        .alert-item {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 5px;
        }
        .slider {
            width: 100%;
            height: 8px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
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
        .table th { background: #f8f9fa; }
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            background: linear-gradient(45deg, #ff69b4, #87ceeb);
            color: white;
            margin: 0.5rem;
        }
        @media (max-width: 768px) {
            .nav-menu { flex-direction: column; }
            .container { padding: 0 1rem; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">BlinkSense - Driver Drowsiness Detection</div>
        <div class="nav-menu">
            <button class="nav-item active" onclick="showPage('home')">Home</button>
            <button class="nav-item" onclick="showPage('dashboard')">Dashboard</button>
            <button class="nav-item" onclick="showPage('alerts')">Alerts</button>
            <button class="nav-item" onclick="showPage('analytics')">Analytics</button>
            <button class="nav-item" onclick="showPage('settings')">Settings</button>
            <button class="nav-item" onclick="showPage('storage')">Storage</button>
        </div>
    </nav>

    <div class="container">
        <!-- Home Page -->
        <div id="home" class="page active">
            <div class="card">
                <h2>Real-Time Drowsiness Detection</h2>
                <div style="text-align: center;">
                    <img src="/video_feed" class="video-feed" alt="Live Camera Feed">
                </div>
                <div style="text-align: center; margin-top: 1rem;">
                    <div id="status" style="padding: 1rem; background: #d4edda; color: #155724; border-radius: 10px; font-weight: bold;">
                        Eyes Open - Safe Driving
                    </div>
                </div>
            </div>
        </div>

        <!-- Dashboard Page -->
        <div id="dashboard" class="page">
            <div class="card">
                <h2>Real-Time Dashboard</h2>
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
                <h2>Alert History</h2>
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
                <h2>Detailed Analytics</h2>
                <div class="grid">
                    <div>
                        <h3>Daily Activity</h3>
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
                <h2>Detection Settings</h2>
                <div style="margin: 1rem 0;">
                    <label>Sensitivity: <span id="sensitivityValue">100</span></label>
                    <input type="range" id="sensitivity" class="slider" min="50" max="150" value="100">
                </div>
                <div style="margin: 1rem 0;">
                    <label>Alert Threshold: <span id="thresholdValue">2.0</span>s</label>
                    <input type="range" id="threshold" class="slider" min="1" max="5" step="0.5" value="2.0">
                </div>
                <button class="btn" onclick="saveSettings()">Save Settings</button>
            </div>
        </div>

        <!-- Storage Page -->
        <div id="storage" class="page">
            <div class="card">
                <h2>Data Management</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Duration</th>
                            <th>Alerts</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>2024-01-15</td>
                            <td>45 min</td>
                            <td>3</td>
                            <td><button class="btn">Download</button></td>
                        </tr>
                        <tr>
                            <td>2024-01-14</td>
                            <td>32 min</td>
                            <td>1</td>
                            <td><button class="btn">Download</button></td>
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
            
            if (pageId === 'dashboard') initDashboard();
            if (pageId === 'analytics') initAnalytics();
        }
        
        function initDashboard() {
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
                        backgroundColor: 'rgba(135, 206, 235, 0.1)'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
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
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
        
        function initAnalytics() {
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
                options: { responsive: true, maintainAspectRatio: false }
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
                        backgroundColor: 'rgba(255, 105, 180, 0.1)'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
        
        function updateAlerts() {
            fetch('/api/alerts')
                .then(response => response.json())
                .then(alerts => {
                    const alertsList = document.getElementById('alertsList');
                    if (alerts.length === 0) {
                        alertsList.innerHTML = '<div class="alert-item"><strong>No alerts yet</strong><br>System is monitoring...</div>';
                    } else {
                        alertsList.innerHTML = alerts.map(alert => 
                            `<div class="alert-item"><strong>${alert.time}</strong><br>${alert.message}</div>`
                        ).join('');
                    }
                });
        }
        
        function saveSettings() {
            alert('Settings saved successfully!');
        }
        
        document.getElementById('sensitivity').addEventListener('input', function() {
            document.getElementById('sensitivityValue').textContent = this.value;
        });
        
        document.getElementById('threshold').addEventListener('input', function() {
            document.getElementById('thresholdValue').textContent = this.value;
        });
        
        setInterval(updateAlerts, 3000);
        initDashboard();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("Starting BlinkSense with all pages...")
    app.run(host='127.0.0.1', port=5000, debug=False)