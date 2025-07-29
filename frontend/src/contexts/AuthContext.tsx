/**
 * Authentication Context Provider for Storied Life.
 * Manages OIDC authentication state and provides auth methods.
 */

import { createContext, useContext, useEffect, useState, ReactNode, useRef } from 'react';
import { UserManager, User as OidcUser, UserManagerSettings } from 'oidc-client-ts';
import { authService, User } from '../services/auth';

export interface AuthContextType {
  // Authentication state
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
  error: string | null;
  
  // Authentication methods
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshAuthStatus: () => Promise<void>;
  
  // OIDC info
  provider: string;
  authMethod: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userManager, setUserManager] = useState<UserManager | null>(null);
  const [provider, setProvider] = useState('unknown');
  const [authMethod, setAuthMethod] = useState<string | null>(null);
  const hasInitialized = useRef(false);

  // Initialize OIDC User Manager
  useEffect(() => {
    const initializeAuth = async () => {
      // Prevent duplicate initialization (React StrictMode)
      if (hasInitialized.current) {
        console.log('AuthContext: Already initialized, skipping...');
        return;
      }

      try {
        hasInitialized.current = true;
        console.log('AuthContext: Starting initialization...');
        setError(null);
        
        // Get OIDC configuration from backend
        console.log('AuthContext: Fetching OIDC config from backend...');
        const oidcConfig = await authService.getOIDCConfig();
        console.log('AuthContext: OIDC config received:', oidcConfig);
        setProvider(oidcConfig.provider);

        // Configure OIDC User Manager
        const userManagerSettings: UserManagerSettings = {
          authority: oidcConfig.issuer,
          client_id: oidcConfig.clientId,
          redirect_uri: oidcConfig.redirectUri,
          response_type: oidcConfig.responseType,
          scope: oidcConfig.scopes.join(' '),
          automaticSilentRenew: true,
          silent_redirect_uri: `${window.location.origin}/silent-refresh.html`,
          post_logout_redirect_uri: window.location.origin,
          
          // PKCE settings
          ...(oidcConfig.usePKCE && {
            response_mode: 'query',
            loadUserInfo: false // Use claims from token instead
          })
        };

        console.log('AuthContext: Creating UserManager...');
        console.log('AuthContext: UserManager settings:', userManagerSettings);
        
        let manager;
        try {
          manager = new UserManager(userManagerSettings);
          console.log('AuthContext: UserManager instantiated');
        } catch (error) {
          console.error('AuthContext: Failed to create UserManager:', error);
          throw error;
        }
        
        setUserManager(manager);
        console.log('AuthContext: UserManager set in state');

        // Make UserManager available globally for callback handling
        (window as any).__userManager = manager;

        // Set up event handlers
        manager.events.addUserLoaded((_oidcUser: OidcUser) => {
          console.log('OIDC user loaded:', _oidcUser);
          // If using client-side flow, sync with backend
          syncUserFromOidc(_oidcUser);
        });

        manager.events.addUserUnloaded(() => {
          console.log('OIDC user unloaded');
          setIsAuthenticated(false);
          setUser(null);
          setAuthMethod(null);
        });

        manager.events.addAccessTokenExpired(() => {
          console.log('Access token expired');
          checkAuthStatus();
        });

        manager.events.addSilentRenewError((error) => {
          console.error('Silent renew error:', error);
          setError('Session expired. Please log in again.');
        });

        // Check if we're returning from login
        if (window.location.pathname === '/login/callback') {
          console.log('AuthContext: On callback path, skipping auth status check');
          // The LoginCallback component will handle the callback
          // After successful login, we'll get the state via event or manual refresh
        } else {
          // Check current authentication status
          console.log('AuthContext: Checking auth status...');
          await checkAuthStatus();
        }
        
        console.log('AuthContext: Initialization complete');
        
      } catch (err) {
        console.error('Auth initialization failed:', err);
        const errorMessage = err instanceof Error ? err.message : String(err);
        setError(`Failed to initialize authentication: ${errorMessage}`);
      } finally {
        console.log('AuthContext: Setting isLoading to false');
        setIsLoading(false);
      }
    };

    // Add timeout to detect hanging initialization
    const timeoutId = setTimeout(() => {
      console.error('AuthContext: Initialization timeout after 30 seconds');
      setError('Authentication initialization timeout');
      setIsLoading(false);
    }, 30000);

    initializeAuth().finally(() => {
      clearTimeout(timeoutId);
    });
  }, []);

  // Sync user from OIDC token claims
  const syncUserFromOidc = async (_oidcUser: OidcUser) => {
    try {
      // TODO: Use _oidcUser claims to sync/validate user data when fully implementing OIDC
      // Use backend to get full user info (which syncs from token)
      const authStatus = await authService.getAuthStatus();
      if (authStatus.authenticated && authStatus.user) {
        setUser(authStatus.user);
        setIsAuthenticated(true);
        setAuthMethod(authStatus.auth_method);
      }
    } catch (err) {
      console.error('Failed to sync user from OIDC:', err);
      setError('Failed to sync user information');
    }
  };

  // Check authentication status with backend
  const checkAuthStatus = async () => {
    try {
      console.log('AuthContext: checkAuthStatus() called');
      const authStatus = await authService.getAuthStatus();
      console.log('AuthContext: Auth status response:', authStatus);
      
      setIsAuthenticated(authStatus.authenticated);
      setUser(authStatus.user);
      setAuthMethod(authStatus.auth_method);
      setProvider(authStatus.provider);
      
      console.log('AuthContext: Auth state updated - authenticated:', authStatus.authenticated);
      
      // If authenticated via OIDC, ensure UserManager has the user
      if (authStatus.authenticated && userManager && authStatus.auth_method?.includes('oidc')) {
        const _oidcUser = await userManager.getUser();
        if (!_oidcUser) {
          // User is authenticated with backend but not with OIDC client
          // This can happen after page refresh - try silent signin
          try {
            await userManager.signinSilent();
          } catch (err) {
            console.log('Silent signin failed, but user is authenticated via cookie');
          }
        }
        // TODO: Use _oidcUser for additional OIDC-specific functionality when needed
      }
    } catch (err) {
      console.error('AuthContext: Failed to check auth status:', err);
      setError('Failed to check authentication status');
    }
  };

  // Initiate login flow
  const login = async () => {
    console.log('AuthContext: login() called');
    console.log('AuthContext: userManager:', !!userManager);
    console.log('AuthContext: isLoading:', isLoading);
    
    if (!userManager) {
      console.error('AuthContext: userManager is null - auth not initialized');
      setError('Authentication not initialized');
      return;
    }

    try {
      setError(null);
      setIsLoading(true);
      
      console.log('AuthContext: Starting signinRedirect...');
      
      // Store state for PKCE and CSRF protection
      await userManager.signinRedirect({
        state: { 
          returnUrl: window.location.pathname + window.location.search 
        }
      });
      
      console.log('AuthContext: signinRedirect completed');
    } catch (err) {
      console.error('AuthContext: Login failed:', err);
      setError('Login failed');
      setIsLoading(false);
    }
  };

  // Logout user
  const logout = async () => {
    try {
      setError(null);
      setIsLoading(true);

      // Logout from backend (clears cookies)
      const logoutResponse = await authService.logout();
      
      // Logout from OIDC provider if we have a logout URL
      if (userManager && logoutResponse.logout_url) {
        await userManager.signoutRedirect({
          post_logout_redirect_uri: window.location.origin
        });
      } else {
        // Just clear local state
        setIsAuthenticated(false);
        setUser(null);
        setAuthMethod(null);
        if (userManager) {
          await userManager.removeUser();
        }
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Logout failed:', err);
      setError('Logout failed');
      setIsLoading(false);
    }
  };

  const contextValue: AuthContextType = {
    isAuthenticated,
    user,
    isLoading,
    error,
    login,
    logout,
    refreshAuthStatus: checkAuthStatus,
    provider,
    authMethod
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
} 