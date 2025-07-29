#!/usr/bin/env python3
"""
OIDC Configuration Validation Script for Storied Life

This script validates the OIDC configuration and connectivity to Authentik/Cognito.
Run this script to quickly check if your authentication setup is correct.

Usage:
    python scripts/validate_oidc_config.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import json
from typing import Dict, Any, List
from app.core.config import settings


class ConfigValidator:
    """Validates OIDC configuration and connectivity."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def log_error(self, message: str):
        """Log an error message."""
        self.errors.append(f"❌ ERROR: {message}")
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.warnings.append(f"⚠️  WARNING: {message}")
    
    def log_info(self, message: str):
        """Log an info message."""
        self.info.append(f"ℹ️  INFO: {message}")
    
    def log_success(self, message: str):
        """Log a success message."""
        self.info.append(f"✅ SUCCESS: {message}")
    
    def validate_environment_variables(self):
        """Validate required environment variables."""
        print("🔍 Validating environment variables...")
        
        required_vars = {
            'AUTH_PROVIDER': 'Authentication provider (authentik or cognito)',
            'OIDC_ISSUER_URL': 'OIDC issuer URL',
            'OIDC_CLIENT_ID': 'OIDC client ID',
            'OIDC_AUDIENCE': 'OIDC audience'
        }
        
        for var, description in required_vars.items():
            value = getattr(settings, var, None)
            if not value:
                self.log_error(f"{var} is not set - {description}")
            elif not value.strip():
                self.log_error(f"{var} is empty - {description}")
            else:
                self.log_success(f"{var} is configured")
        
        # Provider-specific validation
        if settings.AUTH_PROVIDER == "cognito":
            if not settings.COGNITO_USER_POOL_ID:
                self.log_error("COGNITO_USER_POOL_ID is required for Cognito provider")
            if not settings.COGNITO_REGION:
                self.log_error("COGNITO_REGION is required for Cognito provider")
        elif settings.AUTH_PROVIDER == "authentik":
            if not settings.AUTHENTIK_HOST:
                self.log_warning("AUTHENTIK_HOST is not set (optional)")
        
        # URL validation
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(settings.OIDC_ISSUER_URL)
            if parsed.scheme not in ['http', 'https']:
                self.log_error("OIDC_ISSUER_URL must use http or https scheme")
            elif not parsed.netloc:
                self.log_error("OIDC_ISSUER_URL must have a valid host")
            else:
                self.log_success("OIDC_ISSUER_URL format is valid")
                
                if settings.AUTH_PROVIDER == "cognito" and parsed.scheme != "https":
                    self.log_error("Cognito requires HTTPS URLs")
        except Exception as e:
            self.log_error(f"Invalid OIDC_ISSUER_URL: {e}")
    
    async def validate_oidc_discovery(self):
        """Validate OIDC discovery endpoint."""
        print("🔍 Validating OIDC discovery endpoint...")
        
        discovery_url = f"{settings.OIDC_ISSUER_URL.rstrip('/')}/.well-known/openid-configuration"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(discovery_url)
                
                if response.status_code == 200:
                    self.log_success("OIDC discovery endpoint is accessible")
                    
                    try:
                        config = response.json()
                        self.validate_oidc_config(config)
                        return config
                    except json.JSONDecodeError:
                        self.log_error("OIDC discovery response is not valid JSON")
                else:
                    self.log_error(f"OIDC discovery endpoint returned {response.status_code}")
                    self.log_info(f"Response: {response.text[:200]}...")
        
        except httpx.TimeoutException:
            self.log_error("Timeout connecting to OIDC discovery endpoint")
        except httpx.RequestError as e:
            self.log_error(f"Failed to connect to OIDC discovery endpoint: {e}")
        
        return None
    
    def validate_oidc_config(self, config: Dict[str, Any]):
        """Validate OIDC configuration from discovery."""
        required_fields = [
            'issuer',
            'authorization_endpoint',
            'token_endpoint',
            'jwks_uri'
        ]
        
        for field in required_fields:
            if field in config:
                self.log_success(f"OIDC config has {field}")
            else:
                self.log_error(f"OIDC config missing required field: {field}")
        
        # Validate issuer matches our configuration
        if config.get('issuer') != settings.OIDC_ISSUER_URL.rstrip('/'):
            self.log_warning(f"Issuer mismatch: config={config.get('issuer')}, expected={settings.OIDC_ISSUER_URL.rstrip('/')}")
        
        # Check supported features
        if 'code_challenge_methods_supported' in config:
            methods = config['code_challenge_methods_supported']
            if 'S256' in methods:
                self.log_success("PKCE with S256 is supported")
            else:
                self.log_warning("PKCE S256 method not explicitly supported")
        
        if 'scopes_supported' in config:
            required_scopes = ['openid', 'profile', 'email']
            supported_scopes = config['scopes_supported']
            for scope in required_scopes:
                if scope in supported_scopes:
                    self.log_success(f"Required scope '{scope}' is supported")
                else:
                    self.log_warning(f"Required scope '{scope}' may not be supported")
    
    async def validate_jwks_endpoint(self, jwks_uri: str = None):
        """Validate JWKS endpoint."""
        print("🔍 Validating JWKS endpoint...")
        
        if not jwks_uri:
            jwks_uri = f"{settings.OIDC_ISSUER_URL.rstrip('/')}/.well-known/jwks.json"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(jwks_uri)
                
                if response.status_code == 200:
                    self.log_success("JWKS endpoint is accessible")
                    
                    try:
                        jwks = response.json()
                        self.validate_jwks(jwks)
                    except json.JSONDecodeError:
                        self.log_error("JWKS response is not valid JSON")
                else:
                    self.log_error(f"JWKS endpoint returned {response.status_code}")
        
        except httpx.TimeoutException:
            self.log_error("Timeout connecting to JWKS endpoint")
        except httpx.RequestError as e:
            self.log_error(f"Failed to connect to JWKS endpoint: {e}")
    
    def validate_jwks(self, jwks: Dict[str, Any]):
        """Validate JWKS structure."""
        if 'keys' not in jwks:
            self.log_error("JWKS missing 'keys' field")
            return
        
        keys = jwks['keys']
        if not keys:
            self.log_error("JWKS has no keys")
            return
        
        self.log_success(f"JWKS contains {len(keys)} key(s)")
        
        for i, key in enumerate(keys):
            required_fields = ['kty', 'kid']
            for field in required_fields:
                if field not in key:
                    self.log_error(f"JWKS key {i} missing required field: {field}")
            
            if 'use' not in key and 'key_ops' not in key:
                self.log_warning(f"JWKS key {i} missing 'use' or 'key_ops' field")
    
    def validate_authentik_specific(self):
        """Validate Authentik-specific configuration."""
        if settings.AUTH_PROVIDER != "authentik":
            return
        
        print("🔍 Validating Authentik-specific configuration...")
        
        # Check if issuer URL looks like Authentik
        if "/application/o/" in settings.OIDC_ISSUER_URL:
            self.log_success("OIDC issuer URL matches Authentik pattern")
        else:
            self.log_warning("OIDC issuer URL doesn't match typical Authentik pattern (/application/o/)")
        
        # Validate expected claims for Authentik
        expected_groups = ["storied-life-admins", "storied-life-users"]
        self.log_info(f"Expected admin groups for Authentik: {expected_groups}")
    
    def validate_cognito_specific(self):
        """Validate Cognito-specific configuration."""
        if settings.AUTH_PROVIDER != "cognito":
            return
        
        print("🔍 Validating Cognito-specific configuration...")
        
        # Check if issuer URL looks like Cognito
        if "cognito-idp" in settings.OIDC_ISSUER_URL:
            self.log_success("OIDC issuer URL matches Cognito pattern")
        else:
            self.log_warning("OIDC issuer URL doesn't match typical Cognito pattern")
        
        # Validate region and user pool ID
        if settings.COGNITO_REGION and settings.COGNITO_USER_POOL_ID:
            expected_issuer = f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}"
            if expected_issuer == settings.OIDC_ISSUER_URL.rstrip('/'):
                self.log_success("Cognito issuer URL matches region and user pool ID")
            else:
                self.log_warning(f"Expected issuer: {expected_issuer}")
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("📋 VALIDATION SUMMARY")
        print("="*60)
        
        if self.info:
            for msg in self.info:
                print(msg)
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for msg in self.warnings:
                print(msg)
        
        if self.errors:
            print("\n❌ ERRORS:")
            for msg in self.errors:
                print(msg)
        
        print(f"\n📊 RESULTS: {len(self.info)} info, {len(self.warnings)} warnings, {len(self.errors)} errors")
        
        if self.errors:
            print("\n🚨 Configuration has errors that need to be fixed!")
            return False
        elif self.warnings:
            print("\n⚠️  Configuration has warnings but should work.")
            return True
        else:
            print("\n🎉 Configuration looks good!")
            return True


