"""
Main API v1 Router
Includes all feature-specific routers
"""

from fastapi import APIRouter

from app.features.auth.routes import router as auth_router
from app.features.games.routes import router as games_router
from app.features.ai_generation.routes import router as ai_router
from app.features.marketplace.routes import router as marketplace_router
from app.features.multiplayer.routes import router as multiplayer_router
from app.features.users.routes import router as users_router

api_router = APIRouter()

# Include all feature routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(games_router, prefix="/games", tags=["Games"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Generation"])
api_router.include_router(marketplace_router, prefix="/marketplace", tags=["Marketplace"])
api_router.include_router(multiplayer_router, prefix="/multiplayer", tags=["Multiplayer"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])