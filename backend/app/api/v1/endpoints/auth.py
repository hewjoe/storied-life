"""
Authentication API endpoints.
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jwt import PyJWTError

from app.api.deps import get_db, require_authenticated_user, get_current_user_optional, get_oidc_authenticator
from app.models.user import User, UserRole
from app.schemas.auth import Token, OIDCConfig, AuthCallbackRequest, AuthStatus
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.oidc_auth import OIDCAuthenticator

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_authenticated_user)
) -> Any:
    """
    Get current user information.
    """
    return UserResponse.from_orm(current_user)


@router.get("/status")
async def auth_status(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    oidc_auth: OIDCAuthenticator = Depends(get_oidc_authenticator)
) -> Any:
    """
    Get authentication status.
    Shows whether user is authenticated and via what method.
    """
    # Check for different authentication methods
    authentik_email = request.headers.get("X-authentik-email")
    access_token_cookie = request.cookies.get("access_token")
    auth_header = request.headers.get("authorization")
    
    auth_method = None
    if current_user:
        if access_token_cookie:
            auth_method = f"oidc_cookie_{oidc_auth.provider}"
        elif auth_header and auth_header.startswith("Bearer "):
            # Try to determine if it's OIDC or legacy JWT
            try:
                token = auth_header.split(" ")[1]
                await oidc_auth.verify_token(token)
                auth_method = f"oidc_bearer_{oidc_auth.provider}"
            except:
                auth_method = "legacy_jwt"
        elif authentik_email:
            auth_method = "legacy_authentik_headers"
        else:
            auth_method = "unknown"
    
    if current_user:
        return {
            "authenticated": True,
            "user": UserResponse.from_orm(current_user),
            "auth_method": auth_method,
            "provider": oidc_auth.provider,
            "oidc_enabled": True,
            "legacy_authentik_headers": bool(authentik_email)
        }
    else:
        return {
            "authenticated": False,
            "user": None,
            "auth_method": None,
            "provider": oidc_auth.provider,
            "oidc_enabled": True,
            "legacy_authentik_headers": bool(authentik_email)
        }


# Legacy password-based authentication endpoints - disabled for OIDC
# @router.post("/login", response_model=Token)
# @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# These endpoints are not compatible with OIDC-only authentication


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token.
    """
    auth_service = AuthService(db)
    
    access_token = auth_service.create_access_token(subject=str(current_user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(require_authenticated_user),
    oidc_auth: OIDCAuthenticator = Depends(get_oidc_authenticator)
) -> Any:
    """
    Logout current user.
    Clears session cookies and returns provider logout URL if applicable.
    """
    # Clear the access token cookie
    response.delete_cookie(
        key="access_token",
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="lax"
    )
    
    # Get provider logout URL
    logout_url = None
    if oidc_auth.provider == "authentik":
        logout_url = f"{oidc_auth.issuer_url.rstrip('/')}/end-session/"
    elif oidc_auth.provider == "cognito":
        logout_url = f"{oidc_auth.issuer_url.rstrip('/')}/logout"
    
    return {
        "message": "Successfully logged out",
        "logout_url": logout_url
    }


@router.get("/oidc-config")
async def get_oidc_config(
    oidc_auth: OIDCAuthenticator = Depends(get_oidc_authenticator)
) -> Any:
    """
    Get OIDC configuration for frontend.
    Returns the necessary configuration for the OIDC client.
    """
    return await oidc_auth.get_oidc_config()


@router.post("/sync-oidc-session")
async def sync_oidc_session(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    oidc_auth: OIDCAuthenticator = Depends(get_oidc_authenticator)
) -> Any:
    """
    Sync OIDC session from frontend to backend.
    Used when the frontend handles the OIDC callback directly and needs to 
    establish a server-side session with the tokens.
    """
    try:
        # Get the access token from Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token required"
            )
        
        access_token = auth_header.split(" ")[1]
        
        # Get request body for additional token info
        body = await request.json()
        refresh_token = body.get("refresh_token")
        expires_in = body.get("expires_in", 3600)
        
        # Verify the token and get user
        try:
            user = await oidc_auth.get_user_from_token(access_token, db)
        except Exception as e:
            print(f"DEBUG: Token verification failed with error: {str(e)}")
            print(f"DEBUG: Exception type: {type(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
        
        # Set secure HTTP-only cookie with access token
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=expires_in,
            path="/",
            domain=None,
            secure=True,
            httponly=True,
            samesite="lax"
        )
        
        # Optionally store refresh token if provided
        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=expires_in * 24,  # Refresh tokens typically last longer
                path="/",
                domain=None,
                secure=True,
                httponly=True,
                samesite="lax"
            )
        
        return {
            "message": "Session synchronized successfully",
            "user": UserResponse.from_orm(user),
            "expires_in": expires_in
        }
        
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session sync failed: {str(e)}"
        )


@router.post("/callback")
async def oidc_callback(
    response: Response,
    code: str = Form(...),
    state: str = Form(...),
    code_verifier: str = Form(...),
    db: Session = Depends(get_db),
    oidc_auth: OIDCAuthenticator = Depends(get_oidc_authenticator)
) -> Any:
    """
    Handle OIDC authorization code callback.
    Exchanges the authorization code for tokens and creates/updates user.
    """
    try:
        # Exchange code for tokens
        token_data = await oidc_auth.exchange_code_for_tokens(code, state, code_verifier)
        
        # Get user from access token
        access_token = token_data["access_token"]
        user = await oidc_auth.get_user_from_token(access_token, db)
        
        # Set secure HTTP-only cookie with access token
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=token_data.get("expires_in", 3600),
            path="/",
            domain=None,
            secure=True,
            httponly=True,
            samesite="lax"
        )
        
        return {
            "message": "Login successful",
            "user": UserResponse.from_orm(user),
            "expires_in": token_data.get("expires_in", 3600)
        }
        
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/debug/config")
async def debug_config(
    oidc_auth: OIDCAuthenticator = Depends(get_oidc_authenticator)
) -> Any:
    """
    Debug endpoint to check OIDC configuration.
    Only available in DEBUG mode.
    """
    import os
    if not os.getenv("DEBUG", "false").lower() == "true":
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "provider": oidc_auth.provider,
        "issuer_url": oidc_auth.issuer_url,
        "client_id": oidc_auth.client_id,
        "audience": oidc_auth.audience,
        "jwks_uri": oidc_auth.jwks_client.uri if hasattr(oidc_auth.jwks_client, 'uri') else "unknown"
    }