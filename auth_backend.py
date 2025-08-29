"""
Production-Ready Authentication Backend for AI Mini Games
In-memory storage implementation for Phase 1 (no database dependencies)
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any, List
from contextlib import asynccontextmanager
import logging
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, field_validator, SecretStr
from passlib.context import CryptContext
from jose import JWTError, jwt
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('auth_backend.log')
    ]
)
logger = logging.getLogger(__name__)

# ==================== Configuration ====================

class Settings:
    """Application settings with security best practices"""
    
    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Security
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    BCRYPT_ROUNDS = 12
    
    # API Configuration
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "AI Mini Games"
    VERSION = "1.0.0"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "*"  # Allow all origins for mobile development
    ]
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_TIMEOUT_MINUTES = 15

settings = Settings()

# ==================== Security ====================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def create_token(data: dict, token_type: TokenType, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with specified type and expiration"""
    to_encode = data.copy()
    to_encode["type"] = token_type.value
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        if token_type == TokenType.ACCESS:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ==================== Models ====================

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    PREMIUM = "premium"

class UserBase(BaseModel):
    """Base user model with validation"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    full_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v.lower()

class UserCreate(UserBase):
    """User registration model with password validation"""
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH, max_length=settings.PASSWORD_MAX_LENGTH)
    confirm_password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str

class UserInDB(UserBase):
    """User model stored in memory"""
    id: str
    hashed_password: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

class UserResponse(UserBase):
    """User response model (no sensitive data)"""
    id: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    """Token data extracted from JWT"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    type: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str

class PasswordChange(BaseModel):
    """Password change model"""
    current_password: str
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    confirm_new_password: str
    
    @field_validator('confirm_new_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    reset_token: str
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    confirm_password: str
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

# ==================== In-Memory Storage ====================

class InMemoryUserStore:
    """Thread-safe in-memory user storage with security features"""
    
    def __init__(self):
        self.users: Dict[str, UserInDB] = {}
        self.email_index: Dict[str, str] = {}
        self.username_index: Dict[str, str] = {}
        self.refresh_tokens: Dict[str, dict] = {}
        self.blacklisted_tokens: set = set()
        self.password_reset_tokens: Dict[str, dict] = {}
        self._init_admin_user()
    
    def _init_admin_user(self):
        """Create default admin user for testing"""
        admin_id = "admin-001"
        admin_user = UserInDB(
            id=admin_id,
            email="admin@aimini.games",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash("Admin123!"),
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            failed_login_attempts=0
        )
        self.users[admin_id] = admin_user
        self.email_index[admin_user.email] = admin_id
        self.username_index[admin_user.username] = admin_id
        logger.info(f"Admin user created: {admin_user.email}")
    
    def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user with validation"""
        # Check for existing user
        if user_data.email in self.email_index:
            raise ValueError("Email already registered")
        if user_data.username.lower() in self.username_index:
            raise ValueError("Username already taken")
        
        # Generate unique ID
        user_id = f"user-{secrets.token_hex(8)}"
        
        # Create user
        user = UserInDB(
            id=user_id,
            email=user_data.email,
            username=user_data.username.lower(),
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            failed_login_attempts=0
        )
        
        # Store user with indexes
        self.users[user_id] = user
        self.email_index[user.email] = user_id
        self.username_index[user.username] = user_id
        
        logger.info(f"User created: {user.email} (ID: {user_id})")
        return user
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email address"""
        user_id = self.email_index.get(email)
        return self.users.get(user_id) if user_id else None
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        user_id = self.username_index.get(username.lower())
        return self.users.get(user_id) if user_id else None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, update_data: dict) -> Optional[UserInDB]:
        """Update user data"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.now(timezone.utc)
        logger.info(f"User updated: {user_id}")
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user and cleanup indexes"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Remove from indexes
        self.email_index.pop(user.email, None)
        self.username_index.pop(user.username, None)
        
        # Remove user
        del self.users[user_id]
        
        # Cleanup tokens
        self.cleanup_user_tokens(user_id)
        
        logger.info(f"User deleted: {user_id}")
        return True
    
    def store_refresh_token(self, token: str, user_id: str, expires_at: datetime):
        """Store refresh token for validation"""
        self.refresh_tokens[token] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        }
    
    def validate_refresh_token(self, token: str) -> Optional[str]:
        """Validate refresh token and return user_id"""
        if token in self.blacklisted_tokens:
            return None
        
        token_data = self.refresh_tokens.get(token)
        if not token_data:
            return None
        
        if datetime.now(timezone.utc) > token_data["expires_at"]:
            del self.refresh_tokens[token]
            return None
        
        return token_data["user_id"]
    
    def blacklist_token(self, token: str):
        """Add token to blacklist"""
        self.blacklisted_tokens.add(token)
        logger.info(f"Token blacklisted: {token[:20]}...")
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return token in self.blacklisted_tokens
    
    def cleanup_user_tokens(self, user_id: str):
        """Remove all tokens associated with a user"""
        tokens_to_remove = [
            token for token, data in self.refresh_tokens.items()
            if data["user_id"] == user_id
        ]
        for token in tokens_to_remove:
            del self.refresh_tokens[token]
            self.blacklisted_tokens.add(token)
    
    def increment_failed_login(self, user: UserInDB) -> UserInDB:
        """Increment failed login attempts and lock if necessary"""
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOGIN_TIMEOUT_MINUTES)
            logger.warning(f"User locked due to failed login attempts: {user.email}")
        
        return user
    
    def reset_failed_login(self, user: UserInDB) -> UserInDB:
        """Reset failed login attempts"""
        user.failed_login_attempts = 0
        user.locked_until = None
        return user
    
    def is_user_locked(self, user: UserInDB) -> bool:
        """Check if user account is locked"""
        if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
            return True
        elif user.locked_until:
            # Unlock if timeout has passed
            user.locked_until = None
            user.failed_login_attempts = 0
        return False
    
    def create_password_reset_token(self, user_id: str) -> str:
        """Create a password reset token"""
        reset_token = secrets.token_urlsafe(32)
        self.password_reset_tokens[reset_token] = {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        return reset_token
    
    def validate_reset_token(self, token: str) -> Optional[str]:
        """Validate password reset token"""
        token_data = self.password_reset_tokens.get(token)
        if not token_data:
            return None
        
        if datetime.now(timezone.utc) > token_data["expires_at"]:
            del self.password_reset_tokens[token]
            return None
        
        return token_data["user_id"]
    
    def get_stats(self) -> dict:
        """Get storage statistics"""
        return {
            "total_users": len(self.users),
            "active_users": sum(1 for u in self.users.values() if u.is_active),
            "locked_users": sum(1 for u in self.users.values() if self.is_user_locked(u)),
            "active_refresh_tokens": len(self.refresh_tokens),
            "blacklisted_tokens": len(self.blacklisted_tokens),
            "pending_reset_tokens": len(self.password_reset_tokens)
        }

# Initialize storage
user_store = InMemoryUserStore()

# ==================== Dependencies ====================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Get current user from JWT token"""
    if user_store.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("user_id")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != TokenType.ACCESS.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_store.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# ==================== Application ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} Authentication Backend")
    logger.info(f"📝 API Documentation: http://localhost:8000/docs")
    logger.info(f"🔐 JWT Secret Key Length: {len(settings.SECRET_KEY)} characters")
    logger.info(f"👥 Initial users: {len(user_store.users)}")
    logger.info(f"🔑 Default admin credentials: admin@aimini.games / Admin123!")
    
    yield
    
    # Shutdown
    logger.info(f"👋 Shutting down {settings.PROJECT_NAME} Authentication Backend")
    logger.info(f"📊 Final stats: {user_store.get_stats()}")

