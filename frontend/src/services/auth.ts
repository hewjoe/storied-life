/**
 * OIDC Authentication service for Storied Life frontend.
 * Handles communication with backend for OIDC configuration and token management.
 */

import axios from 'axios';

export interface OIDCConfig {
  issuer: string;
  clientId: string;
  redirectUri: string;
  scopes: string[];
  responseType: string;
  usePKCE: boolean;
  provider: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  first_name: string | null;
  last_name: string | null;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  profile_image_url?: string;
  bio?: string;
  external_id?: string;
  created_at: string;
  updated_at?: string;
  last_login?: string;
  is_admin: boolean;
  is_moderator?: boolean;
}

export interface AuthStatus {
  authenticated: boolean;
  user: User | null;
  auth_method: string | null;
  provider: string;
  oidc_enabled: boolean;
  legacy_authentik_headers: boolean;
}

export interface LoginCallbackData {
  message: string;
  user: User;
  expires_in: number;
}

class AuthService {
  private baseURL: string;

  constructor() {
    // In development, use empty string to rely on Vite proxy
    // In production, use the environment variable
    this.baseURL = import.meta.env.PROD ? (import.meta.env.VITE_API_URL || '') : '';
  }

  /**
   * Get OIDC configuration from backend
   */
  async getOIDCConfig(): Promise<OIDCConfig> {
    try {
      const response = await axios.get(`${this.baseURL}/api/v1/auth/oidc-config`);
      return response.data;
    } catch (error) {
      console.error('Failed to get OIDC config:', error);
      throw new Error('Failed to load authentication configuration');
    }
  }

  /**
   * Get current authentication status
   */
  async getAuthStatus(): Promise<AuthStatus> {
    try {
      const response = await axios.get(`${this.baseURL}/api/v1/auth/status`, {
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get auth status:', error);
      return {
        authenticated: false,
        user: null,
        auth_method: null,
        provider: 'unknown',
        oidc_enabled: false,
        legacy_authentik_headers: false
      };
    }
  }

  /**
   * Handle OIDC callback - exchange authorization code for tokens
   */
  async handleCallback(code: string, state: string, codeVerifier: string): Promise<LoginCallbackData> {
    try {
      const formData = new FormData();
      formData.append('code', code);
      formData.append('state', state);
      formData.append('code_verifier', codeVerifier);

      const response = await axios.post(
        `${this.baseURL}/api/v1/auth/callback`,
        formData,
        {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Callback handling failed:', error);
      throw new Error('Login failed');
    }
  }

  /**
   * Logout user and clear session
   */
  async logout(): Promise<{ message: string; logout_url?: string }> {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/v1/auth/logout`,
        {},
        { withCredentials: true }
      );
      return response.data;
    } catch (error) {
      console.error('Logout failed:', error);
      throw new Error('Logout failed');
    }
  }

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await axios.get(`${this.baseURL}/api/v1/auth/me`, {
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw new Error('Failed to get user information');
    }
  }
}

export const authService = new AuthService(); 