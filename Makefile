# AI Mini Games - Development Makefile

.PHONY: help setup start stop clean test backend-test flutter-test lint format

# Default target
help:
	@echo "AI Mini Games - Development Commands"
	@echo "=================================="
	@echo "setup          - Initial project setup"
	@echo "start          - Start all services"
	@echo "stop           - Stop all services"
	@echo "clean          - Clean all build artifacts"
	@echo "test           - Run all tests"
	@echo "backend-test   - Run backend tests only"
	@echo "flutter-test   - Run Flutter tests only"
	@echo "lint           - Run linting on all code"
	@echo "format         - Format all code"
	@echo "backend-shell  - Access backend container shell"
	@echo "logs           - Show all container logs"

# Initial setup
setup:
	@echo "🔧 Setting up AI Mini Games development environment..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "📝 Created .env file from template"; fi
	@echo "🐳 Starting Docker services..."
	@docker-compose up -d postgres redis
	@echo "📦 Installing Python dependencies..."
	@pip install -r requirements.txt
	@echo "🔨 Setting up pre-commit hooks..."
	@pre-commit install
	@echo "✅ Setup complete! Run 'make start' to begin development"

# Start development environment
start:
	@echo "🚀 Starting AI Mini Games development environment..."
	@docker-compose up -d
	@echo "Backend API: http://localhost:8000"
	@echo "Backend Docs: http://localhost:8000/docs"
	@echo "📱 To start Flutter: cd mobile && flutter run"

# Stop all services
stop:
	@echo "⏹️  Stopping AI Mini Games services..."
	@docker-compose down

# Clean up
clean:
	@echo "🧹 Cleaning up build artifacts..."
	@docker-compose down -v
	@docker system prune -f
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -name "*.pyc" -delete
	@cd mobile && flutter clean
	@echo "✅ Cleanup complete"

# Run all tests
test: backend-test flutter-test
	@echo "✅ All tests completed"

# Backend tests
backend-test:
	@echo "🧪 Running backend tests..."
	@pytest tests/ -v --cov=app --cov-report=html

# Flutter tests
flutter-test:
	@echo "🧪 Running Flutter tests..."
	@cd mobile && flutter test

# Lint all code
lint:
	@echo "🔍 Running linters..."
	@echo "Backend linting..."
	@flake8 app tests
	@black --check app tests
	@isort --check-only app tests
	@echo "Flutter linting..."
	@cd mobile && flutter analyze

# Format all code
format:
	@echo "✨ Formatting code..."
	@echo "Backend formatting..."
	@black app tests
	@isort app tests
	@echo "Flutter formatting..."
	@cd mobile && dart format .

# Development utilities
backend-shell:
	@docker-compose exec api /bin/bash

logs:
	@docker-compose logs -f

db-migrate:
	@echo "🗄️  Running database migrations..."
	@alembic upgrade head

db-reset:
	@echo "⚠️  Resetting database..."
	@docker-compose down postgres
	@docker volume rm aimini_postgres_data
	@docker-compose up -d postgres
	@sleep 5
	@alembic upgrade head

# Mobile development
flutter-setup:
	@echo "📱 Setting up Flutter..."
	@cd mobile && flutter pub get
	@cd mobile && flutter pub run build_runner build

flutter-run-ios:
	@cd mobile && flutter run -d ios

flutter-run-android:
	@cd mobile && flutter run -d android

flutter-build-ios:
	@cd mobile && flutter build ios --release

flutter-build-android:
	@cd mobile && flutter build apk --release

# Production deployment
docker-build:
	@echo "🐳 Building production Docker images..."
	@docker build -t aimini-backend .

docker-push:
	@echo "📤 Pushing to registry..."
	@docker tag aimini-backend your-registry/aimini-backend:latest
	@docker push your-registry/aimini-backend:latest

# Monitoring
health-check:
	@echo "🔍 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend is down"
	@echo "✅ Health check complete"