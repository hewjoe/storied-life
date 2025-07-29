# Authentication & Authorization ‑ Storied Life

> **TL;DR**  
> Storied Life now authenticates **directly with an OpenID-Connect (OIDC) provider** instead of relying on Traefik’s forward-auth middleware.  
> • **Local development** → Authentik (self-hosted)  
> • **Production on AWS** → Amazon Cognito  
> The active provider is selected at runtime via environment variables so the same containers/images run in every environment.

---

## 1. Motivation for the Pivot
1. **Remove hard dependency on Traefik forward-auth** – simplifies reverse-proxy config and enables alternative ingress solutions (e.g. AWS ALB, CloudFront).  
2. **Leverage first-class OAuth2 / OIDC flows** – standard, battle-tested login UX, refresh-token support, MFA, social logins, etc.  
3. **Cloud portability** – keep dev experience identical while seamlessly swapping in Cognito for managed auth in AWS.

---

## 2. Dual-Provider OIDC Strategy
| Stage | OIDC Issuer | Why |
|-------|-------------|-----|
| Local / CI | **Authentik** (`https://auth.storied-life.me`) | Fast to spin up, full UI, runs in docker-compose. |
| AWS Prod | **Amazon Cognito** (`https://cognito-idp.us-east-1.amazonaws.com/<user-pool-id>`) | Managed, scalable, SAML & social logins, MFA. |

All auth-related settings are injected via **environment variables** (see Section 4). The application reads only generic OIDC values (issuer URL, client ID, JWKS URI, audience, etc.), so any conforming provider can be substituted without code changes.

---

## 3. Authentication Flow (Authorization Code + PKCE)
```mermaid
graph TD;
  browser[(Browser / SPA)] -->|1. Redirect to /login| oidc[OIDC Provider]
  oidc -->|2. User authenticates| oidc
  oidc -->|3. Redirect w/ code| browser
  browser -->|4. POST /api/v1/auth/callback (code, verifier)| backend[FastAPI]
  backend -->|5. Exchange code for tokens| oidc
  oidc -->|6. id_token, access_token| backend
  backend -->|7. Set httpOnly secure cookie (access_token)| browser
  browser -->|8. Subsequent API calls w/ cookie| backend
  backend -->|9. Verify JWT via JWKS| backend
```

Key points:
* **Frontend** performs the Code + PKCE dance using `oidc-client-ts` (or similar).  
* **Backend** accepts the authorization code on `/api/v1/auth/callback`, completes the token exchange, and issues a short-lived session cookie (`SameSite=Lax`, HTTP-only).  
* API requests include `Authorization: Bearer <access_token>` (mobile/native apps) **or** rely on the cookie (web).

---

## 4. Environment Configuration
The following variables are consumed by both frontend & backend.  They can be stored in `.env`, Docker Compose, AWS Secrets Manager, etc.

```bash
# Select provider: "authentik" | "cognito" (default: authentik)
AUTH_PROVIDER=authentik

# Generic OIDC parameters (provider-specific examples below)
OIDC_ISSUER_URL=https://auth.storied-life.me/application/o/storied-life/
OIDC_CLIENT_ID=storied-life-web
OIDC_CLIENT_SECRET=super-secret-in-dev-only
OIDC_AUDIENCE=storied-life-api
OIDC_SCOPES=openid profile email offline_access

# ---- Authentik (dev) ----
AUTHENTIK_HOST=auth.storied-life.me
AUTHENTIK_PORT=443

# ---- Cognito (prod) ----
COGNITO_USER_POOL_ID=us-east-1_AbCdEf123
COGNITO_APP_CLIENT_ID=1h57kf5cpq17m0eml12EXAMPLE
COGNITO_REGION=us-east-1
```

Provider-specific settings are transformed into the generic variables during container startup (see `docker-compose.dev.yml` and `deploy/aws/ecs-params.yml`).

---

## 5. Backend Changes (FastAPI)

### Current State Analysis
The backend currently uses:
- `backend/app/api/deps.py`: Parses `X-authentik-*` headers from Traefik forward-auth
- `backend/app/services/auth_service.py`: Manages users from Authentik headers + JWT fallback
- `backend/app/schemas/auth.py`: Defines `AuthentikUserInfo` for header parsing

