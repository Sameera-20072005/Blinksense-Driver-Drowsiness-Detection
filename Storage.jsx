import React, { useState } from 'react'
import { useAlerts } from '../App'
import { Download, FileText, Trash2 } from 'lucide-react'

const Storage = () => {
  const { alerts } = useAlerts()
  const [sessions] = useState([
    {
      id: 1,
      date: '2024-01-15',
      duration: '45 minutes',
      alerts: 3,
      avgEar: 0.287,
      status: 'completed'
    },
    {
      id: 2,
      date: '2024-01-14',
      duration: '32 minutes',
      alerts: 1,
      avgEar: 0.295,
      status: 'completed'
    },
    {
      id: 3,
      date: '2024-01-13',
      duration: '28 minutes',
      alerts: 0,
      avgEar: 0.312,
      status: 'completed'
    }
  ])

  const exportToJSON = () => {
    const data = {
      exportDate: new Date().toISOString(),
      sessions: sessions,
      alerts: alerts,
      summary: {
        totalSessions: sessions.length,
        totalAlerts: alerts.length,
        avgSessionDuration: sessions.reduce((sum, s) => sum + parseInt(s.duration), 0) / sessions.length
      }
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `blinksense-data-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const exportToCSV = () => {
    const csvContent = [
      ['Date', 'Duration', 'Alerts', 'Avg EAR', 'Status'],
      ...sessions.map(session => [
        session.date,
        session.duration,
        session.alerts,
        session.avgEar,
        session.status
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `blinksense-sessions-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'interrupted': return 'bg-yellow-100 text-yellow-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Data Storage</h1>
        <div className="flex space-x-4">
          <button
            onClick={exportToJSON}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Download size={16} />
            <span>Export JSON</span>
          </button>
          <button
            onClick={exportToCSV}
            className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            <FileText size={16} />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Storage Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-2xl font-bold text-blue-600">{sessions.length}</div>
          <div className="text-sm text-gray-600">Total Sessions</div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-2xl font-bold text-red-600">{alerts.length}</div>
          <div className="text-sm text-gray-600">Total Alerts</div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-2xl font-bold text-green-600">
            {sessions.reduce((sum, s) => sum + parseInt(s.duration), 0)}m
          </div>
          <div className="text-sm text-gray-600">Total Duration</div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-2xl font-bold text-purple-600">
            {(localStorage.getItem('blinksense-alerts')?.length || 0) + 
             (localStorage.getItem('blinksense-settings')?.length || 0)}B
          </div>
          <div className="text-sm text-gray-600">Storage Used</div>
        </div>
      </div>

      {/* Sessions Table */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Detection Sessions</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Alerts
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg EAR
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sessions.map((session) => (
                <tr key={session.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {session.date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {session.duration}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      session.alerts > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {session.alerts}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {session.avgEar.toFixed(3)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(session.status)}`}>
                      {session.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button className="text-blue-600 hover:text-blue-900">
                        <Download size={16} />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Management */}
      <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Data Management</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-medium mb-3">Local Storage</h3>
            <p className="text-gray-600 mb-4">
              All data is stored locally in your browser. No data is sent to external servers.
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Alerts:</span>
                <span>{alerts.length} items</span>
              </div>
              <div className="flex justify-between">
                <span>Settings:</span>
                <span>1 item</span>
              </div>
              <div className="flex justify-between">
                <span>Sessions:</span>
                <span>{sessions.length} items</span>
              </div>
            </div>
          </div>
          <div>
            <h3 className="text-lg font-medium mb-3">Privacy & Security</h3>
            <ul className="text-gray-600 space-y-2 text-sm">
              <li>✅ No data uploaded to servers</li>
              <li>✅ Camera feed processed locally</li>
              <li>✅ Alerts stored in browser only</li>
              <li>✅ Export data anytime</li>
              <li>✅ Clear data anytime</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Storage