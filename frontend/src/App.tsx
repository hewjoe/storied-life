import { Routes, Route } from 'react-router-dom'
import { Suspense } from 'react'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoadingSpinner from './components/LoadingSpinner'
import ProtectedRoute from './components/ProtectedRoute'
import LoginCallback from './components/Auth/LoginCallback'

function App() {
  return (
    <AuthProvider>
      <Layout>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login/callback" element={<LoginCallback />} />
            
            {/* Protected routes */}
            <Route 
              path="/legacies" 
              element={
                <ProtectedRoute>
                  <div>Legacies Page (Coming Soon)</div>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/stories" 
              element={
                <ProtectedRoute>
                  <div>Stories Page (Coming Soon)</div>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/chat" 
              element={
                <ProtectedRoute>
                  <div>AI Chat Page (Coming Soon)</div>
                </ProtectedRoute>
              } 
            />
            
            {/* Catch all */}
            <Route path="*" element={<div>Page Not Found</div>} />
          </Routes>
        </Suspense>
      </Layout>
    </AuthProvider>
  )
}

export default App