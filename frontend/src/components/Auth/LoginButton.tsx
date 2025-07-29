/**
 * Login Button component.
 * Triggers OIDC login flow when clicked.
 */

import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface LoginButtonProps {
  className?: string;
  children?: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export default function LoginButton({
  className = '',
  children,
  variant = 'primary',
  size = 'md'
}: LoginButtonProps) {
  const { login, isLoading, provider, error } = useAuth();

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors';
  
  const variantClasses = {
    primary: 'text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'text-blue-700 bg-blue-100 hover:bg-blue-200 focus:ring-blue-500',
    ghost: 'text-blue-600 hover:text-blue-500 hover:bg-blue-50 focus:ring-blue-500'
  };

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  // Simple click handler for testing
  const handleTestClick = () => {
    console.log('DIRECT CLICK TEST: Button clicked!');
    alert('Direct click test - button is clickable!');
  };

  const handleLogin = async () => {
    try {
      console.log('LoginButton: Click handler triggered');
      console.log('LoginButton: isLoading:', isLoading);
      console.log('LoginButton: error:', error);
      console.log('LoginButton: provider:', provider);
      await login();
    } catch (error) {
      console.error('LoginButton: Error in handleLogin:', error);
    }
  };

  const defaultText = `Sign In${provider === 'cognito' ? ' with AWS Cognito' : ' with Authentik'}`;

  // If there's a serious error, show a simple test button
  if (error && error.includes('timeout')) {
    return (
      <button
        onClick={handleTestClick}
        className={buttonClasses}
        title="Test button - click to verify basic functionality"
      >
        🔧 Test Click
      </button>
    );
  }

  return (
    <button
      onClick={handleLogin}
      onMouseDown={() => console.log('LoginButton: Mouse down')}
      onMouseUp={() => console.log('LoginButton: Mouse up')}
      disabled={isLoading}
      className={buttonClasses}
      title={`Loading: ${isLoading}, Error: ${error || 'none'}, Provider: ${provider}`}
      style={{ pointerEvents: 'auto', zIndex: 10 }}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Signing In...
        </>
      ) : (
        <>
          <svg className="-ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          {children || defaultText}
        </>
      )}
    </button>
  );
} 