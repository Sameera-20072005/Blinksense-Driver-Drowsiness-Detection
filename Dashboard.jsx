import React, { useState, useEffect } from 'react'
import { useAlerts } from '../App'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const Dashboard = () => {
  const { alerts } = useAlerts()
  const [sessionData, setSessionData] = useState(null)

  useEffect(() => {
    // Fetch session data from backend
    fetch('http://localhost:8000/api/metrics')
      .then(res => res.json())
      .then(data => setSessionData(data))
      .catch(console.error)
  }, [])

  const todayAlerts = alerts.filter(alert => {
    const today = new Date().toDateString()
    return new Date(alert.timestamp).toDateString() === today
  })

  const alertsByHour = Array.from({ length: 24 }, (_, hour) => {
    const count = todayAlerts.filter(alert => {
      return new Date(alert.timestamp).getHours() === hour
    }).length
    return { hour: `${hour}:00`, alerts: count }
  })

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Alerts Today"
          value={todayAlerts.length}
          icon="🚨"
          color="bg-red-500"
        />
        <StatCard
          title="Session Duration"
          value={sessionData ? `${Math.round(sessionData.session_duration / 60)}m` : '0m'}
          icon="⏱️"
          color="bg-blue-500"
        />
        <StatCard
          title="Average EAR"
          value={sessionData ? sessionData.avg_ear.toFixed(3) : '0.000'}
          icon="👁️"
          color="bg-green-500"
        />
        <StatCard
          title="Status"
          value={alerts.length > 0 && alerts[0].timestamp > Date.now() - 300000 ? 'Alert' : 'Safe'}
          icon="✅"
          color="bg-purple-500"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Alerts by Hour</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={alertsByHour}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="alerts" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {alerts.slice(0, 5).map(alert => (
              <div key={alert.id} className="flex items-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl mr-3">⚠️</div>
                <div className="flex-1">
                  <p className="font-semibold">{alert.message}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
            {alerts.length === 0 && (
              <p className="text-gray-500 text-center py-8">No alerts recorded yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const StatCard = ({ title, value, icon, color }) => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
      <div className={`${color} rounded-full p-3 text-white text-2xl`}>
        {icon}
      </div>
    </div>
  </div>
)

export default Dashboard