### Required Changes

#### 5.1 New OIDC Service (`backend/app/services/oidc_auth.py`)
Replace header-based auth with proper OIDC verification:

```python
class OIDCAuthenticator:
    def __init__(self):
        self.provider = os.getenv("AUTH_PROVIDER", "authentik")
        self.jwks_cache = {}  # Cache JWKS keys
        
    async def get_jwks(self) -> dict:
        """Download and cache JWKS from provider"""
        
    async def verify_token(self, token: str) -> dict:
        """Verify JWT token against JWKS"""
        
    async def get_user_from_token(self, token: str, db: Session) -> User:
        """Extract user claims and sync to database"""
```

#### 5.2 Updated Dependencies (`backend/app/api/deps.py`)
- **Remove**: `get_user_from_authentik_headers()` function
- **Replace**: `get_current_user()` to use OIDC token verification instead of headers
- **Add**: Cookie-based authentication support for web clients

#### 5.3 Enhanced Configuration (`backend/app/core/config.py`)
Add OIDC-specific settings:

```python
# OIDC Configuration (replaces Authentik headers)
AUTH_PROVIDER: str = "authentik"  # "authentik" | "cognito"
OIDC_ISSUER_URL: str = "https://auth.storied-life.me/application/o/storied-life/"
OIDC_CLIENT_ID: str = "storied-life-web"
OIDC_CLIENT_SECRET: Optional[str] = None  # Only needed for confidential clients
OIDC_AUDIENCE: str = "storied-life-api"
OIDC_SCOPES: str = "openid profile email"
OIDC_JWKS_CACHE_TTL: int = 3600  # 1 hour
```

#### 5.4 New Auth Endpoints (`backend/app/api/v1/endpoints/auth.py`)
Add OIDC-specific endpoints:

```python
@router.get("/oidc-config")
async def get_oidc_config():
    """Return OIDC configuration for frontend"""
    
@router.post("/callback")
async def oidc_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle OIDC authorization code callback"""
    
@router.post("/logout")
async def logout(response: Response):
    """Clear session cookies and return logout URL"""
```

#### 5.5 Provider Adapters (`backend/app/services/provider_adapters.py`)
Normalize claims across providers:

```python
class AuthentikAdapter:
    def get_user_info(self, claims: dict) -> UserInfo: ...
    def get_groups(self, claims: dict) -> List[str]: ...
    
class CognitoAdapter:
    def get_user_info(self, claims: dict) -> UserInfo: ...
    def get_groups(self, claims: dict) -> List[str]: ...
```

---

## 6. Frontend Changes (React + TypeScript)

### Current State Analysis
The frontend currently has:
- **No authentication system** - fresh React app with basic routing
- `frontend/package.json`: React 18, React Router, React Query, Zustand for state
- `frontend/src/App.tsx`: Simple routing without auth protection
- **Missing**: OIDC client library, auth context, login/logout components

### Required Changes

#### 6.1 Add OIDC Dependencies (`frontend/package.json`)
Add OIDC client library:

```json
{
  "dependencies": {
    "oidc-client-ts": "^2.4.0",
    "@types/oidc-client": "^1.11.2"
  }
}
```

#### 6.2 OIDC Configuration Service (`frontend/src/services/auth.ts`)
Create service to communicate with backend OIDC config:

```typescript
export interface OIDCConfig {
  issuer: string;
  clientId: string;
  redirectUri: string;
  scopes: string[];
  responseType: string;
}

export const authService = {
  async getOIDCConfig(): Promise<OIDCConfig> {
    // Fetch from /api/v1/auth/oidc-config
  },
  
  async handleCallback(code: string, state: string): Promise<void> {
    // POST to /api/v1/auth/callback
  }
}
```

#### 6.3 Auth Context Provider (`frontend/src/contexts/AuthContext.tsx`)
Replace missing auth with OIDC-aware context:

```typescript
export interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  // Initialize UserManager from oidc-client-ts
  // Handle login/logout/silent refresh
  // Provide authentication state
}
```

