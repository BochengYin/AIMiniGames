# Implementation Guide - AI Mini Games Backend

## Quick Start Implementation

This guide provides step-by-step implementation details with code examples to get your AI Mini Games backend up and running quickly.

## Phase 1: Core Foundation Setup

### 1. Create the Core Application Structure

First, let's create the basic FastAPI application:

#### `app/main.py`
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.middleware.rate_limiting import RateLimitMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AI Mini Games API",
    description="Backend API for AI-powered mini game generator",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(RateLimitMiddleware)

# Include API router
app.include_router(api_router, prefix="/api")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Mini Games API...")
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

#### `app/core/config.py`
```python
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Mini Games API"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_VERSION: str = "v1"
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis
    REDIS_URL: str
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # AI Services
    OPENAI_API_KEY: str
    OPENAI_MAX_TOKENS: int = 4000
    AI_GENERATION_TIMEOUT: int = 120  # seconds
    
    # File Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "aimini-assets"
    S3_REGION: str = "us-east-1"
    CDN_BASE_URL: Optional[str] = None
    
    # Upload Limits
    MAX_GAME_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    MAX_ASSET_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Security
    ALLOWED_HOSTS: List[str] = ["*"]
    RATE_LIMIT_ENABLED: bool = True
    
    # Rate Limits (requests per minute)
    AI_GENERATION_RATE_LIMIT: int = 5
    API_RATE_LIMIT: int = 100
    UPLOAD_RATE_LIMIT: int = 10
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@aimini.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

#### `app/core/database.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Database dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 2. User Authentication System

#### `app/models/user.py`
```python
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class UserRole(enum.Enum):
    USER = "user"
    PREMIUM = "premium"
    MODERATOR = "moderator"
    ADMIN = "admin"

class UserStatus(enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)
    
    # Status and roles
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # AI Usage tracking
    ai_tokens_used = Column(Integer, default=0)
    ai_generations_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
```

#### `app/schemas/user.py`
```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: str
    role: UserRole
    status: UserStatus
    is_verified: bool
    is_premium: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    ai_generations_count: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
```

#### `app/core/security.py`
```python
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def verify_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    return token_data

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token_data = await verify_token(credentials.credentials)
    
    result = await db.execute(
        select(User).where(User.username == token_data.username)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user
```

### 3. Authentication Endpoints

#### `app/api/v1/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    create_refresh_token
)
from app.models.user import User, UserStatus
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.user_service import UserService

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    user_service = UserService(db)
    
    # Check if user exists
    if await user_service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if await user_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await user_service.create_user(user_data)
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user and return tokens"""
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Update last login
    await user_service.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        from jose import jwt, JWTError
        from app.core.config import settings
        
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Verify user exists
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user or user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": username})
        new_refresh_token = create_refresh_token(data={"sub": username})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

### 4. User Service Layer

#### `app/services/user_service.py`
```python
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
import uuid

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            password_hash=hashed_password,
            display_name=user_data.display_name or user_data.username
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.get_user_by_username(username.lower())
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**user_data.dict(exclude_unset=True))
            .returning(User)
        )
        
        updated_user = result.scalar_one_or_none()
        if updated_user:
            await self.db.commit()
        
        return updated_user
    
    async def update_last_login(self, user_id: uuid.UUID):
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.db.commit()
```

### 5. User Management Endpoints

#### `app/api/v1/users.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.services.asset_service import AssetService

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload user avatar"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    asset_service = AssetService()
    user_service = UserService(db)
    
    # Upload to storage
    avatar_url = await asset_service.upload_user_avatar(current_user.id, file)
    
    # Update user record
    await user_service.update_user(
        current_user.id, 
        UserUpdate(avatar_url=avatar_url)
    )
    
    return {"avatar_url": avatar_url}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (public profile)"""
    user_service = UserService(db)
    
    try:
        user = await user_service.get_user_by_id(uuid.UUID(user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
```

## Phase 2: Game Management System

### 1. Game Models

#### `app/models/game.py`
```python
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class GameCategory(enum.Enum):
    PUZZLE = "puzzle"
    ACTION = "action"
    STRATEGY = "strategy"
    ARCADE = "arcade"
    CARD = "card"
    WORD = "word"
    MATH = "math"
    TRIVIA = "trivia"

class GameDifficulty(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class GameStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    MODERATED = "moderated"
    DELETED = "deleted"

class Game(Base):
    __tablename__ = "games"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Basic info
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(GameCategory), nullable=False)
    difficulty = Column(Enum(GameDifficulty), default=GameDifficulty.MEDIUM)
    
    # Game data
    game_data = Column(JSONB, nullable=False)  # Generated game logic and configuration
    thumbnail_url = Column(String(500))
    assets_urls = Column(JSONB)  # URLs for game assets
    
    # Visibility and status
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    status = Column(Enum(GameStatus), default=GameStatus.ACTIVE)
    
    # Stats
    play_count = Column(Integer, default=0)
    rating = Column(DECIMAL(3,2), default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Search and discovery
    tags = Column(ARRAY(String))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", backref="created_games")
    
    def __repr__(self):
        return f"<Game(title='{self.title}', creator_id='{self.creator_id}')>"

class GameRating(Base):
    __tablename__ = "game_ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    game = relationship("Game", backref="ratings")
```

### 2. Game Schemas

#### `app/schemas/game.py`
```python
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.game import GameCategory, GameDifficulty, GameStatus

class GameBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: GameCategory
    difficulty: GameDifficulty = GameDifficulty.MEDIUM
    tags: Optional[List[str]] = []
    is_public: bool = True

class GameCreate(GameBase):
    game_data: Dict[str, Any]
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) < 3:
            raise ValueError('Title must be at least 3 characters')
        if len(v) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v

class GameUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[GameCategory] = None
    difficulty: Optional[GameDifficulty] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class GameResponse(GameBase):
    id: str
    creator_id: str
    creator_username: str
    thumbnail_url: Optional[str] = None
    status: GameStatus
    play_count: int
    rating: float
    rating_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class GameDetailResponse(GameResponse):
    game_data: Dict[str, Any]
    assets_urls: Optional[Dict[str, str]] = None

class GameListResponse(BaseModel):
    games: List[GameResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class GameRatingCreate(BaseModel):
    rating: int
    review: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class GameRatingResponse(BaseModel):
    id: str
    user_id: str
    username: str
    rating: int
    review: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

This implementation guide provides a solid foundation for your AI Mini Games backend. The architecture is designed to be:

1. **Scalable**: Using async/await, connection pooling, and proper database design
2. **Secure**: JWT authentication, input validation, and rate limiting
3. **Maintainable**: Clean separation of concerns with services, schemas, and models
4. **Production-ready**: Proper error handling, logging, and health checks

The next phases would cover AI integration, marketplace functionality, and multiplayer features. Each phase builds upon the previous one, allowing for iterative development that matches your 10 hours/week timeline.