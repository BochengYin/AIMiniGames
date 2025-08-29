#!/usr/bin/env python3
"""
Test script to verify Flutter app authentication with FastAPI backend
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✓ Backend is running at http://localhost:8000")
            return True
    except:
        print("✗ Backend is not running")
        return False

def test_login_admin():
    """Test login with admin credentials"""
    print("\n--- Testing Admin Login ---")
    
    # Test with form-data format (as expected by backend)
    data = {
        "username": "admin@aimini.games",  # Backend accepts email as username
        "password": "Admin123!"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=data,  # form-data format
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Login successful!")
        print(f"  - Access Token: {result['access_token'][:50]}...")
        print(f"  - Token Type: {result['token_type']}")
        print(f"  - User: {result['user']['username']} ({result['user']['email']})")
        print(f"  - Role: {result['user']['role']}")
        return result['access_token']
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint with token"""
    print("\n--- Testing Protected Endpoint ---")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✓ Protected endpoint accessible")
        print(f"  - User ID: {user['id']}")
        print(f"  - Username: {user['username']}")
        print(f"  - Email: {user['email']}")
        print(f"  - Last Login: {user['last_login']}")
        return True
    else:
        print(f"✗ Protected endpoint failed: {response.status_code}")
        return False

def test_register_new_user():
    """Test registering a new user"""
    print("\n--- Testing User Registration ---")
    
    # Generate unique test user
    timestamp = int(time.time())
    test_user = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@aimini.games",
        "password": "Test123!Pass",
        "full_name": "Test User"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=test_user
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Registration successful!")
        print(f"  - User ID: {result['id']}")
        print(f"  - Username: {result['username']}")
        print(f"  - Email: {result['email']}")
        
        # Try to login with new user
        print("\n  Testing login with new user...")
        login_data = {
            "username": test_user['username'],
            "password": test_user['password']
        }
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code == 200:
            print(f"  ✓ New user can login successfully")
            return True
        else:
            print(f"  ✗ New user login failed")
            return False
    else:
        print(f"✗ Registration failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_invalid_credentials():
    """Test login with invalid credentials"""
    print("\n--- Testing Invalid Credentials ---")
    
    data = {
        "username": "invalid@user.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 401:
        print(f"✓ Invalid credentials properly rejected (401)")
        return True
    else:
        print(f"✗ Unexpected response for invalid credentials: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("Flutter Authentication Test Suite")
    print("=" * 60)
    
    if not test_backend_health():
        print("\n⚠ Please start the backend first:")
        print("  python3 auth_backend.py")
        return
    
    # Run tests
    token = test_login_admin()
    if token:
        test_protected_endpoint(token)
    
    test_register_new_user()
    test_invalid_credentials()
    
    print("\n" + "=" * 60)
    print("Flutter App Configuration:")
    print("=" * 60)
    print("\n✓ Backend URL: http://localhost:8000")
    print("✓ Login endpoint: POST /auth/login (form-data)")
    print("✓ Register endpoint: POST /auth/register (JSON)")
    print("✓ Protected endpoint: GET /auth/me")
    print("\n✓ Test credentials:")
    print("  - Email: admin@aimini.games")
    print("  - Password: Admin123!")
    print("\n✓ Flutter app ready to test!")
    print("  Run: cd mobile && flutter run")

if __name__ == "__main__":
    main()