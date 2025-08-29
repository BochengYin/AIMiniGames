
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import json
from datetime import datetime

app = FastAPI(
    title="AI Mini Games API (Minimal)",
    description="Minimal backend for development without Docker",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class GameCreate(BaseModel):
    title: str
    description: Optional[str]
    game_type: str
    config: dict

class GameResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    game_type: str
    config: dict
    created_at: str

# Routes
@app.get("/")
def read_root():
    return {
        "message": "AI Mini Games API (Minimal Mode)",
        "status": "running",
        "mode": "minimal (SQLite + In-Memory Cache)"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": "development",
        "version": "1.0.0",
        "mode": "minimal"
    }

@app.post("/api/v1/auth/register", response_model=UserResponse)
def register(user: UserCreate):
    conn = sqlite3.connect("aimini.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (user.username, user.email, f"hashed_{user.password}")
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        return UserResponse(
            id=user_id,
            username=user.username,
            email=user.email
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()

@app.post("/api/v1/auth/login")
def login(username: str, password: str):
    # Minimal login implementation
    return {
        "access_token": "minimal_test_token",
        "token_type": "bearer"
    }

@app.get("/api/v1/games", response_model=List[GameResponse])
def list_games():
    conn = sqlite3.connect("aimini.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM games ORDER BY created_at DESC")
    games = cursor.fetchall()
    conn.close()
    
    result = []
    for game in games:
        result.append(GameResponse(
            id=game[0],
            title=game[1],
            description=game[2],
            game_type=game[4],
            config=json.loads(game[5]) if game[5] else {},
            created_at=game[6]
        ))
    
    return result

@app.post("/api/v1/games", response_model=GameResponse)
def create_game(game: GameCreate):
    conn = sqlite3.connect("aimini.db")
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO games (title, description, game_type, config, user_id) VALUES (?, ?, ?, ?, ?)",
        (game.title, game.description, game.game_type, json.dumps(game.config), 1)
    )
    conn.commit()
    game_id = cursor.lastrowid
    
    conn.close()
    
    return GameResponse(
        id=game_id,
        title=game.title,
        description=game.description,
        game_type=game.game_type,
        config=game.config,
        created_at=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
