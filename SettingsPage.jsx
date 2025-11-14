import React, { useState } from 'react'
import { useAlerts } from '../App'
import { Save, RotateCcw } from 'lucide-react'

const SettingsPage = () => {
  const { settings, updateSettings } = useAlerts()
  const [localSettings, setLocalSettings] = useState(settings)
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    updateSettings(localSettings)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    const defaultSettings = {
      earThreshold: 0.25,
      closureDuration: 3,
      alertSound: true,
      sensitivity: 0.5
    }
    setLocalSettings(defaultSettings)
  }

  const handleChange = (key, value) => {
    setLocalSettings(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Settings</h1>

      <div className="space-y-8">
        {/* Detection Settings */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-6">Detection Settings</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                EAR Threshold: {localSettings.earThreshold.toFixed(3)}
              </label>
              <input
                type="range"
                min="0.15"
                max="0.35"
                step="0.005"
                value={localSettings.earThreshold}
                onChange={(e) => handleChange('earThreshold', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>More Sensitive (0.15)</span>
                <span>Less Sensitive (0.35)</span>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Lower values trigger alerts more easily. Recommended: 0.25
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Closure Duration: {localSettings.closureDuration} seconds
              </label>
              <input
                type="range"
                min="1"
                max="10"
                step="0.5"
                value={localSettings.closureDuration}
                onChange={(e) => handleChange('closureDuration', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1 second</span>
                <span>10 seconds</span>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                How long eyes must be closed before triggering an alert
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Detection Sensitivity: {Math.round(localSettings.sensitivity * 100)}%
              </label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={localSettings.sensitivity}
                onChange={(e) => handleChange('sensitivity', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Low (10%)</span>
                <span>High (100%)</span>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Overall detection sensitivity for face and eye tracking
              </p>
            </div>
          </div>
        </div>

        {/* Alert Settings */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-6">Alert Settings</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-700">Audio Alerts</h3>
                <p className="text-sm text-gray-500">Play sound when drowsiness is detected</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={localSettings.alertSound}
                  onChange={(e) => handleChange('alertSound', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Camera Settings */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-6">Camera Settings</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Camera Source
              </label>
              <select className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                <option value="0">Default Camera (0)</option>
                <option value="1">Camera 1</option>
                <option value="2">Camera 2</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video Quality
              </label>
              <select className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                <option value="480p">480p (Faster)</option>
                <option value="720p">720p (Balanced)</option>
                <option value="1080p">1080p (Higher Quality)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Privacy Settings */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-6">Privacy & Data</h2>
          
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-green-800 mb-2">🔒 Privacy Protected</h3>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• Camera feed is processed locally in your browser</li>
                <li>• No video data is uploaded to any server</li>
                <li>• Alerts are stored only in your browser's local storage</li>
                <li>• You can clear all data at any time</li>
              </ul>
            </div>

            <button className="w-full px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors">
              Clear All Local Data
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between">
          <button
            onClick={handleReset}
            className="flex items-center space-x-2 px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            <RotateCcw size={16} />
            <span>Reset to Defaults</span>
          </button>
          
          <button
            onClick={handleSave}
            className={`flex items-center space-x-2 px-6 py-2 rounded-lg transition-colors ${
              saved 
                ? 'bg-green-500 text-white' 
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            <Save size={16} />
            <span>{saved ? 'Saved!' : 'Save Settings'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage