#!/usr/bin/env python3
"""
Minimal Backend Runner - Works without Docker
Uses SQLite instead of PostgreSQL and in-memory cache instead of Redis
FOR DEVELOPMENT TESTING ONLY
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def create_minimal_env():
    """Create minimal environment configuration"""
    
    # Create .env.minimal file with SQLite configuration
    env_content = """# Minimal Development Environment
DATABASE_URL=sqlite:///./aimini.db
REDIS_URL=memory://
SECRET_KEY=dev-secret-key-not-for-production
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://localhost:19006"]
API_BASE_URL=http://localhost:8000
"""
    
    with open('.env.minimal', 'w') as f:
        f.write(env_content)
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///./aimini.db'
    os.environ['REDIS_URL'] = 'memory://'
    os.environ['SECRET_KEY'] = 'dev-secret-key-not-for-production'
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['DEBUG'] = 'true'
    
    print("✓ Minimal environment configured")

def check_dependencies():
    """Check and install required Python packages"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'python-jose',
        'passlib',
        'python-multipart',
        'aiofiles'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
    
    print("✓ All dependencies available")

def create_sqlite_tables():
    """Create basic SQLite tables for testing"""
    conn = sqlite3.connect('aimini.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            user_id INTEGER,
            game_type TEXT,
            config TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ SQLite database initialized")

def create_minimal_api():
    """Create a minimal FastAPI app for testing"""
    
    # Create minimal main.py if the main app doesn't work
    minimal_api = '''
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
'''
    
    with open('minimal_api.py', 'w') as f:
        f.write(minimal_api)
    
    print("✓ Minimal API created")

def main():
    print("=" * 50)
    print("AI Mini Games - Minimal Backend Runner")
    print("FOR DEVELOPMENT TESTING ONLY")
    print("=" * 50)
    
    # Setup minimal environment
    print("\n1. Setting up minimal environment...")
    create_minimal_env()
    
    # Check dependencies
    print("\n2. Checking dependencies...")
    check_dependencies()
    
    # Initialize SQLite database
    print("\n3. Initializing SQLite database...")
    create_sqlite_tables()
    
    # Create minimal API if needed
    print("\n4. Creating minimal API...")
    create_minimal_api()
    
    # Update coordination status
    print("\n5. Updating coordination status...")
    coord_file = Path("coordination.json")
    if coord_file.exists():
        with open(coord_file, 'r') as f:
            data = json.load(f)
        
        data['infrastructure_status'] = {
            'docker_available': False,
            'services_running': ['SQLite (local)', 'In-Memory Cache', 'FastAPI (minimal mode)'],
            'issues': ['Running in minimal mode without Docker'],
            'mode': 'minimal',
            'api_url': 'http://localhost:8000'
        }
        
        with open(coord_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("✓ Updated coordination.json")
    
    # Start the minimal API
    print("\n" + "=" * 50)
    print("Starting Minimal API Server...")
    print("API URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("=" * 50 + "\n")
    
    try:
        import uvicorn
        # Try to import the main app first
        try:
            from app.main import app
            print("Using main application...")
            uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
        except Exception as e:
            print(f"Main app failed: {e}")
            print("Using minimal API...")
            from minimal_api import app
            uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Please install: pip install uvicorn fastapi")
        sys.exit(1)

if __name__ == "__main__":
    main()