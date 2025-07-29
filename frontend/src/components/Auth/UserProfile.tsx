/**
 * User Profile component.
 * Displays current user information and authentication status.
 */

import { useAuth } from '../../contexts/AuthContext';
import LogoutButton from './LogoutButton';

interface UserProfileProps {
  showAuthMethod?: boolean;
  showLogoutButton?: boolean;
  className?: string;
}

export default function UserProfile({ 
  showAuthMethod = false, 
  showLogoutButton = true,
  className = ''
}: UserProfileProps) {
  const { user, authMethod, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return null;
  }

  const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ') || user.full_name || user.email;
  const initials = fullName
    .split(' ')
    .map(name => name.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('');

  const getAuthMethodDisplay = (method: string | null) => {
    if (!method) return 'Unknown';
    
    if (method.includes('oidc_cookie')) {
      const provider = method.split('_')[2];
      return `OIDC (${provider === 'cognito' ? 'AWS Cognito' : 'Authentik'})`;
    }
    if (method.includes('oidc_bearer')) {
      const provider = method.split('_')[2];
      return `OIDC API (${provider === 'cognito' ? 'AWS Cognito' : 'Authentik'})`;
    }
    if (method === 'legacy_jwt') return 'Legacy JWT';
    if (method === 'legacy_authentik_headers') return 'Legacy Authentik';
    
    return method;
  };

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* User Avatar */}
      <div className="flex-shrink-0">
        <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center">
          <span className="text-sm font-medium text-white">{initials}</span>
        </div>
      </div>

      {/* User Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-2">
          <p className="text-sm font-medium text-gray-900 truncate">{fullName}</p>
          {user.is_admin && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
              Admin
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 truncate">{user.email}</p>
        {showAuthMethod && authMethod && (
          <p className="text-xs text-gray-400 truncate">
            {getAuthMethodDisplay(authMethod)}
          </p>
        )}
      </div>

      {/* Logout Button */}
      {showLogoutButton && (
        <div className="flex-shrink-0">
          <LogoutButton size="sm" variant="ghost" />
        </div>
      )}
    </div>
  );
} 