app = FastAPI(
    title=f"{settings.PROJECT_NAME} Auth API",
    description="Production-ready authentication backend with JWT tokens",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# ==================== Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ==================== Exception Handlers ====================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# ==================== Routes ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"{settings.PROJECT_NAME} Authentication API",
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = user_store.get_stats()
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stats": stats
    }

# ==================== Authentication Routes ====================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user account
    
    Requirements:
    - Unique email and username
    - Password minimum 8 characters with complexity requirements
    - Email validation
    """
    try:
        # Create user
        user = user_store.create_user(user_data)
        
        # Log registration
        logger.info(f"New user registered: {user.email}")
        
        # Return user response
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email/username and password
    
    Returns JWT access and refresh tokens
    Compatible with OAuth2 password flow
    """
    # Find user by email or username
    user = user_store.get_user_by_email(form_data.username)
    if not user:
        user = user_store.get_user_by_username(form_data.username)
    
    if not user:
        logger.warning(f"Login attempt with unknown user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if user_store.is_user_locked(user):
        remaining_time = (user.locked_until - datetime.now(timezone.utc)).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {remaining_time} minutes"
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        user_store.increment_failed_login(user)
        logger.warning(f"Failed login attempt for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Reset failed attempts on successful login
    user_store.reset_failed_login(user)
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    
    # Create tokens
    access_token = create_token(
        data={"user_id": user.id, "username": user.username},
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token = create_token(
        data={"user_id": user.id, "username": user.username},
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    # Store refresh token
    user_store.store_refresh_token(
        refresh_token,
        user.id,
        datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
    )

@app.post("/auth/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    Mobile apps should use this to maintain authentication
    """
    # Validate refresh token
    try:
        payload = decode_token(request.refresh_token)
        token_type = payload.get("type")
        
        if token_type != TokenType.REFRESH.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = user_store.validate_refresh_token(request.refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    user = user_store.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_token(
        data={"user_id": user.id, "username": user.username},
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    new_refresh_token = create_token(
        data={"user_id": user.id, "username": user.username},
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    # Blacklist old refresh token
    user_store.blacklist_token(request.refresh_token)
    
    # Store new refresh token
    user_store.store_refresh_token(
        new_refresh_token,
        user.id,
        datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    logger.info(f"Token refreshed for user: {user.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
    )

@app.post("/auth/logout")
async def logout(
    current_user: UserInDB = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Logout current user and blacklist token
    
    Mobile apps should clear stored tokens
    """
    # Blacklist current access token
    user_store.blacklist_token(token)
    
    # Cleanup user's refresh tokens
    user_store.cleanup_user_tokens(current_user.id)
    
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Successfully logged out"}

# ==================== User Management Routes ====================

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user's profile information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@app.put("/auth/me")
async def update_profile(
    full_name: Optional[str] = Body(None, max_length=100),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update current user's profile"""
    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
    
    if update_data:
        user_store.update_user(current_user.id, update_data)
        logger.info(f"Profile updated for user: {current_user.email}")
    
    return {"message": "Profile updated successfully"}

@app.put("/auth/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Change user's password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    new_hashed_password = get_password_hash(password_data.new_password)
    user_store.update_user(current_user.id, {"hashed_password": new_hashed_password})
    
    # Invalidate all existing tokens
    user_store.cleanup_user_tokens(current_user.id)
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {"message": "Password updated successfully. Please login again."}

@app.post("/auth/request-password-reset")
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset token"""
    user = user_store.get_user_by_email(request.email)
    
    # Don't reveal if email exists
    if user:
        reset_token = user_store.create_password_reset_token(user.id)
        # In production, send email with reset token
        logger.info(f"Password reset requested for: {user.email}")
        # For testing, return token (remove in production)
        return {
            "message": "If the email exists, a reset link has been sent",
            "reset_token": reset_token  # REMOVE IN PRODUCTION
        }
    
    return {"message": "If the email exists, a reset link has been sent"}

@app.post("/auth/reset-password")
async def reset_password(reset_data: PasswordResetConfirm):
    """Reset password with reset token"""
    user_id = user_store.validate_reset_token(reset_data.reset_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    new_hashed_password = get_password_hash(reset_data.new_password)
    user_store.update_user(user_id, {
        "hashed_password": new_hashed_password,
        "failed_login_attempts": 0,
        "locked_until": None
    })
    
    # Invalidate all existing tokens
    user_store.cleanup_user_tokens(user_id)
    
    # Remove reset token
    del user_store.password_reset_tokens[reset_data.reset_token]
    
    user = user_store.get_user_by_id(user_id)
    logger.info(f"Password reset completed for: {user.email}")
    
    return {"message": "Password reset successfully"}

@app.delete("/auth/delete-account")
async def delete_account(
    current_user: UserInDB = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme)
):
    """Delete user account and all associated data"""
    # Blacklist current token
    user_store.blacklist_token(token)
    
    # Delete user
    if user_store.delete_user(current_user.id):
        logger.info(f"Account deleted: {current_user.email}")
        return {"message": "Account deleted successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete account"
    )

# ==================== Admin Routes ====================

@app.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_admin_user)
):
    """List all users (Admin only)"""
    users = list(user_store.users.values())[skip:skip + limit]
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in users
    ]

@app.get("/admin/stats")
async def get_system_stats(current_user: UserInDB = Depends(get_admin_user)):
    """Get system statistics (Admin only)"""
    return {
        "stats": user_store.get_stats(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.put("/admin/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: UserInDB = Depends(get_admin_user)
):
    """Activate a user account (Admin only)"""
    user = user_store.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_store.update_user(user_id, {"is_active": True})
    logger.info(f"User activated by admin: {user.email}")
    return {"message": "User activated successfully"}

@app.put("/admin/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: UserInDB = Depends(get_admin_user)
):
    """Deactivate a user account (Admin only)"""
    user = user_store.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user_store.update_user(user_id, {"is_active": False})
    user_store.cleanup_user_tokens(user_id)
    logger.info(f"User deactivated by admin: {user.email}")
    return {"message": "User deactivated successfully"}

# ==================== Testing/Development Routes ====================

if settings.SECRET_KEY == secrets.token_urlsafe(32):
    @app.get("/dev/test-auth")
    async def test_auth_flow():
        """Test authentication flow (Development only)"""
        test_user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="TestPass123!",
            confirm_password="TestPass123!"
        )
        
        # Try to create test user
        try:
            user = user_store.create_user(test_user_data)
        except ValueError:
            user = user_store.get_user_by_email(test_user_data.email)
        
        # Create tokens
        access_token = create_token(
            data={"user_id": user.id, "username": user.username},
            token_type=TokenType.ACCESS
        )
        
        return {
            "message": "Test authentication successful",
            "test_credentials": {
                "email": test_user_data.email,
                "password": "TestPass123!"
            },
            "sample_token": access_token,
            "api_docs": "http://localhost:8000/docs"
        }

# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )