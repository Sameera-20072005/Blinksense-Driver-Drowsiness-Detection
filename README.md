# BlinkSense - Advanced Driver Drowsiness Detection System

A comprehensive real-time drowsiness detection system using computer vision and machine learning with a modern React frontend dashboard.

## 🎯 Features

### Real-time Detection
- **Eye Aspect Ratio (EAR) Analysis** - Precise eye state monitoring using MediaPipe
- **2-Second Alert Threshold** - Configurable drowsiness detection timing
- **Live WebSocket Streaming** - Real-time data transmission to frontend
- **Audio & Visual Alerts** - Multi-modal alert system

### Frontend Dashboard
- **Home Page** - Live camera feed with real-time EAR display
- **Dashboard** - Session statistics and alert summaries
- **Analytics** - Detailed charts and drowsiness patterns
- **Storage** - Data export (JSON/CSV) and session management
- **Alerts** - Frontend-only alert history with localStorage
- **Settings** - Configurable thresholds and preferences

### Privacy & Security
- **No Database Storage** - Alerts stored only in browser localStorage
- **Local Processing** - Camera feed processed locally
- **No Data Upload** - Complete privacy protection
- **Offline Capable** - Works without internet connection

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Webcam/Camera
- Modern web browser

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd drowsy-driver-detection
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Docker Setup (Alternative)
```bash
docker-compose up --build
```

## 🔧 Configuration

### Detection Settings
- **EAR Threshold**: 0.15 - 0.35 (default: 0.25)
- **Closure Duration**: 1-10 seconds (default: 3s)
- **Detection Sensitivity**: 10-100% (default: 50%)

### Alert Settings
- **Audio Alerts**: Enable/disable sound notifications
- **Browser Notifications**: Desktop notification support
- **Visual Alerts**: Customizable alert overlays

## 📊 How It Works

### Eye Aspect Ratio (EAR) Calculation
```
EAR = (|p2 - p6| + |p3 - p5|) / (2 * |p1 - p4|)
```

Where p1-p6 are facial landmark points around the eye.

### Detection Logic
1. **Face Detection** - MediaPipe identifies facial landmarks
2. **Eye Tracking** - Extract eye landmark coordinates
3. **EAR Calculation** - Compute eye aspect ratio for both eyes
4. **Drowsiness Detection** - Monitor EAR below threshold for 3+ seconds
5. **Alert Trigger** - Generate frontend alert with audio/visual cues

### Frontend Alert Storage
```javascript
{
  "id": 1642123456789,
  "timestamp": "2024-01-15T18:05:00.000Z",
  "type": "Drowsiness",
  "message": "Eyes closed for more than 3 seconds",
  "duration": "3.2s",
  "severity": "high"
}
```

## 🏗️ Architecture

### Backend (FastAPI)
- **WebSocket Endpoint** - Real-time data streaming
- **MediaPipe Integration** - Advanced facial landmark detection
- **OpenCV Processing** - Camera feed handling
- **No Alert Storage** - Stateless alert generation

### Frontend (React + Vite)
- **Context API** - Global state management
- **localStorage** - Client-side alert persistence
- **Recharts** - Data visualization
- **Tailwind CSS** - Modern UI styling
- **React Router** - Multi-page navigation

## 📱 Pages Overview

### Home Page
- Live camera feed display
- Real-time EAR monitoring
- Instant drowsiness alerts
- Connection status indicator

### Dashboard
- Session statistics cards
- Alert frequency charts
- Recent activity timeline
- Performance metrics

### Analytics
- EAR trend analysis
- Blink pattern visualization
- Daily/hourly alert distribution
- PERCLOS calculations

### Storage
- Session data export (JSON/CSV)
- Local storage management
- Privacy information
- Data usage statistics

### Alerts
- Complete alert history
- Severity-based filtering
- Manual alert clearing
- Alert statistics

### Settings
- Detection threshold adjustment
- Audio alert configuration
- Camera source selection
- Privacy controls

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Manual Testing
1. **Camera Test** - Verify camera access and feed quality
2. **Detection Test** - Close eyes for 3+ seconds to trigger alert
3. **Alert Storage** - Check localStorage for alert persistence
4. **Export Test** - Verify JSON/CSV export functionality

## 🔒 Privacy & Security

### Data Handling
- **No Server Storage** - Alerts never leave your browser
- **Local Processing** - All detection happens on your device
- **No Tracking** - No analytics or user tracking
- **Secure by Design** - Privacy-first architecture

### Browser Permissions
- **Camera Access** - Required for drowsiness detection
- **Notification Permission** - Optional for desktop alerts
- **Local Storage** - Used for settings and alert history

## 🛠️ Development

### Project Structure
```
drowsy-driver-detection/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Backend container
├── frontend/
│   ├── src/
│   │   ├── pages/          # React page components
│   │   ├── App.jsx         # Main application
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile         # Frontend container
├── docker-compose.yml      # Multi-container setup
└── README.md              # This file
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| WebSocket | `/ws` | Real-time detection data stream |
| POST | `/api/start` | Start detection session |
| GET | `/api/metrics` | Get session metrics |

**Note**: No `/api/alerts` endpoints - alerts are frontend-only!

## 🚨 Troubleshooting

### Common Issues

**Camera Not Working**
- Check camera permissions in browser
- Ensure no other applications are using the camera
- Try different camera indices in settings

**WebSocket Connection Failed**
- Verify backend is running on port 8000
- Check firewall settings
- Ensure CORS is properly configured

**Alerts Not Saving**
- Check browser localStorage is enabled
- Verify sufficient storage space
- Clear browser cache if needed

**Detection Not Accurate**
- Adjust EAR threshold in settings
- Ensure good lighting conditions
- Position face clearly in camera view

## 📈 Performance Optimization

### Backend Optimization
- **Frame Rate Control** - Adjustable processing FPS
- **Efficient Landmark Detection** - Optimized MediaPipe settings
- **Memory Management** - Proper resource cleanup

### Frontend Optimization
- **Lazy Loading** - Components loaded on demand
- **Efficient Re-renders** - Optimized React state updates
- **Chart Performance** - Recharts with data limiting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **MediaPipe** - Google's ML framework for facial landmarks
- **OpenCV** - Computer vision library
- **React** - Frontend framework
- **FastAPI** - Modern Python web framework
- **Tailwind CSS** - Utility-first CSS framework

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**⚠️ Safety Notice**: This system is designed to assist with drowsiness detection but should not be relied upon as the sole safety measure. Always prioritize proper rest and safe driving practices.