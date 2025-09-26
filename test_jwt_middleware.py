"""
Test script for JWT authentication middleware
Tests the get_current_user function and role verification
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.security import (
    create_access_token, 
    create_user_token_data, 
    verify_token,
    get_current_user,
    require_patient_role,
    require_doctor_role,
    require_admin_role
)
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException
import pytest
from datetime import timedelta

def test_create_and_verify_token():
    """Test JWT token creation and verification"""
    print("Testing JWT token creation and verification...")
    
    # Create token data
    user_data = create_user_token_data(
        user_id=1,
        email="test@mediclab.com", 
        role="patient"
    )
    
    # Create token
    token = create_access_token(user_data)
    print(f"Created token: {token[:50]}...")
    
    # Verify token
    try:
        payload = verify_token(token)
        print(f"Token verified successfully: {payload}")
        
        # Check payload contents
        assert payload['sub'] == '1'
        assert payload['email'] == 'test@mediclab.com'
        assert payload['role'] == 'patient'
        print("✓ Token payload is correct")
        return True
        
    except Exception as e:
        print(f"✗ Token verification failed: {e}")
        return False

def test_expired_token():
    """Test handling of expired tokens"""
    print("\nTesting expired token handling...")
    
    # Create token with very short expiration
    user_data = create_user_token_data(1, "test@mediclab.com", "patient")
    token = create_access_token(user_data, expires_delta=timedelta(seconds=-1))
    
    try:
        payload = verify_token(token)
        print("✗ Expired token was accepted (should have failed)")
        return False
    except HTTPException as e:
        if e.status_code == 401:
            print("✓ Expired token correctly rejected")
            return True
        else:
            print(f"✗ Wrong error code: {e.status_code}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_invalid_token():
    """Test handling of invalid tokens"""
    print("\nTesting invalid token handling...")
    
    invalid_token = "invalid.jwt.token"
    
    try:
        payload = verify_token(invalid_token)
        print("✗ Invalid token was accepted (should have failed)")
        return False
    except HTTPException as e:
        if e.status_code == 401:
            print("✓ Invalid token correctly rejected")
            return True
        else:
            print(f"✗ Wrong error code: {e.status_code}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

async def test_get_current_user_function():
    """Test the get_current_user middleware function"""
    print("\nTesting get_current_user function...")
    
    # Create a valid token
    user_data = create_user_token_data(1, "test@mediclab.com", "patient")
    token = create_access_token(user_data)
    
    # Create mock credentials
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token
    )
    
    try:
        user_info = await get_current_user(credentials)
        print(f"User info extracted: {user_info}")
        
        # Verify user info
        assert user_info['user_id'] == 1
        assert user_info['email'] == 'test@mediclab.com'
        assert user_info['role'] == 'patient'
        print("✓ get_current_user works correctly")
        return True
        
    except Exception as e:
        print(f"✗ get_current_user failed: {e}")
        return False

async def test_role_verification():
    """Test role verification functions"""
    print("\nTesting role verification functions...")
    
    # Test patient role
    patient_user = {
        'user_id': 1,
        'email': 'patient@mediclab.com',
        'role': 'patient'
    }
    
    try:
        result = await require_patient_role(patient_user)
        assert result == patient_user
        print("✓ Patient role verification works")
    except Exception as e:
        print(f"✗ Patient role verification failed: {e}")
        return False
    
    # Test doctor role
    doctor_user = {
        'user_id': 2,
        'email': 'doctor@mediclab.com',
        'role': 'doctor'
    }
    
    try:
        result = await require_doctor_role(doctor_user)
        assert result == doctor_user
        print("✓ Doctor role verification works")
    except Exception as e:
        print(f"✗ Doctor role verification failed: {e}")
        return False
    
    # Test admin role
    admin_user = {
        'user_id': 3,
        'email': 'admin@mediclab.com',
        'role': 'admin'
    }
    
    try:
        result = await require_admin_role(admin_user)
        assert result == admin_user
        print("✓ Admin role verification works")
    except Exception as e:
        print(f"✗ Admin role verification failed: {e}")
        return False
    
    return True

async def test_role_access_denial():
    """Test that role verification denies wrong roles"""
    print("\nTesting role access denial...")
    
    # Patient trying to access doctor endpoint
    patient_user = {
        'user_id': 1,
        'email': 'patient@mediclab.com',
        'role': 'patient'
    }
    
    try:
        await require_doctor_role(patient_user)
        print("✗ Patient was allowed doctor access (should have failed)")
        return False
    except HTTPException as e:
        if e.status_code == 403:
            print("✓ Patient correctly denied doctor access")
        else:
            print(f"✗ Wrong error code: {e.status_code}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Doctor trying to access admin endpoint
    doctor_user = {
        'user_id': 2,
        'email': 'doctor@mediclab.com',
        'role': 'doctor'
    }
    
    try:
        await require_admin_role(doctor_user)
        print("✗ Doctor was allowed admin access (should have failed)")
        return False
    except HTTPException as e:
        if e.status_code == 403:
            print("✓ Doctor correctly denied admin access")
            return True
        else:
            print(f"✗ Wrong error code: {e.status_code}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

async def run_async_tests():
    """Run all async tests"""
    tests = [
        ("get_current_user function", test_get_current_user_function),
        ("Role verification", test_role_verification),
        ("Role access denial", test_role_access_denial)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    return results

if __name__ == "__main__":
    import asyncio
    
    print("=== MedicLab JWT Middleware Test ===")
    print("Testing JWT authentication middleware functionality")
    print("=" * 50)
    
    # Run synchronous tests
    sync_tests = [
        ("JWT token creation/verification", test_create_and_verify_token),
        ("Expired token handling", test_expired_token),
        ("Invalid token handling", test_invalid_token)
    ]
    
    sync_results = []
    for test_name, test_func in sync_tests:
        try:
            result = test_func()
            sync_results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            sync_results.append((test_name, False))
    
    # Run async tests
    async_results = asyncio.run(run_async_tests())
    
    # Combine results
    all_results = sync_results + async_results
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    for test_name, result in all_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("✓ All JWT middleware tests passed!")
    else:
        print("✗ Some tests failed. Check implementation.")