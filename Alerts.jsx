import React from 'react'
import { useAlerts } from '../App'
import { Trash2, AlertTriangle, CheckCircle } from 'lucide-react'

const Alerts = () => {
  const { alerts, clearAlerts } = useAlerts()

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-red-100 border-red-500 text-red-800'
      case 'medium': return 'bg-yellow-100 border-yellow-500 text-yellow-800'
      case 'low': return 'bg-blue-100 border-blue-500 text-blue-800'
      default: return 'bg-gray-100 border-gray-500 text-gray-800'
    }
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high': return <AlertTriangle className="text-red-500" size={20} />
      case 'medium': return <AlertTriangle className="text-yellow-500" size={20} />
      case 'low': return <AlertTriangle className="text-blue-500" size={20} />
      default: return <CheckCircle className="text-gray-500" size={20} />
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Alert History</h1>
        {alerts.length > 0 && (
          <button
            onClick={clearAlerts}
            className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            <Trash2 size={16} />
            <span>Clear All</span>
          </button>
        )}
      </div>

      {alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Alerts</h2>
          <p className="text-gray-500">Great job! No drowsiness alerts have been triggered.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map(alert => (
            <div
              key={alert.id}
              className={`border-l-4 p-6 rounded-lg shadow-lg ${getSeverityColor(alert.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold">{alert.type} Alert</h3>
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-white bg-opacity-50">
                        {alert.severity?.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm mb-2">{alert.message}</p>
                    <div className="flex items-center space-x-4 text-xs opacity-75">
                      <span>📅 {new Date(alert.timestamp).toLocaleDateString()}</span>
                      <span>🕐 {new Date(alert.timestamp).toLocaleTimeString()}</span>
                      {alert.duration && <span>⏱️ Duration: {alert.duration}</span>}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Alert Statistics */}
      {alerts.length > 0 && (
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Alert Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {alerts.filter(a => a.severity === 'high').length}
              </div>
              <div className="text-sm text-red-700">High Severity</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {alerts.filter(a => a.severity === 'medium').length}
              </div>
              <div className="text-sm text-yellow-700">Medium Severity</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {alerts.filter(a => a.severity === 'low').length}
              </div>
              <div className="text-sm text-blue-700">Low Severity</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Alerts