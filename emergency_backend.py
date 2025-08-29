#!/usr/bin/env python3
"""
Emergency Backend for AI Mini Games
Runs without Docker, PostgreSQL, or Redis
FOR DEVELOPMENT USE ONLY - Install Docker for full functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import uvicorn
import json

# Create FastAPI app
app = FastAPI(
    title="AI Mini Games API (Emergency Mode)",
    description="Emergency backend without database - Install Docker for full functionality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in emergency mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (will be lost on restart)
STORAGE = {
    "users": {},
    "games": {},
    "sessions": {}
}

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GameCreate(BaseModel):
    title: str
    description: Optional[str] = None
    game_type: str
    config: Dict = {}

class GameResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    game_type: str
    config: Dict
    created_at: str
    user_id: str

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "AI Mini Games API - Emergency Mode",
        "status": "running",
        "warning": "No database connected - data will be lost on restart",
        "solution": "Install Docker Desktop for full functionality"
    }

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": "development",
        "version": "1.0.0",
        "mode": "emergency",
        "storage": {
            "users": len(STORAGE["users"]),
            "games": len(STORAGE["games"]),
            "sessions": len(STORAGE["sessions"])
        }
    }

# Mobile version check
@app.get("/mobile/version")
def mobile_version():
    return {
        "min_version": "1.0.0",
        "latest_version": "1.0.0",
        "update_required": False,
        "update_url": None,
        "backend_mode": "emergency"
    }

# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=UserResponse)
def register(user: UserCreate):
    # Check if user exists
    if user.username in STORAGE["users"]:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user_id = f"user_{len(STORAGE['users']) + 1}"
    STORAGE["users"][user.username] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password": user.password,  # Note: In emergency mode, not hashing
        "created_at": datetime.now().isoformat()
    }
    
    return UserResponse(
        id=user_id,
        username=user.username,
        email=user.email
    )

@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    # Check user
    if request.username not in STORAGE["users"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = STORAGE["users"][request.username]
    if user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token (simplified)
    token = f"emergency_token_{request.username}_{datetime.now().timestamp()}"
    STORAGE["sessions"][token] = {
        "user_id": user["id"],
        "username": request.username,
        "created_at": datetime.now().isoformat()
    }
    
    return TokenResponse(access_token=token)

# Game endpoints
@app.get("/api/v1/games", response_model=List[GameResponse])
def list_games():
    games = []
    for game_id, game_data in STORAGE["games"].items():
        games.append(GameResponse(
            id=game_id,
            title=game_data["title"],
            description=game_data["description"],
            game_type=game_data["game_type"],
            config=game_data["config"],
            created_at=game_data["created_at"],
            user_id=game_data["user_id"]
        ))
    return games

@app.post("/api/v1/games", response_model=GameResponse)
def create_game(game: GameCreate):
    # Create game
    game_id = f"game_{len(STORAGE['games']) + 1}"
    game_data = {
        "id": game_id,
        "title": game.title,
        "description": game.description,
        "game_type": game.game_type,
        "config": game.config,
        "created_at": datetime.now().isoformat(),
        "user_id": "user_1"  # Default user in emergency mode
    }
    STORAGE["games"][game_id] = game_data
    
    return GameResponse(**game_data)

@app.get("/api/v1/games/{game_id}", response_model=GameResponse)
def get_game(game_id: str):
    if game_id not in STORAGE["games"]:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return GameResponse(**STORAGE["games"][game_id])

# User profile endpoint
@app.get("/api/v1/users/profile")
def get_profile():
    # Return mock profile in emergency mode
    return {
        "id": "user_1",
        "username": "test_user",
        "email": "test@example.com",
        "created_at": datetime.now().isoformat(),
        "warning": "Emergency mode - no persistent data"
    }

# AI generation endpoint (mock)
@app.post("/api/v1/ai/generate")
def generate_ai_content(prompt: str):
    return {
        "result": "AI generation not available in emergency mode",
        "prompt": prompt,
        "status": "mock",
        "message": "Install Docker and configure OpenAI API key for AI features"
    }

# Admin status endpoint
@app.get("/api/v1/admin/status")
def admin_status():
    return {
        "mode": "emergency",
        "docker_installed": False,
        "postgresql": "not available",
        "redis": "not available",
        "issues": [
            "Docker not installed",
            "No database connection",
            "No Redis cache",
            "Data not persistent"
        ],
        "resolution_steps": [
            "1. Install Docker Desktop from https://docker.com",
            "2. Start Docker Desktop",
            "3. Run: docker-compose up -d",
            "4. Verify: make health-check"
        ],
        "current_storage": STORAGE
    }

if __name__ == "__main__":
    print("=" * 60)
    print("AI MINI GAMES - EMERGENCY BACKEND")
    print("=" * 60)
    print("WARNING: Running without Docker, PostgreSQL, or Redis")
    print("Data will be lost when the server stops!")
    print()
    print("To install full infrastructure:")
    print("1. Install Docker Desktop: https://docker.com")
    print("2. Run: docker-compose up -d")
    print()
    print("API URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)