async def main():
    """Main validation function."""
    print("🚀 Storied Life OIDC Configuration Validator")
    print("="*50)
    
    validator = ConfigValidator()
    
    # Current configuration
    print(f"📋 Current Configuration:")
    print(f"   Provider: {settings.AUTH_PROVIDER}")
    print(f"   Issuer: {settings.OIDC_ISSUER_URL}")
    print(f"   Client ID: {settings.OIDC_CLIENT_ID}")
    print(f"   Audience: {settings.OIDC_AUDIENCE}")
    print()
    
    # Run validations
    validator.validate_environment_variables()
    
    oidc_config = await validator.validate_oidc_discovery()
    
    if oidc_config and 'jwks_uri' in oidc_config:
        await validator.validate_jwks_endpoint(oidc_config['jwks_uri'])
    else:
        await validator.validate_jwks_endpoint()
    
    validator.validate_authentik_specific()
    validator.validate_cognito_specific()
    
    # Print summary
    success = validator.print_summary()
    
    # Provide next steps
    if not success:
        print("\n🔧 NEXT STEPS:")
        print("1. Fix the configuration errors listed above")
        print("2. Check your Authentik/Cognito application settings")
        print("3. Verify network connectivity to the OIDC provider")
        print("4. Run this script again to validate fixes")
        sys.exit(1)
    else:
        print("\n🎯 NEXT STEPS:")
        print("1. Run the full test suite: pytest backend/tests/test_oidc_auth.py")
        print("2. Test the complete authentication flow with a real user")
        print("3. Monitor logs during authentication for any issues")


if __name__ == "__main__":
    asyncio.run(main()) 