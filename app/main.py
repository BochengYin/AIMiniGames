"""
AI Mini Games - FastAPI Backend
Main application entry point with enhanced mobile support
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.redis_client import init_redis, close_redis
from app.api.v1.router import api_router
from app.api.middleware.error_handler import ErrorHandlerMiddleware
from app.api.middleware.rate_limiter import RateLimitMiddleware
from app.websocket.manager import WebSocketManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    await init_redis()
    
    # Initialize WebSocket manager
    app.state.websocket_manager = WebSocketManager()
    
    print("🚀 AI Mini Games Backend Started")
    print(f"📱 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"🌐 API Base URL: {settings.API_BASE_URL}")
    
    yield
    
    # Shutdown
    await close_database()
    await close_redis()
    print("👋 AI Mini Games Backend Stopped")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="AI Mini Games API",
        description="Backend API for AI-powered mini games platform",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Add security middleware
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )
    
    # CORS middleware for mobile apps
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middleware
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0"
        }
    
    # Mobile app version endpoint
    @app.get("/mobile/version")
    async def mobile_version():
        return {
            "min_version": "1.0.0",
            "latest_version": "1.0.0",
            "update_required": False,
            "update_url": None
        }
    
    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )