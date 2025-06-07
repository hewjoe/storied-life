"""
Configuration settings for Storied Life backend.
"""

from typing import List, Optional, Any
from pydantic_settings import BaseSettings
from pydantic import validator
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Basic configuration
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Storied Life"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://vision.projecthewitt.info:3001",
        "http://vision.projecthewitt.info:8000",
        "http://vision.projecthewitt.info:8001",
        "http://localhost:5173",
    ]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Security settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database configuration
    DATABASE_URL: str = "postgresql://storied:password@localhost:5432/storied_life"
    
    # Neo4J configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI configuration
    LITELLM_URL: str = "http://localhost:4000"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Storage configuration
    STORAGE_TYPE: str = "local"  # "local" or "s3"
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    
    # Email configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "Storied Life"
    
    # Authentication
    AUTHELIA_URL: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"  # JWT algorithm
    
    # Feature flags
    FEATURE_SMS_INTEGRATION: bool = False
    FEATURE_SOCIAL_IMPORT: bool = False
    FEATURE_VOICE_SYNTHESIS: bool = False
    FEATURE_MULTI_TENANT: bool = False
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings() 