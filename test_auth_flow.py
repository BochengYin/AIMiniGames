#!/usr/bin/env python3
"""
Test script to verify authentication flow for Flutter mobile app
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    """Terminal color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{message}{Colors.RESET}")
    print("=" * 50)

def test_health_check():
    """Test health check endpoint"""
    print_header("Testing Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is {data['status']}")
            print_info(f"Version: {data['version']}")
            print_info(f"Total users: {data['stats']['total_users']}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def test_registration():
    """Test user registration"""
    print_header("Testing User Registration")
    
    test_user = {
        "email": f"flutter_test_{datetime.now().timestamp()}@example.com",
        "username": f"flutter_test_{int(datetime.now().timestamp())}",
        "full_name": "Flutter Test User",
        "password": "Flutter123!",
        "confirm_password": "Flutter123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        
        if response.status_code == 201:
            user_data = response.json()
            print_success(f"User registered: {user_data['email']}")
            print_info(f"User ID: {user_data['id']}")
            print_info(f"Username: {user_data['username']}")
            return test_user
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(response.json())
            return None
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None

def test_login(credentials):
    """Test user login"""
    print_header("Testing User Login")
    
    login_data = {
        "username": credentials["email"],  # Can use email or username
        "password": credentials["password"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print_success("Login successful!")
            print_info(f"Access token (first 50 chars): {token_data['access_token'][:50]}...")
            print_info(f"Token expires in: {token_data['expires_in']} seconds")
            print_info(f"User role: {token_data['user']['role']}")
            return token_data
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(response.json())
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_authenticated_request(token_data):
    """Test authenticated endpoint"""
    print_header("Testing Authenticated Request")
    
    headers = {
        "Authorization": f"Bearer {token_data['access_token']}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print_success("Authenticated request successful!")
            print_info(f"User email: {user_data['email']}")
            print_info(f"User ID: {user_data['id']}")
            print_info(f"Last login: {user_data['last_login']}")
            return True
        else:
            print_error(f"Auth request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Auth request error: {e}")
        return False

def test_refresh_token(token_data):
    """Test token refresh"""
    print_header("Testing Token Refresh")
    
    refresh_data = {
        "refresh_token": token_data["refresh_token"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        
        if response.status_code == 200:
            new_token_data = response.json()
            print_success("Token refresh successful!")
            print_info(f"New access token (first 50 chars): {new_token_data['access_token'][:50]}...")
            return new_token_data
        else:
            print_error(f"Token refresh failed: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Token refresh error: {e}")
        return None

def test_logout(token_data):
    """Test user logout"""
    print_header("Testing Logout")
    
    headers = {
        "Authorization": f"Bearer {token_data['access_token']}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
        
        if response.status_code == 200:
            print_success("Logout successful!")
            return True
        else:
            print_error(f"Logout failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Logout error: {e}")
        return False

def test_cors_headers():
    """Test CORS headers for mobile app"""
    print_header("Testing CORS Headers")
    
    headers = {
        "Origin": "http://localhost:8081",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    }
    
    try:
        response = requests.options(f"{BASE_URL}/auth/login", headers=headers)
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        if cors_headers["Access-Control-Allow-Origin"]:
            print_success("CORS headers present")
            for header, value in cors_headers.items():
                if value:
                    print_info(f"{header}: {value}")
            return True
        else:
            print_error("CORS headers missing")
            return False
    except Exception as e:
        print_error(f"CORS test error: {e}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== AI Mini Games Authentication Test Suite ==={Colors.RESET}")
    print(f"Testing backend at: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}\n")
    
    results = []
    
    # Test health check
    results.append(("Health Check", test_health_check()))
    
    # Test CORS
    results.append(("CORS Headers", test_cors_headers()))
    
    # Test registration
    test_user = test_registration()
    results.append(("Registration", test_user is not None))
    
    if test_user:
        # Test login
        token_data = test_login(test_user)
        results.append(("Login", token_data is not None))
        
        if token_data:
            # Test authenticated request
            results.append(("Authenticated Request", test_authenticated_request(token_data)))
            
            # Test token refresh
            new_token = test_refresh_token(token_data)
            results.append(("Token Refresh", new_token is not None))
            
            # Use new token if refresh was successful
            if new_token:
                token_data = new_token
            
            # Test logout
            results.append(("Logout", test_logout(token_data)))
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print(f"{Colors.GREEN}✓{Colors.RESET} {test_name}")
        else:
            print(f"{Colors.RED}✗{Colors.RESET} {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Backend is ready for Flutter mobile app.{Colors.RESET}")
        print(f"\n{Colors.BLUE}Flutter app can connect to:{Colors.RESET}")
        print(f"  - API URL: {BASE_URL}")
        print(f"  - Auth endpoints: /auth/register, /auth/login, /auth/refresh, /auth/logout")
        print(f"  - Protected endpoints: /auth/me")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please check the backend.{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())