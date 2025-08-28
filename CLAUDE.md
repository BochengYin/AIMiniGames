# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Plan & Review

**ALWAYS start with plan mode before any development work.** Before implementing features, fixes, or changes:

1. **Plan First** - Use Claude Code's plan mode to break down work into clear, actionable steps
2. **Document Plans** - Create task files in `.claude/tasks/YYYY-MM-DD_task_name.md` with:
   - Objective and prerequisites
   - Step-by-step implementation plan
   - Files to be modified and testing strategy
   - Risks and definition of done
3. **Track Progress** - Update plans during development with ✅ completed steps and real-time implementation logs
4. **Document Completion** - When finished, append detailed summary including:
   - All files modified (backend/frontend/database/config changes)
   - Tests added and patterns established
   - Known issues and handover notes for next engineer

**Future Claude Code instances:** Always check `.claude/tasks/` directory first to understand recent work and context. Look for "Next Steps" and "Handover Notes" in the most recent completed tasks.

This ensures seamless handover between Claude Code sessions and provides complete implementation documentation for human developers.

## Project Overview

AI Mini Games is a dual-stack platform consisting of a Flutter mobile app and Python FastAPI backend for creating, sharing, and playing AI-generated mini-games. Users describe games in natural language, and the AI generates playable games within 15-30 minutes.

## Architecture

**Frontend (Mobile App):**
- Flutter 3.16+ cross-platform mobile app
- Riverpod for state management
- Clean Architecture with feature-based organization (`lib/features/`)
- Offline-first approach using Hive + Secure Storage
- Flame game engine for generated mini-games

**Backend (API):**
- FastAPI with Python 3.11+ using async/await patterns
- Feature-based modular structure in `app/features/`
- PostgreSQL + SQLAlchemy 2.0 for data persistence
- Redis for caching and Celery for background AI processing
- JWT authentication with refresh token support
- WebSocket support for real-time multiplayer

## Development Commands

### Environment Setup
```bash
make setup          # Initial project setup (creates .env, starts Docker services, installs deps)
make start          # Start all backend services (Docker containers)
make stop           # Stop all services
make clean          # Clean all build artifacts and containers
```

### Backend Development
```bash
# Run backend directly (without Docker)
cd app && python main.py

# Backend testing and quality
make backend-test   # Run pytest with coverage
make backend-shell  # Access running container shell
make db-migrate     # Run database migrations
make db-reset       # Reset database completely

# Code quality
make lint           # Run flake8, black, isort on Python code
make format         # Auto-format Python code with black + isort
```

### Flutter Development
```bash
# Setup and run
make flutter-setup  # Install Flutter dependencies
cd mobile && flutter run -d chrome --web-port=3000  # Run on web
cd mobile && flutter run -d macos   # Run on macOS
cd mobile && flutter run -d ios     # Run on iOS simulator

# Flutter testing and quality
make flutter-test   # Run Flutter unit/widget tests
cd mobile && flutter analyze        # Static analysis
cd mobile && flutter test --coverage  # Run tests with coverage

# Building for production
make flutter-build-ios      # Build iOS release
make flutter-build-android  # Build Android release
```

### Combined Development
```bash
make test           # Run both backend and Flutter tests
make logs           # Show all Docker container logs
make health-check   # Check service health endpoints
```

## Key Architecture Patterns

**Backend Feature Organization:**
Each feature in `app/features/` follows this structure:
- `routes.py` - FastAPI route definitions
- `models.py` - SQLAlchemy database models
- `schemas.py` - Pydantic request/response schemas
- `services.py` - Business logic layer

**Mobile App Clean Architecture:**
- `data/` - Repository implementations, API clients, local storage
- `domain/` - Business entities, repository abstractions, use cases
- `presentation/` - UI screens, widgets, Riverpod providers

**Configuration Management:**
- Backend: `app/core/config.py` with environment-based settings
- Mobile: `mobile/lib/core/config/app_config.dart` with compile-time definitions
- Environment variables in `.env` file (create from `.env.example`)

## API Structure

All API endpoints are prefixed with `/api/v1/` and organized by feature:
- `/auth` - JWT authentication, user management
- `/games` - CRUD operations for user games
- `/ai` - AI game generation and status tracking
- `/marketplace` - Game sharing and discovery
- `/multiplayer` - Real-time multiplayer sessions
- `/users` - User profile management

Interactive API documentation available at `http://localhost:8000/docs` when backend is running.

## Data Flow

**Game Generation Process:**
1. Mobile app sends natural language prompt to `/api/v1/ai/generate-game`
2. Backend queues Celery background task for AI processing
3. Mobile app polls `/api/v1/ai/generation/{task_id}` for status updates
4. Generated game assets stored in S3-compatible storage
5. Game metadata saved to PostgreSQL
6. Mobile app downloads and caches game locally using Hive

**Authentication Flow:**
1. Mobile app authenticates via `/api/v1/auth/login`
2. Backend returns JWT access + refresh tokens
3. Mobile stores tokens in FlutterSecureStorage
4. API requests include Bearer token in Authorization header
5. Automatic token refresh handled by Dio interceptors

## Development Environment

**Required Services:**
- PostgreSQL (localhost:5432) - Primary database
- Redis (localhost:6379) - Caching and task queue
- FastAPI server (localhost:8000) - Backend API
- Flutter web server (localhost:3000) - Mobile app development

**Key Directories:**
- `app/` - Python FastAPI backend
- `mobile/` - Flutter cross-platform mobile app
- `requirements.txt` - Python dependencies
- `mobile/pubspec.yaml` - Flutter dependencies
- `docker-compose.yml` - Development services orchestration

## Testing Strategy

**Backend Testing:**
- Unit tests using pytest with async support
- Integration tests for API endpoints
- Database tests using SQLAlchemy test fixtures
- Coverage reporting via pytest-cov

**Mobile Testing:**
- Widget tests for UI components
- Unit tests for business logic
- Integration tests for API communication
- Golden tests for visual regression

## Common Development Workflows

**Adding a New Feature:**
1. Create feature directory in both `app/features/` and `mobile/lib/features/`
2. Implement backend routes, models, schemas in Python
3. Add route to `app/api/v1/router.py`
4. Implement mobile UI, providers, and services in Flutter
5. Add navigation routes if needed
6. Write tests for both backend and mobile
7. Update API documentation

**Database Changes:**
1. Modify SQLAlchemy models in `app/features/{feature}/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and edit migration file
4. Apply migration: `alembic upgrade head`
5. Update corresponding Flutter models if needed

**Mobile UI Development:**
1. Flutter app supports hot reload - press `r` in terminal while running
2. Use Material 3 design system (already configured)
3. State management via Riverpod providers
4. Navigation handled by GoRouter
5. API integration via Dio HTTP client with automatic JWT handling