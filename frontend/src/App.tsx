import { Routes, Route } from 'react-router-dom'
import { Suspense } from 'react'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoadingSpinner from './components/LoadingSpinner'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Layout>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/memorials" element={<div>Memorials Page (Coming Soon)</div>} />
            <Route path="/stories" element={<div>Stories Page (Coming Soon)</div>} />
            <Route path="/chat" element={<div>AI Chat Page (Coming Soon)</div>} />
            <Route path="*" element={<div>Page Not Found</div>} />
          </Routes>
        </Suspense>
      </Layout>
    </div>
  )
}

export default App 