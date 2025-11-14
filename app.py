from flask import Flask, render_template, jsonify, request
import json
import datetime
import os

app = Flask(__name__)

# Sample data for demonstration
alerts_data = [
    {"time": "2024-01-15 14:30:25", "duration": "3.2s", "severity": "High"},
    {"time": "2024-01-15 12:15:10", "duration": "2.8s", "severity": "Medium"},
    {"time": "2024-01-14 16:45:33", "duration": "4.1s", "severity": "High"}
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    stats = {
        "total_alerts": len(alerts_data),
        "today_alerts": 2,
        "avg_response_time": "1.2s",
        "system_status": "Active"
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/alerts')
def alerts():
    return render_template('alerts.html', alerts=alerts_data)

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/storage')
def storage():
    return render_template('storage.html')

@app.route('/api/start_detection')
def start_detection():
    return jsonify({"status": "Detection started", "message": "Camera activated"})

@app.route('/api/stop_detection')
def stop_detection():
    return jsonify({"status": "Detection stopped", "message": "Camera deactivated"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)