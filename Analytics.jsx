import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { useAlerts } from '../App'

const Analytics = () => {
  const { alerts } = useAlerts()
  const [earData, setEarData] = useState([])

  useEffect(() => {
    // Generate sample EAR data for visualization
    const generateEarData = () => {
      const data = []
      const now = new Date()
      for (let i = 59; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 1000)
        data.push({
          time: time.toLocaleTimeString(),
          ear: 0.25 + Math.random() * 0.1 + (Math.sin(i / 10) * 0.05),
          timestamp: time.getTime()
        })
      }
      return data
    }

    setEarData(generateEarData())
    
    // Update data every 5 seconds
    const interval = setInterval(() => {
      setEarData(prev => {
        const newData = [...prev.slice(1)]
        const now = new Date()
        newData.push({
          time: now.toLocaleTimeString(),
          ear: 0.25 + Math.random() * 0.1 + (Math.sin(Date.now() / 10000) * 0.05),
          timestamp: now.getTime()
        })
        return newData
      })
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  // Process alert data for analytics
  const alertsByDay = alerts.reduce((acc, alert) => {
    const day = new Date(alert.timestamp).toLocaleDateString()
    acc[day] = (acc[day] || 0) + 1
    return acc
  }, {})

  const dailyAlertData = Object.entries(alertsByDay).map(([day, count]) => ({
    day: day.split('/').slice(0, 2).join('/'),
    alerts: count
  }))

  const blinkPatternData = [
    { hour: '6AM', blinks: 15, drowsiness: 0 },
    { hour: '9AM', blinks: 18, drowsiness: 1 },
    { hour: '12PM', blinks: 20, drowsiness: 0 },
    { hour: '3PM', blinks: 16, drowsiness: 2 },
    { hour: '6PM', blinks: 14, drowsiness: 3 },
    { hour: '9PM', blinks: 12, drowsiness: 1 }
  ]

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Analytics</h1>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Average EAR"
          value={earData.length > 0 ? (earData.reduce((sum, d) => sum + d.ear, 0) / earData.length).toFixed(3) : '0.000'}
          subtitle="Last 60 seconds"
          color="bg-blue-500"
        />
        <MetricCard
          title="Total Alerts"
          value={alerts.length}
          subtitle="All time"
          color="bg-red-500"
        />
        <MetricCard
          title="PERCLOS"
          value="12.5%"
          subtitle="Percentage of eyelid closure"
          color="bg-yellow-500"
        />
        <MetricCard
          title="Blink Rate"
          value="18/min"
          subtitle="Current session"
          color="bg-green-500"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* EAR Over Time */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Eye Aspect Ratio (Real-time)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={earData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis domain={[0.15, 0.4]} />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="ear" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-2 text-sm text-gray-600">
            <span className="inline-block w-3 h-3 bg-red-200 mr-2"></span>
            Drowsiness threshold: 0.25
          </div>
        </div>

        {/* Daily Alerts */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Daily Alert Count</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dailyAlertData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="alerts" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Blink Patterns */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Blink Patterns & Drowsiness Events</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={blinkPatternData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="blinks" 
              stroke="#10b981" 
              strokeWidth={2}
              name="Blinks per minute"
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="drowsiness" 
              stroke="#ef4444" 
              strokeWidth={2}
              name="Drowsiness events"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Statistics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Detailed Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-medium mb-3">Detection Metrics</h3>
            <div className="space-y-3">
              <StatRow label="Session Duration" value="45 minutes" />
              <StatRow label="Frames Processed" value="27,000" />
              <StatRow label="Face Detection Rate" value="98.5%" />
              <StatRow label="Eye Detection Rate" value="96.2%" />
            </div>
          </div>
          <div>
            <h3 className="text-lg font-medium mb-3">Alert Analysis</h3>
            <div className="space-y-3">
              <StatRow label="Average Alert Duration" value="3.2 seconds" />
              <StatRow label="Longest Alert" value="5.8 seconds" />
              <StatRow label="Time Between Alerts" value="8.5 minutes" />
              <StatRow label="False Positive Rate" value="2.1%" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const MetricCard = ({ title, value, subtitle, color }) => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-xs text-gray-500">{subtitle}</p>
      </div>
      <div className={`${color} rounded-full p-3 text-white`}>
        📊
      </div>
    </div>
  </div>
)

const StatRow = ({ label, value }) => (
  <div className="flex justify-between items-center py-2 border-b border-gray-100">
    <span className="text-gray-600">{label}</span>
    <span className="font-semibold">{value}</span>
  </div>
)

export default Analytics