#### 6.4 Protected Route Component (`frontend/src/components/ProtectedRoute.tsx`)
Create route wrapper for authenticated content:

```typescript
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading, login } = useAuth();
  
  if (isLoading) return <LoadingSpinner />;
  if (!isAuthenticated) return <LoginPrompt onLogin={login} />;
  
  return <>{children}</>;
}
```

#### 6.5 Updated App Structure (`frontend/src/App.tsx`)
Wrap app with auth providers and add protected routes:

```typescript
function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login/callback" element={<LoginCallback />} />
            <Route 
              path="/memorials" 
              element={
                <ProtectedRoute>
                  <MemorialsPage />
                </ProtectedRoute>
              } 
            />
            {/* Other protected routes */}
          </Routes>
        </Layout>
      </div>
    </AuthProvider>
  );
}
```

#### 6.6 Login/Logout Components (`frontend/src/components/Auth/`)
Create authentication UI components:

- `LoginButton.tsx`: Trigger OIDC login flow
- `LogoutButton.tsx`: Clear session and redirect to provider logout
- `LoginCallback.tsx`: Handle OIDC callback and token exchange
- `UserProfile.tsx`: Display current user info

#### 6.7 HTTP Client Integration (`frontend/src/services/api.ts`)
Update API client to include authentication:

```typescript
// Configure axios/fetch to include access token
axios.defaults.withCredentials = true; // For cookie-based auth
// OR
axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
```

---

## 7. Reverse Proxy / Ingress
Traefik remains the edge router but **no longer performs authentication**:
```yaml
# traefik labels (example)
traefik.http.routers.frontend.rule: "Host(`memorial.localhost`)"
traefik.http.routers.frontend.middlewares: security-headers@file
```
All auth concerns are handled by the browser ↔︎ OIDC provider ↔︎ backend flow.

---

## 8. Authentik Configuration Requirements

### 8.1 Authentik Application Setup

To configure Authentik for OIDC authentication with Storied Life:

#### Create OAuth2/OpenID Provider
1. **Navigate to Applications → Providers** in Authentik admin
2. **Create new Provider** → Select "OAuth2/OpenID Provider"
3. **Configure Provider Settings**:
   ```
   Name: Storied Life OIDC
   Client Type: Public
   Client ID: storied-life-web
   Redirect URIs: 
     - http://localhost:3000/login/callback (development)
     - https://storied-life.me/login/callback (production)
   
   Signing Key: (auto-generated or select existing)
   
   Advanced Settings:
   - Include Claims in ID Token: ✓
   - Issuer Mode: Per Provider
   - Subject Mode: User ID
   
   Scopes:
   - openid (required)
   - profile (required) 
   - email (required)
   - offline_access (for refresh tokens)
   ```

#### Create Application
1. **Navigate to Applications → Applications**
2. **Create new Application**:
   ```
   Name: Storied Life
   Slug: storied-life
   Provider: Storied Life OIDC (from above)
   Policy Engine Mode: any
   ```

#### Configure Groups and Users
1. **Create Groups**:
   - `storied-life-admins` - for system administrators
   - `users` - for regular users
   - `family-members` - for family access (optional)

2. **Assign Users to Groups**:
   - Add admin users to `storied-life-admins`
   - All users should be in `users` group

3. **Group Claims Mapping**:
   - Ensure groups are included in token claims
   - Navigate to **Property Mappings** → Create new **Scope Mapping**:
     ```
     Name: Groups Scope
     Scope: groups
     Expression: return request.user.ak_groups.all()
     ```

### 8.2 Required Environment Variables

```bash
# Authentik OIDC Configuration
AUTH_PROVIDER=authentik
OIDC_ISSUER_URL=https://auth.storied-life.me/application/o/storied-life/
OIDC_CLIENT_ID=storied-life-web
OIDC_CLIENT_SECRET=  # Leave empty for public client
OIDC_AUDIENCE=storied-life-api
OIDC_SCOPES=openid profile email offline_access

# Authentik Host (optional)
AUTHENTIK_HOST=auth.storied-life.me

# Frontend URL for redirects
FRONTEND_URL=http://localhost:3000  # or production URL
```

