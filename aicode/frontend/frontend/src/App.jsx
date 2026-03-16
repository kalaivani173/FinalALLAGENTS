import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ToastProvider } from './contexts/ToastContext'
import AdminPortal from './components/AdminPortal'
import Login from './components/Login'
import './App.css'

import React from 'react'

class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, errorInfo) {
    // eslint-disable-next-line no-console
    console.error('App crashed:', error, errorInfo)
  }

  render() {
    if (this.state.error) {
      const msg = this.state.error?.message || String(this.state.error)
      return (
        <div className="min-h-screen bg-slate-50 text-slate-900 flex items-center justify-center p-6">
          <div className="w-full max-w-2xl rounded-2xl border bg-white p-6 shadow-sm">
            <div className="text-sm font-semibold text-rose-600">Something went wrong</div>
            <div className="mt-2 text-lg font-semibold">The portal crashed while rendering.</div>
            <div className="mt-3 text-sm text-slate-700">
              <span className="font-medium">Error:</span> {msg}
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                className="rounded-lg border px-3 py-2 text-sm hover:bg-slate-50"
                onClick={() => window.location.reload()}
              >
                Reload
              </button>
              <button
                type="button"
                className="rounded-lg border px-3 py-2 text-sm hover:bg-slate-50"
                onClick={() => {
                  try {
                    sessionStorage.removeItem('user')
                  } catch {
                    // ignore
                  }
                  window.location.reload()
                }}
              >
                Reset session
              </button>
            </div>
            <div className="mt-4 text-xs text-slate-500">
              Open DevTools Console to see the full stack trace.
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

function AppContent() {
  const { isAuthenticated, login } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={<Login onLogin={login} />} />
      <Route path="/" element={isAuthenticated ? <AdminPortal /> : <Login onLogin={login} />} />
      <Route path="/admin" element={isAuthenticated ? <AdminPortal /> : <Login onLogin={login} />} />
      <Route path="*" element={isAuthenticated ? <AdminPortal /> : <Login onLogin={login} />} />
    </Routes>
  )
}

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <Router>
          <AppErrorBoundary>
            <AppContent />
          </AppErrorBoundary>
        </Router>
      </AuthProvider>
    </ToastProvider>
  )
}

export default App
