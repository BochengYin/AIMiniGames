#!/bin/bash

# AI Mini Games Authentication Backend Startup Script
# Phase 1 - In-Memory Storage Implementation

echo "========================================"
echo "AI Mini Games Authentication Backend"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python version: $PYTHON_VERSION"

# Check for required packages
echo ""
echo "Checking dependencies..."

MISSING_DEPS=0

# Check each required package
for package in fastapi uvicorn pydantic passlib jose bcrypt email_validator; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "✓ $package is installed"
    else
        echo "❌ $package is missing"
        MISSING_DEPS=1
    fi
done

# Install missing dependencies
if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo "Installing missing dependencies..."
    python3 -m pip install fastapi uvicorn pydantic passlib python-jose[cryptography] bcrypt email-validator
fi

echo ""
echo "========================================"
echo "Starting Authentication Backend..."
echo "========================================"
echo ""
echo "🔐 Admin Credentials:"
echo "   Email: admin@aimini.games"
echo "   Password: Admin123!"
echo ""
echo "📝 API Documentation: http://localhost:8000/docs"
echo "🔗 API Base URL: http://localhost:8000"
echo ""
echo "📱 Flutter App Configuration:"
echo "   - Base URL: http://localhost:8000"
echo "   - Auth endpoints:"
echo "     • POST /auth/register"
echo "     • POST /auth/login"
echo "     • POST /auth/refresh"
echo "     • POST /auth/logout"
echo "     • GET  /auth/me"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start the authentication backend
python3 auth_backend.py