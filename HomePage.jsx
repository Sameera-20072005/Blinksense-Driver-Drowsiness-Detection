import React, { useState, useEffect, useRef } from 'react'
import { useAlerts } from '../App'
import { Eye, EyeOff, AlertTriangle, Camera } from 'lucide-react'

const HomePage = () => {
  const { addAlert, settings } = useAlerts()
  const [isConnected, setIsConnected] = useState(false)
  const [earValue, setEarValue] = useState(0)
  const [isDrowsy, setIsDrowsy] = useState(false)
  const [faceDetected, setFaceDetected] = useState(false)
  const [cameraStream, setCameraStream] = useState(null)
  const wsRef = useRef(null)
  const audioRef = useRef(null)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)

  useEffect(() => {
    // Create alarm sound using Web Audio API
    const createAlarmSound = () => {
      let audioContext
      
      const playAlarm = () => {
        try {
          if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)()
          }
          
          console.log('Creating alarm sound...')
          
          // Play 3 beeps
          for (let i = 0; i < 3; i++) {
            setTimeout(() => {
              const oscillator = audioContext.createOscillator()
              const gainNode = audioContext.createGain()
              
              oscillator.connect(gainNode)
              gainNode.connect(audioContext.destination)
              
              // Alternating frequencies for attention
              oscillator.frequency.setValueAtTime(i % 2 === 0 ? 800 : 1000, audioContext.currentTime)
              oscillator.type = 'sine'
              
              // Volume envelope
              gainNode.gain.setValueAtTime(0, audioContext.currentTime)
              gainNode.gain.linearRampToValueAtTime(0.5, audioContext.currentTime + 0.05)
              gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.4)
              
              oscillator.start(audioContext.currentTime)
              oscillator.stop(audioContext.currentTime + 0.4)
              
              console.log(`Beep ${i + 1} played`)
            }, i * 500)
          }
        } catch (error) {
          console.error('Alarm creation failed:', error)
        }
      }
      
      return playAlarm
    }
    
    audioRef.current = createAlarmSound()
    
    // Initialize camera
    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: 640, 
            height: 480,
            facingMode: 'user'
          } 
        })
        setCameraStream(stream)
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
      } catch (error) {
        console.error('Camera access failed:', error)
      }
    }
    
    initCamera()
    
    // Connect to WebSocket
    const connectWebSocket = () => {
      wsRef.current = new WebSocket('ws://localhost:8000/ws')
      
      wsRef.current.onopen = () => {
        setIsConnected(true)
        console.log('Connected to WebSocket')
      }
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data)
        setEarValue(data.ear)
        setFaceDetected(data.face_detected)
        
        if (data.is_drowsy && !isDrowsy) {
          setIsDrowsy(true)
          
          // Add alert to frontend storage
          addAlert({
            type: 'Drowsiness',
            message: 'Eyes closed for more than 3 seconds',
            duration: '3.0s',
            severity: 'high'
          })
          
          // Play alert sound
          if (settings.alertSound && audioRef.current) {
            try {
              audioRef.current() // Call the alarm function
              console.log('ALARM TRIGGERED! Playing sound...')
            } catch (error) {
              console.error('Audio play failed:', error)
            }
          }
          
          // Browser notification
          if (Notification.permission === 'granted') {
            new Notification('BlinkSense Alert', {
              body: 'Drowsiness detected! Please stay alert.',
              icon: '/favicon.ico'
            })
          }
        } else if (!data.is_drowsy) {
          setIsDrowsy(false)
        }
      }
      
      wsRef.current.onclose = () => {
        setIsConnected(false)
        setTimeout(connectWebSocket, 3000) // Reconnect after 3 seconds
      }
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }
    }
    
    connectWebSocket()
    
    // Request notification permission and test alarm
    if (Notification.permission === 'default') {
      Notification.requestPermission()
    }
    
    // Test alarm system on load
    setTimeout(() => {
      console.log('Testing alarm system...')
      if (audioRef.current) {
        console.log('Alarm system ready!')
      }
    }, 2000)
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop())
      }
    }
  }, [addAlert, settings.alertSound, isDrowsy])

  const getStatusColor = () => {
    if (!faceDetected) return 'bg-gray-500'
    if (isDrowsy) return 'bg-red-500 animate-pulse'
    return 'bg-green-500'
  }

  const getStatusText = () => {
    if (!faceDetected) return 'No Face Detected'
    if (isDrowsy) return 'DROWSY - WAKE UP!'
    return 'Awake & Alert'
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Real-Time Drowsiness Detection
        </h1>
        
        {/* Connection Status */}
        <div className="flex justify-center mb-6">
          <div className={`px-4 py-2 rounded-full text-white font-semibold ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
        </div>

        {/* Live Camera Feed */}
        <div className="relative bg-gray-900 rounded-lg aspect-video mb-6 overflow-hidden">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{ transform: 'scaleX(-1)' }} // Mirror effect
          />
          <canvas
            ref={canvasRef}
            className="absolute top-0 left-0 w-full h-full pointer-events-none"
            style={{ transform: 'scaleX(-1)' }}
          />
          
          {/* Camera status overlay */}
          <div className="absolute top-4 left-4 flex items-center space-x-2 bg-black bg-opacity-50 rounded-lg px-3 py-2">
            <Camera className="text-white" size={16} />
            <span className="text-white text-sm">
              {cameraStream ? 'Live' : 'No Camera'}
            </span>
            {cameraStream && (
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            )}
          </div>
          
          {/* Face detection overlay */}
          {faceDetected && (
            <div className="absolute top-4 right-4 bg-green-500 bg-opacity-80 rounded-lg px-3 py-2">
              <span className="text-white text-sm font-semibold">Face Detected</span>
            </div>
          )}
          
          {/* Drowsiness alert overlay */}
          {isDrowsy && (
            <div className="absolute inset-0 bg-red-500 bg-opacity-30 flex items-center justify-center animate-pulse">
              <div className="bg-red-600 text-white px-6 py-3 rounded-lg font-bold text-xl">
                ⚠️ DROWSINESS ALERT ⚠️
              </div>
            </div>
          )}
        </div>

        {/* Status Display */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-3xl mb-2">👁️</div>
            <h3 className="text-lg font-semibold mb-2">Eye Aspect Ratio</h3>
            <p className="text-2xl font-bold text-blue-600">{earValue.toFixed(3)}</p>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-3xl mb-2">{faceDetected ? '😊' : '❓'}</div>
            <h3 className="text-lg font-semibold mb-2">Face Detection</h3>
            <p className={`text-lg font-semibold ${faceDetected ? 'text-green-600' : 'text-gray-500'}`}>
              {faceDetected ? 'Detected' : 'Not Detected'}
            </p>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="text-3xl mb-2">{isDrowsy ? '😴' : '😊'}</div>
            <h3 className="text-lg font-semibold mb-2">Status</h3>
            <div className={`px-4 py-2 rounded-full text-white font-semibold ${getStatusColor()}`}>
              {getStatusText()}
            </div>
          </div>
        </div>

        {/* Alert Banner */}
        {isDrowsy && (
          <div className="bg-red-100 border-l-4 border-red-500 p-4 mb-6 animate-pulse">
            <div className="flex items-center">
              <AlertTriangle className="text-red-500 mr-3" size={24} />
              <div>
                <h4 className="text-red-800 font-bold">DROWSINESS ALERT!</h4>
                <p className="text-red-700">Please take a break or pull over safely.</p>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3 text-blue-800">How it works:</h3>
          <ul className="text-blue-700 space-y-2">
            <li>• System monitors your eye aspect ratio (EAR) in real-time</li>
            <li>• Alert triggers if eyes remain closed for more than 3 seconds</li>
            <li>• All alerts are stored locally in your browser</li>
            <li>• Audio and visual notifications help keep you alert</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default HomePage