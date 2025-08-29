#!/usr/bin/env python3
"""
Development Services Startup Script
Attempts to start services with Docker, falls back to local alternatives
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

# Color codes for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def run_command(cmd, check=False, capture_output=False):
    """Run a shell command and return result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return None


def check_command_exists(cmd):
    """Check if a command exists"""
    result = run_command(f"which {cmd}", capture_output=True)
    return result is not None and result.returncode == 0


def check_docker():
    """Check if Docker is available and running"""
    if not check_command_exists("docker"):
        return False
    
    # Check if Docker daemon is running
    result = run_command("docker info", capture_output=True)
    return result is not None and result.returncode == 0


def start_docker_services():
    """Start services using Docker Compose"""
    print(f"{BLUE}Starting services with Docker...{NC}")
    
    # Check if docker-compose.yml exists
    if not Path("docker-compose.yml").exists():
        print(f"{RED}docker-compose.yml not found{NC}")
        return False
    
    # Start only essential services first
    print("Starting PostgreSQL and Redis...")
    result = run_command("docker-compose up -d db redis", check=False)
    if result and result.returncode == 0:
        print(f"{GREEN}✓ Database services started{NC}")
        
        # Wait for services to be healthy
        print("Waiting for services to be ready...")
        time.sleep(5)
        
        # Start API service
        print("Starting API service...")
        result = run_command("docker-compose up -d api", check=False)
        if result and result.returncode == 0:
            print(f"{GREEN}✓ API service started{NC}")
            return True
    
    print(f"{RED}Failed to start Docker services{NC}")
    return False


def check_local_services():
    """Check and start local PostgreSQL and Redis if available"""
    services_available = True
    
    # Check PostgreSQL
    if check_command_exists("psql"):
        print(f"{GREEN}✓ PostgreSQL is available locally{NC}")
        # Try to start if not running
        run_command("brew services start postgresql@15", capture_output=True)
    else:
        print(f"{YELLOW}PostgreSQL not found locally{NC}")
        services_available = False
    
    # Check Redis
    if check_command_exists("redis-server"):
        print(f"{GREEN}✓ Redis is available locally{NC}")
        # Try to start if not running
        run_command("brew services start redis", capture_output=True)
    else:
        print(f"{YELLOW}Redis not found locally{NC}")
        services_available = False
    
    return services_available


def setup_python_env():
    """Setup Python environment and install dependencies"""
    print(f"{BLUE}Setting up Python environment...{NC}")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print(f"{RED}requirements.txt not found{NC}")
        return False
    
    # Install dependencies
    print("Installing Python dependencies...")
    result = run_command(f"{sys.executable} -m pip install -r requirements.txt", capture_output=True)
    if result and result.returncode == 0:
        print(f"{GREEN}✓ Dependencies installed{NC}")
        return True
    else:
        print(f"{RED}Failed to install dependencies{NC}")
        if result:
            print(result.stderr)
        return False


def start_backend_local():
    """Start the backend API locally"""
    print(f"{BLUE}Starting backend API locally...{NC}")
    
    # Set environment variables for local development
    env = os.environ.copy()
    env.update({
        'DATABASE_URL': 'postgresql://aimini_user:password@localhost:5432/aimini_db',
        'REDIS_URL': 'redis://localhost:6379',
        'SECRET_KEY': 'dev-secret-key-not-for-production',
        'ENVIRONMENT': 'development',
        'DEBUG': 'true'
    })
    
    # Try to start the backend
    print(f"Starting API server on http://localhost:8000")
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"], env=env)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Backend stopped{NC}")
    except Exception as e:
        print(f"{RED}Failed to start backend: {e}{NC}")
        return False
    
    return True


def update_coordination_status(status_update):
    """Update the coordination.json file with current status"""
    coord_file = Path("coordination.json")
    if coord_file.exists():
        with open(coord_file, 'r') as f:
            data = json.load(f)
        
        # Add infrastructure status
        data['infrastructure_status'] = status_update
        data['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        with open(coord_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"{GREEN}✓ Updated coordination.json{NC}")


def main():
    """Main execution flow"""
    print("=" * 50)
    print("AI Mini Games - Development Services Startup")
    print("=" * 50)
    
    status_update = {
        'docker_available': False,
        'services_running': [],
        'issues': []
    }
    
    # Check for Docker
    if check_docker():
        print(f"{GREEN}✓ Docker is available{NC}")
        status_update['docker_available'] = True
        
        # Try to start services with Docker
        if start_docker_services():
            print(f"\n{GREEN}Services started successfully with Docker!{NC}")
            print(f"Backend API: http://localhost:8000")
            print(f"API Documentation: http://localhost:8000/docs")
            status_update['services_running'] = ['PostgreSQL', 'Redis', 'FastAPI']
            update_coordination_status(status_update)
            return 0
    else:
        print(f"{YELLOW}⚠ Docker is not available{NC}")
        status_update['issues'].append("Docker not installed or not running")
        
        # Fallback to local services
        print(f"\n{YELLOW}Attempting to use local services...{NC}")
        
        if check_local_services():
            # Setup Python environment
            if setup_python_env():
                # Start backend locally
                status_update['services_running'] = ['PostgreSQL (local)', 'Redis (local)']
                update_coordination_status(status_update)
                
                if start_backend_local():
                    status_update['services_running'].append('FastAPI (local)')
                    update_coordination_status(status_update)
                    return 0
            else:
                status_update['issues'].append("Failed to setup Python environment")
        else:
            status_update['issues'].append("Local services not available")
            print(f"\n{RED}Unable to start services.{NC}")
            print(f"{YELLOW}Please install Docker Desktop or run the infrastructure setup script:{NC}")
            print(f"  ./infrastructure_setup.sh")
    
    update_coordination_status(status_update)
    return 1


if __name__ == "__main__":
    sys.exit(main())