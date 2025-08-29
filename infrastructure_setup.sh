#!/bin/bash

# AI Mini Games - Infrastructure Setup Script
# This script helps set up the development infrastructure

set -e

echo "========================================="
echo "AI Mini Games - Infrastructure Setup"
echo "========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script is designed for macOS${NC}"
    exit 1
fi

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Homebrew if not present
install_homebrew() {
    if ! command_exists brew; then
        echo -e "${YELLOW}Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH based on architecture
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    else
        echo -e "${GREEN}✓ Homebrew is installed${NC}"
    fi
}

# Function to check and install Docker Desktop
check_docker() {
    echo ""
    echo "Checking Docker installation..."
    
    if command_exists docker; then
        echo -e "${GREEN}✓ Docker is installed${NC}"
        docker --version
    else
        echo -e "${RED}✗ Docker is not installed${NC}"
        echo -e "${YELLOW}Please install Docker Desktop for Mac:${NC}"
        echo "  1. Download from: https://www.docker.com/products/docker-desktop/"
        echo "  2. Install and launch Docker Desktop"
        echo "  3. Wait for Docker to start (whale icon in menu bar)"
        echo "  4. Re-run this script"
        return 1
    fi
    
    # Check if Docker daemon is running
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker daemon is running${NC}"
    else
        echo -e "${RED}✗ Docker daemon is not running${NC}"
        echo -e "${YELLOW}Please start Docker Desktop and try again${NC}"
        return 1
    fi
    
    # Check docker-compose
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker Compose is available${NC}"
    else
        echo -e "${RED}✗ Docker Compose is not available${NC}"
        return 1
    fi
    
    return 0
}

# Function to install PostgreSQL locally (fallback option)
install_postgresql_local() {
    echo ""
    echo -e "${YELLOW}Installing PostgreSQL locally (fallback option)...${NC}"
    
    if command_exists psql; then
        echo -e "${GREEN}✓ PostgreSQL is already installed${NC}"
    else
        brew install postgresql@15
        brew services start postgresql@15
        echo -e "${GREEN}✓ PostgreSQL installed and started${NC}"
    fi
    
    # Create database and user
    createdb aimini_db 2>/dev/null || echo "Database already exists"
    psql -d aimini_db -c "CREATE USER aimini_user WITH PASSWORD 'password';" 2>/dev/null || echo "User already exists"
    psql -d aimini_db -c "GRANT ALL PRIVILEGES ON DATABASE aimini_db TO aimini_user;" 2>/dev/null || true
}

# Function to install Redis locally (fallback option)
install_redis_local() {
    echo ""
    echo -e "${YELLOW}Installing Redis locally (fallback option)...${NC}"
    
    if command_exists redis-server; then
        echo -e "${GREEN}✓ Redis is already installed${NC}"
    else
        brew install redis
        brew services start redis
        echo -e "${GREEN}✓ Redis installed and started${NC}"
    fi
}

# Function to setup Python environment
setup_python_env() {
    echo ""
    echo "Setting up Python environment..."
    
    # Check Python version
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
        echo -e "${GREEN}✓ Python $PYTHON_VERSION is installed${NC}"
    else
        echo -e "${RED}✗ Python 3 is not installed${NC}"
        echo "Installing Python 3.11..."
        brew install python@3.11
    fi
    
    # Create virtual environment if not exists
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    echo "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Python dependencies installed${NC}"
    else
        echo -e "${RED}✗ requirements.txt not found${NC}"
    fi
}

# Main execution
echo ""
echo "Step 1: Installing Homebrew (if needed)..."
install_homebrew

echo ""
echo "Step 2: Checking Docker..."
if check_docker; then
    DOCKER_AVAILABLE=true
else
    DOCKER_AVAILABLE=false
    echo ""
    echo -e "${YELLOW}Docker is not available. Setting up local fallback services...${NC}"
    
    echo "Step 2a: Installing PostgreSQL locally..."
    install_postgresql_local
    
    echo "Step 2b: Installing Redis locally..."
    install_redis_local
fi

echo ""
echo "Step 3: Setting up Python environment..."
setup_python_env

echo ""
echo "========================================="
echo "Setup Summary"
echo "========================================="

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "${GREEN}✓ Docker is ready${NC}"
    echo ""
    echo "To start the services, run:"
    echo "  make start"
    echo "  OR"
    echo "  docker-compose up -d"
else
    echo -e "${YELLOW}⚠ Docker is not available${NC}"
    echo "PostgreSQL and Redis have been installed locally as fallback"
    echo ""
    echo "To run the backend locally:"
    echo "  source .venv/bin/activate"
    echo "  python -m app.main"
    echo ""
    echo -e "${RED}Important: For full functionality, please install Docker Desktop${NC}"
fi

echo ""
echo "Backend API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "========================================="