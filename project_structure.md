# AIMiniGames - Project Structure

## Recommended Directory Structure

```
AIMiniGames/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   ├── security.py         # JWT and authentication utilities
│   │   ├── database.py         # Database connection and session
│   │   └── exceptions.py       # Custom exception handlers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # User database model
│   │   ├── game.py            # Game database model
│   │   ├── marketplace.py     # Marketplace models
│   │   ├── multiplayer.py     # Multiplayer session models
│   │   └── ai_generation.py   # AI generation tracking models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # User Pydantic schemas
│   │   ├── game.py            # Game Pydantic schemas
│   │   ├── marketplace.py     # Marketplace schemas
│   │   ├── multiplayer.py     # Multiplayer schemas
│   │   └── ai_generation.py   # AI generation schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py    # Common API dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── users.py       # User management endpoints
│   │       ├── games.py       # Game CRUD endpoints
│   │       ├── marketplace.py # Marketplace endpoints
│   │       ├── multiplayer.py # Multiplayer endpoints
│   │       └── ai.py          # AI generation endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Authentication business logic
│   │   ├── game_service.py    # Game management logic
│   │   ├── ai_service.py      # AI integration service
│   │   ├── asset_service.py   # File and asset management
│   │   ├── multiplayer_service.py # Multiplayer session logic
│   │   └── moderation_service.py # Content moderation
│   ├── websocket/
│   │   ├── __init__.py
│   │   ├── manager.py         # WebSocket connection manager
│   │   ├── multiplayer.py     # Multiplayer WebSocket handlers
│   │   └── notifications.py   # Notification WebSocket handlers
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery configuration
│   │   ├── ai_tasks.py        # AI generation background tasks
│   │   └── moderation_tasks.py # Content moderation tasks
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py      # Custom validation functions
│   │   ├── helpers.py         # Helper functions
│   │   └── constants.py       # Application constants
│   └── middleware/
│       ├── __init__.py
│       ├── rate_limiting.py   # Rate limiting middleware
│       ├── cors.py            # CORS configuration
│       └── logging.py         # Request logging middleware
├── migrations/                 # Alembic database migrations
│   ├── versions/
│   ├── alembic.ini
│   └── env.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration
│   ├── test_auth.py           # Authentication tests
│   ├── test_games.py          # Game functionality tests
│   ├── test_ai.py             # AI service tests
│   └── test_multiplayer.py    # Multiplayer tests
├── docker/
│   ├── Dockerfile             # Main application container
│   ├── Dockerfile.celery      # Celery worker container
│   └── docker-compose.yml     # Development environment
├── scripts/
│   ├── init_db.py            # Database initialization
│   ├── seed_data.py          # Test data seeding
│   └── deploy.sh             # Deployment script
├── docs/                      # Additional documentation
│   ├── api_documentation.md
│   └── deployment_guide.md
├── .env.example               # Environment variables template
├── .gitignore
├── requirements.txt           # Python dependencies
├── backend_architecture.md    # This architecture document
└── README.md                  # Project overview
```

## Key Files Description

### Core Application Files

#### `app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, games, marketplace, multiplayer, ai
from app.websocket import multiplayer_ws, notifications_ws

app = FastAPI(
    title="AI Mini Games API",
    description="Backend API for AI-powered mini game generator",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(games.router, prefix="/api/v1/games", tags=["games"])
app.include_router(marketplace.router, prefix="/api/v1/marketplace", tags=["marketplace"])
app.include_router(multiplayer.router, prefix="/api/v1/multiplayer", tags=["multiplayer"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])

# WebSocket endpoints
app.include_router(multiplayer_ws.router, prefix="/ws")
app.include_router(notifications_ws.router, prefix="/ws")
```

#### `app/core/config.py`
```python
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # AI Services
    OPENAI_API_KEY: str
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "aimini-assets"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Development Environment Setup

#### `.env.example`
```bash
# Database Configuration
DATABASE_URL=postgresql://aimini_user:password@localhost:5432/aimini_db
REDIS_URL=redis://localhost:6379

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# AI Service Keys
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_API_KEY=your-huggingface-key

# AWS/S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=aimini-assets

# Application Settings
ENVIRONMENT=development
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: aimini_db
      POSTGRES_USER: aimini_user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://aimini_user:password@db:5432/aimini_db
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=dev-secret-key
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://aimini_user:password@db:5432/aimini_db
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - .:/app

  flower:
    build: .
    command: celery -A app.tasks.celery_app flower
    ports:
      - "5555:5555"
    environment:
      - DATABASE_URL=postgresql://aimini_user:password@db:5432/aimini_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

volumes:
  postgres_data:
```

## Development Workflow

### 1. Initial Setup
```bash
# Clone and setup
git clone <repository>
cd AIMiniGames

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your actual values

# Start services
docker-compose up -d db redis

# Initialize database
python scripts/init_db.py

# Run migrations
alembic upgrade head
```

### 2. Development Commands
```bash
# Start development server
uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Start Celery Flower (monitoring)
celery -A app.tasks.celery_app flower

# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/
```

### 3. Database Operations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Seed test data
python scripts/seed_data.py
```

This structure provides a solid foundation for your AI mini games backend, with clear separation of concerns and scalable architecture patterns.