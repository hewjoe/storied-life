import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { HeartIcon, BookOpenIcon, ChatBubbleLeftRightIcon, HomeIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../contexts/AuthContext'
import LoginButton from './Auth/LoginButton'
import UserProfile from './Auth/UserProfile'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { isAuthenticated, isLoading, error } = useAuth()

  const navigation = [
    { name: 'Home', href: '/', icon: HomeIcon },
    { name: 'Legacies', href: '/legacies', icon: HeartIcon },
    { name: 'Stories', href: '/stories', icon: BookOpenIcon },
    { name: 'AI Chat', href: '/chat', icon: ChatBubbleLeftRightIcon },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              {/* Logo */}
              <div className="flex-shrink-0 flex items-center">
                <Link to="/" className="text-2xl font-bold text-gray-900">
                  Storied Life
                </Link>
              </div>
              
              {/* Navigation Links */}
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                        isActive(item.href)
                          ? 'border-blue-500 text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </div>

            {/* User menu */}
            <div className="flex items-center">
              {/* Debug info */}
              <div className="mr-2 text-xs text-gray-500">
                Loading: {isLoading ? 'true' : 'false'} | Auth: {isAuthenticated ? 'true' : 'false'}
              </div>
              
              {error && (
                <div className="mr-4 text-red-600 text-sm max-w-xs truncate">
                  {error}
                </div>
              )}
              {isLoading ? (
                <div className="w-8 h-8 rounded-full bg-gray-200 animate-pulse"></div>
              ) : isAuthenticated ? (
                <UserProfile showAuthMethod={false} />
              ) : (
                <LoginButton size="md" />
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-500">
            <p>&copy; 2025 Storied Life. Preserving memories. Honoring legacies.</p>
          </div>
        </div>
      </footer>
    </div>
  )
} 