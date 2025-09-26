"""
Test script for authentication endpoints
Tests the implemented auth router functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_register_endpoint():
    """Test user registration endpoint"""
    print("Testing /api/auth/register endpoint...")
    
    # Test data
    user_data = {
        "email": "test@mediclab.com",
        "password": "TestPassword123",
        "first_name": "Juan",
        "last_name": "Pérez",
        "role": "patient"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login_endpoint():
    """Test user login endpoint"""
    print("\nTesting /api/auth/login endpoint...")
    
    # Login data
    login_data = {
        "email": "test@mediclab.com",
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_login():
    """Test login with invalid credentials"""
    print("\nTesting login with invalid credentials...")
    
    # Invalid login data
    login_data = {
        "email": "test@mediclab.com",
        "password": "WrongPassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting on login endpoint"""
    print("\nTesting rate limiting (making multiple requests)...")
    
    login_data = {
        "email": "test@mediclab.com",
        "password": "WrongPassword"
    }
    
    # Make multiple requests to trigger rate limiting
    for i in range(7):  # Rate limit is 5/minute
        try:
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            print(f"Request {i+1}: Status {response.status_code}")
            if response.status_code == 429:
                print("Rate limiting triggered!")
                return True
        except Exception as e:
            print(f"Error on request {i+1}: {e}")
    
    return False

if __name__ == "__main__":
    print("=== MedicLab Auth Endpoints Test ===")
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    print("=" * 40)
    
    # Run tests
    tests = [
        ("Register", test_register_endpoint),
        ("Login", test_login_endpoint),
        ("Invalid Login", test_invalid_login),
        ("Rate Limiting", test_rate_limiting)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")