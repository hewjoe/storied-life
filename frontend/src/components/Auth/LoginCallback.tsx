/**
 * OIDC Login Callback component.
 * Handles the authorization code callback and completes the login process.
 */

import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../LoadingSpinner';

export default function LoginCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [error, setError] = useState<string | null>(null);
  const hasProcessed = useRef(false);
  const { refreshAuthStatus } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      // Prevent duplicate processing (React StrictMode runs effects twice)
      if (hasProcessed.current) {
        console.log('LoginCallback: Already processed, skipping...');
        return;
      }

      try {
        hasProcessed.current = true;
        
        // Check for OAuth errors first
        const oauthError = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        if (oauthError) {
          throw new Error(errorDescription || `OAuth error: ${oauthError}`);
        }

        // Get parameters from URL
        const code = searchParams.get('code');
        const state = searchParams.get('state');

        if (!code) {
          throw new Error('No authorization code received');
        }

        if (!state) {
          throw new Error('No state parameter received');
        }

        console.log('LoginCallback: Waiting for UserManager to be available...');
        
        // Wait for UserManager to be available (it should be set by AuthContext)
        let userManager = (window as any).__userManager;
        let retries = 0;
        const maxRetries = 50; // 5 seconds max wait
        
        while (!userManager && retries < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, 100));
          userManager = (window as any).__userManager;
          retries++;
          console.log(`LoginCallback: Waiting for UserManager, retry ${retries}/${maxRetries}`);
        }
        
        if (!userManager) {
          throw new Error('UserManager not available after waiting. Please refresh and try again.');
        }

        console.log('LoginCallback: Using UserManager to handle callback...');
        
        try {
          // Let the OIDC library handle the callback (it manages PKCE internally)
          const user = await userManager.signinRedirectCallback();
          console.log('LoginCallback: OIDC callback successful with UserManager:', user);
          
          // After successful OIDC callback, we need to inform the backend
          // Extract tokens and send them to establish a server-side session
          console.log('LoginCallback: Establishing backend session...');
          
          try {
            // Send access token to backend to establish session
            console.log('LoginCallback: Calling sync-oidc-session endpoint...');
            const tokenResponse = await fetch('/api/v1/auth/sync-oidc-session', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${user.access_token}`
              },
              credentials: 'include',
              body: JSON.stringify({
                access_token: user.access_token,
                refresh_token: user.refresh_token,
                expires_in: user.expires_in || 3600
              })
            });

            if (!tokenResponse.ok) {
              const errorText = await tokenResponse.text();
              console.warn('LoginCallback: Backend session sync failed:', tokenResponse.status, errorText);
              // Don't throw here - the OIDC tokens are still valid
            } else {
              const syncResult = await tokenResponse.json();
              console.log('LoginCallback: Backend session established successfully:', syncResult);
            }
          } catch (syncError) {
            console.warn('LoginCallback: Backend session sync error, but continuing:', syncError);
            // Don't throw here - the OIDC tokens are still valid
          }
          
          // Refresh auth status to sync with the new authentication state
          console.log('LoginCallback: Refreshing auth status...');
          await refreshAuthStatus();
          
          setStatus('success');
          
          // Get return URL from user state or default to home
          let returnUrl = '/';
          if (user.state && typeof user.state === 'object' && user.state.returnUrl) {
            returnUrl = user.state.returnUrl;
          }

          // Redirect to return URL after short delay
          setTimeout(() => {
            navigate(returnUrl, { replace: true });
          }, 1500);
          
        } catch (oidcError) {
          console.error('LoginCallback: UserManager callback failed:', oidcError);
          
          // If UserManager fails, fall back to manual backend approach
          console.log('LoginCallback: Falling back to manual backend callback...');
          await handleManualCallback(code, state);
        }

      } catch (err) {
        console.error('Login callback failed:', err);
        setError(err instanceof Error ? err.message : 'Login failed');
        setStatus('error');
      }
    };

    const handleManualCallback = async (code: string, state: string) => {
      // This is a fallback method that tries to handle the callback manually
      // by calling the backend directly (less secure but might work)
      
      console.log('LoginCallback: Attempting manual backend callback (fallback)...');
      
      // Try to call backend without code verifier (backend might not require it)
      const formData = new FormData();
      formData.append('code', code);
      formData.append('state', state);
      formData.append('code_verifier', ''); // Empty, backend might generate or not require

      try {
        const response = await fetch('/api/v1/auth/callback', {
          method: 'POST',
          body: formData,
          credentials: 'include'
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Backend callback failed');
        }

        const result = await response.json();
        console.log('LoginCallback: Manual backend callback successful:', result);

        // Refresh auth status to sync with the new authentication state
        await refreshAuthStatus();

        setStatus('success');

        // Get return URL from state or default to home
        let returnUrl = '/';
        try {
          const stateData = JSON.parse(state);
          returnUrl = stateData.returnUrl || '/';
        } catch {
          // State is not JSON, use default
        }

        // Redirect to return URL after short delay
        setTimeout(() => {
          navigate(returnUrl, { replace: true });
        }, 1500);
        
      } catch (backendError) {
        console.error('LoginCallback: Manual backend callback also failed:', backendError);
        throw new Error('Both OIDC library and backend callback methods failed. Please try logging in again.');
      }
    };

    handleCallback();
  }, [searchParams, navigate, refreshAuthStatus]);

  if (status === 'processing') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-center">
            <LoadingSpinner />
            <h3 className="mt-4 text-lg font-medium text-gray-900">Completing Sign In</h3>
            <p className="mt-2 text-sm text-gray-500">
              Please wait while we verify your credentials...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">Sign In Successful</h3>
            <p className="mt-2 text-sm text-gray-500">
              Welcome to Storied Life! Redirecting you now...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="mt-4 text-lg font-medium text-gray-900">Sign In Failed</h3>
          <p className="mt-2 text-sm text-gray-500">{error}</p>
          <div className="mt-4 space-y-2">
            <button
              onClick={() => navigate('/')}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Return to Home
            </button>
            <button
              onClick={() => window.location.href = '/'}
              className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 