### 8.3 Expected Token Claims

Authentik should provide these claims in access tokens:

```json
{
  "sub": "ak_user_unique_id",
  "email": "user@example.com", 
  "name": "Full Name",
  "given_name": "First",
  "family_name": "Last",
  "groups": ["storied-life-admins", "users"],
  "aud": "storied-life-api",
  "iss": "https://auth.storied-life.me/application/o/storied-life/",
  "exp": 1703980800,
  "iat": 1703977200
}
```

### 8.4 Testing Configuration

#### Quick Validation (Recommended First Step)
Run the configuration validator to quickly check your setup:

```bash
cd backend
python scripts/validate_oidc_config.py
```

This standalone script will verify:
- ✅ Environment variables are set correctly
- ✅ OIDC discovery endpoint is accessible  
- ✅ JWKS endpoint returns valid keys
- ✅ Required scopes and PKCE support
- ✅ Authentik-specific URL patterns
- ✅ Provider-specific configuration

#### Test Runner Script
Use the test runner for convenient testing:

```bash
cd backend

# Quick validation (config + unit tests)
python scripts/run_auth_tests.py quick

# Unit tests only (fast, no external dependencies)
python scripts/run_auth_tests.py unit

# Integration tests (requires Authentik connectivity)
python scripts/run_auth_tests.py integration

# All authentication tests
python scripts/run_auth_tests.py all

# Configuration validation only
python scripts/run_auth_tests.py config
```

#### Manual pytest Commands
Run tests directly with pytest for more control:

```bash
cd backend

# All OIDC tests
pytest tests/test_oidc_auth.py -v

# Unit tests only (fast)
pytest tests/test_oidc_auth.py -m unit -v

# Integration tests only (requires connectivity)
pytest tests/test_oidc_auth.py -m integration -v

# Configuration tests only
pytest tests/test_oidc_auth.py -m config -v

# With coverage reporting
pytest tests/test_oidc_auth.py --cov=app.services.oidc_auth -v
```

#### Test Coverage
The test suite includes:

**Unit Tests** (no external dependencies):
- ✅ Provider adapter functionality (Authentik vs Cognito)
- ✅ Token verification and claims extraction  
- ✅ User synchronization and admin detection
- ✅ Error handling and edge cases
- ✅ Configuration validation logic

**Integration Tests** (requires connectivity):
- ✅ Live OIDC discovery endpoint validation
- ✅ JWKS endpoint accessibility and structure
- ✅ Real provider connectivity tests
- ✅ Network error handling

**Configuration Tests**:
- ✅ Environment variable validation
- ✅ URL format and security checks
- ✅ Provider-specific requirements

#### Integration Testing
For full end-to-end testing:

1. **Automated Testing**:
   ```bash
   # Quick check (recommended after config changes)
   python scripts/run_auth_tests.py quick
   
   # Full integration test (requires Authentik running)
   python scripts/run_auth_tests.py integration
   ```

2. **Manual Testing**:
   - Visit frontend login page
   - Complete Authentik authentication flow
   - Verify user creation in backend
   - Test admin vs regular user permissions

3. **API Testing**:
   ```bash
   # Get OIDC configuration
   curl http://localhost:8001/api/v1/auth/oidc-config
   
   # Check auth status (should show provider info)
   curl http://localhost:8001/api/v1/auth/status
   
   # Test discovery endpoint directly
   curl https://auth.storied-life.me/application/o/storied-life/.well-known/openid-configuration
   ```

### 8.5 Common Issues and Solutions

#### Issue: "OIDC discovery endpoint not accessible"
- **Solution**: Check `OIDC_ISSUER_URL` is correct and Authentik is running
- **Verify**: Visit `https://your-authentik-host/application/o/your-app/.well-known/openid-configuration`

#### Issue: "JWKS has no keys"  
- **Solution**: Ensure Authentik provider has a signing key configured
- **Check**: Applications → Providers → Your Provider → Signing Key

#### Issue: "Invalid audience"
- **Solution**: Verify `OIDC_AUDIENCE` matches what Authentik expects
- **Fix**: Update audience in provider settings or environment variable

