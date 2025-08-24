"""
Configuration settings for AI Mini Games Backend
Enhanced for mobile app support
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # API Configuration
    API_BASE_URL: str = "http://localhost:8000"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # CORS for mobile apps
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Web development
        "capacitor://localhost",  # Capacitor apps
        "ionic://localhost",      # Ionic apps
        "http://localhost",       # Generic localhost
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://aimini:aimini@localhost:5432/aimini_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    HUGGING_FACE_API_KEY: Optional[str] = None
    AI_GENERATION_TIMEOUT_MINUTES: int = 30
    MAX_CONCURRENT_GENERATIONS: int = 10
    
    # File Storage (S3 or local)
    USE_S3_STORAGE: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET_NAME: Optional[str] = None
    AWS_S3_REGION: str = "us-east-1"
    LOCAL_STORAGE_PATH: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50
    
    # WebSocket
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    MAX_WEBSOCKET_CONNECTIONS: int = 1000
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST_SIZE: int = 100
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Mobile App Settings
    MOBILE_MIN_VERSION: str = "1.0.0"
    MOBILE_LATEST_VERSION: str = "1.0.0"
    FORCE_UPDATE_BELOW_VERSION: Optional[str] = None
    
    # Game Settings
    MAX_GAMES_PER_USER: int = 100
    MAX_GAME_FILE_SIZE_MB: int = 10
    ALLOWED_GAME_FORMATS: List[str] = ["json", "js", "html"]
    
    # Marketplace
    MARKETPLACE_COMMISSION_PERCENTAGE: float = 30.0
    MIN_GAME_PRICE: float = 0.99
    MAX_GAME_PRICE: float = 99.99
    
    # Multiplayer
    MAX_PLAYERS_PER_SESSION: int = 4
    SESSION_TIMEOUT_MINUTES: int = 30
    MATCHMAKING_TIMEOUT_SECONDS: int = 60
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v
    
    @validator("DEBUG")
    def set_debug_based_on_environment(cls, v, values):
        if values.get("ENVIRONMENT") == "production":
            return False
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Environment-specific configurations
def get_database_url() -> str:
    """Get database URL with proper SSL settings for production"""
    url = settings.DATABASE_URL
    if settings.ENVIRONMENT == "production" and "sslmode" not in url:
        url += "?sslmode=require"
    return url


def get_cors_origins() -> List[str]:
    """Get CORS origins including mobile-specific origins"""
    origins = settings.CORS_ORIGINS.copy()
    
    if settings.ENVIRONMENT == "development":
        # Add development-specific origins
        origins.extend([
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ])
    
    return origins


def is_production() -> bool:
    """Check if running in production environment"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """Check if running in development environment"""
    return settings.ENVIRONMENT == "development"