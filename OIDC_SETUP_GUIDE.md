# Authentik OIDC Provider Setup Guide

## Issue
The "Sign In with Authentik" button is not clickable because the OIDC provider application is not configured in Authentik.

## Solution
You need to create an OIDC provider application in Authentik with the slug `storied-life-oidc`.

## Steps to Configure Authentik OIDC Provider

### 1. Access Authentik Admin Interface
- Navigate to: https://auth.storied-life.me/if/admin/
- Login with admin credentials

### 2. Create OAuth2/OpenID Provider
1. Go to **Applications → Providers**
2. Click **Create** → Select **OAuth2/OpenID Provider**
3. Configure the provider with these settings:

```
Name: Storied Life OIDC
Authorization flow: default-authorization-flow (Built-in)
Client type: Public
Client ID: XpMZJMaaAG6OUjJPr2CBho13aJp5Vzik9CWYRmSD
Client Secret: (leave empty for public client)

Redirect URIs:
- https://remember.storied-life.me/login/callback
- http://localhost:3000/login/callback (for local development)

Signing Key: authentik Self-signed Certificate (or create a new one)

Advanced settings:
- Include claims in id_token: ✓
- Issuer mode: Per Provider
- Subject mode: User UUID

Scopes:
- openid (required)
- profile (required) 
- email (required)
- offline_access (for refresh tokens)
```

### 3. Create Application
1. Go to **Applications → Applications**
2. Click **Create**
3. Configure the application:

```
Name: Storied Life
Slug: storied-life-oidc
Provider: (select the provider created above)
```

### 4. Verify Configuration
After creating the provider and application, verify:

1. The discovery endpoint should be accessible:
   ```
   https://auth.storied-life.me/application/o/storied-life-oidc/.well-known/openid-configuration
   ```

2. Run the backend validation script:
   ```bash
   docker exec storied-life-dev-backend python scripts/validate_oidc_config.py
   ```

3. Test the authorization endpoint:
   ```
   https://auth.storied-life.me/application/o/storied-life-oidc/authorize
   ```

### 5. Test the Login Flow
1. Refresh the Storied Life application: https://remember.storied-life.me
2. Click the "Sign In with Authentik" button
3. You should be redirected to Authentik for authentication

## Current Configuration Status

- ✅ Backend OIDC settings are correct
- ✅ Frontend authentication code is implemented
- ✅ Environment variables are configured properly
- ❌ **Authentik OIDC provider needs to be created** (this is the missing step)

## Environment Variables Reference

The application is configured with these OIDC settings (in `.env.dev`):

```bash
AUTH_PROVIDER=authentik
OIDC_ISSUER_URL=https://auth.storied-life.me/application/o/storied-life-oidc/
OIDC_CLIENT_ID=XpMZJMaaAG6OUjJPr2CBho13aJp5Vzik9CWYRmSD
OIDC_AUDIENCE=storied-life-api
OIDC_SCOPES=openid profile email offline_access
```

These match what needs to be configured in Authentik.