#### Issue: "Groups not appearing in token"
- **Solution**: Configure proper scope mapping for groups claim
- **Check**: Property Mappings → Ensure groups scope mapping exists

#### Issue: "Admin users not detected"
- **Solution**: Verify admin users are in `storied-life-admins` group
- **Check**: Users → Groups tab shows correct group membership

## 9. Migration Steps
1. **Configure Authentik Application** following Section 8.1 above
2. **Drop forward-auth labels** on Traefik services  
3. **Update environment variables** with OIDC configuration
4. **Run validation script** to verify setup
5. **Test authentication flow** with real users
6. **Create AWS Cognito setup** for production (if needed)

---

## 9. Security Considerations
* **HTTPS everywhere** – OIDC requires secure redirect URIs.  
* **SameSite =Lax** cookies mitigate CSRF; state + nonce parameters mitigate replay.  
* **JWKS caching** with automatic key-rotation support.  
* **Token TTLs**: 15 min access tokens, 8 h refresh tokens (configurable via provider).  
* **Multi-Factor Authentication** and social logins are delegated to the provider.

---

## 10. Legacy Documentation
The old Traefik forward-auth approach has been superseded by this OIDC design and will be removed in a future release.  Refer to commit `abc1234` if you need the historical docs.

---

## 11. Implementation Priorities & Migration Steps

### Phase 1: Backend OIDC Foundation (Priority: High)
1. **Add OIDC dependencies** to `backend/requirements.txt`:
   ```
   pyjwt[crypto]==2.8.0
   cryptography==41.0.8
   httpx==0.25.2  # For JWKS fetching
   ```

2. **Create OIDC service** (`backend/app/services/oidc_auth.py`)
3. **Update configuration** (`backend/app/core/config.py`) with OIDC settings
4. **Modify dependencies** (`backend/app/api/deps.py`) to use OIDC instead of headers
5. **Add OIDC endpoints** (`backend/app/api/v1/endpoints/auth.py`)

### Phase 2: Frontend OIDC Integration (Priority: High)  
1. **Add OIDC dependencies** to `frontend/package.json`
2. **Create auth service** (`frontend/src/services/auth.ts`)
3. **Implement auth context** (`frontend/src/contexts/AuthContext.tsx`)
4. **Create auth components** (`frontend/src/components/Auth/`)
5. **Update App.tsx** with auth provider and protected routes

### Phase 3: Provider Configuration (Priority: Medium)
1. **Configure Authentik OIDC application** (development)
2. **Set up AWS Cognito User Pool** (production)
3. **Test provider switching** via environment variables
4. **Update Docker Compose** to remove Traefik forward-auth

### Phase 4: Migration & Testing (Priority: Medium)
1. **Backup current user data** before migration
2. **Test OIDC flow end-to-end** in development
3. **Verify token refresh mechanisms**
4. **Test anonymous access** still works for public content
5. **Update documentation** and remove legacy auth code

### Environment-Specific Configurations

#### Development (Authentik)
```bash
AUTH_PROVIDER=authentik
OIDC_ISSUER_URL=https://auth.storied-life.me/application/o/storied-life/
OIDC_CLIENT_ID=storied-life-web
OIDC_AUDIENCE=storied-life-api
```

#### Production (AWS Cognito)
```bash
AUTH_PROVIDER=cognito
OIDC_ISSUER_URL=https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEf123
OIDC_CLIENT_ID=1h57kf5cpq17m0eml12EXAMPLE
OIDC_AUDIENCE=storied-life-api
COGNITO_USER_POOL_ID=us-east-1_AbCdEf123
COGNITO_REGION=us-east-1
```

### Key Implementation Notes

1. **Backwards Compatibility**: Keep JWT fallback during transition period
2. **Anonymous Access**: Ensure public memorial content remains accessible
3. **Session Management**: Use secure HTTP-only cookies for web, Bearer tokens for API clients  
4. **Error Handling**: Graceful fallback when OIDC providers are unavailable
5. **Testing Strategy**: Mock OIDC responses for unit tests

---

> _"Every story matters. Every memory counts."_ – with secure, modern authentication, families can share those memories confidently. 