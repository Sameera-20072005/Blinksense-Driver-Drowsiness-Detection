import React, { useState, useEffect, createContext, useContext } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Home, BarChart3, AlertTriangle, TrendingUp, Database, Settings } from 'lucide-react'
import HomePage from './pages/HomePage'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import Storage from './pages/Storage'
import Alerts from './pages/Alerts'
import SettingsPage from './pages/SettingsPage'

const AlertContext = createContext()

export const useAlerts = () => useContext(AlertContext)

function App() {
  const [alerts, setAlerts] = useState(() => {
    const saved = localStorage.getItem('blinksense-alerts')
    return saved ? JSON.parse(saved) : []
  })

  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('blinksense-settings')
    return saved ? JSON.parse(saved) : {
      earThreshold: 0.25,
      closureDuration: 3,
      alertSound: true,
      sensitivity: 0.5
    }
  })

  const addAlert = (alert) => {
    const newAlert = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...alert
    }
    const updatedAlerts = [newAlert, ...alerts].slice(0, 50)
    setAlerts(updatedAlerts)
    localStorage.setItem('blinksense-alerts', JSON.stringify(updatedAlerts))
  }

  const clearAlerts = () => {
    setAlerts([])
    localStorage.removeItem('blinksense-alerts')
  }

  const updateSettings = (newSettings) => {
    setSettings(newSettings)
    localStorage.setItem('blinksense-settings', JSON.stringify(newSettings))
  }

  return (
    <AlertContext.Provider value={{ alerts, addAlert, clearAlerts, settings, updateSettings }}>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-pink-50 to-blue-50">
          <nav className="bg-white shadow-lg">
            <div className="max-w-7xl mx-auto px-4">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <span className="text-2xl font-bold text-pink-600">BlinkSense</span>
                </div>
                <div className="flex space-x-8">
                  <NavLink to="/" icon={<Home size={20} />} text="Home" />
                  <NavLink to="/dashboard" icon={<BarChart3 size={20} />} text="Dashboard" />
                  <NavLink to="/analytics" icon={<TrendingUp size={20} />} text="Analytics" />
                  <NavLink to="/storage" icon={<Database size={20} />} text="Storage" />
                  <NavLink to="/alerts" icon={<AlertTriangle size={20} />} text="Alerts" />
                  <NavLink to="/settings" icon={<Settings size={20} />} text="Settings" />
                </div>
              </div>
            </div>
          </nav>

          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/storage" element={<Storage />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>
      </Router>
    </AlertContext.Provider>
  )
}

const NavLink = ({ to, icon, text }) => (
  <Link
    to={to}
    className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-pink-600 hover:bg-pink-50 transition-colors"
  >
    {icon}
    <span>{text}</span>
  </Link>
)

export default App