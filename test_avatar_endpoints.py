"""
Tests for avatar update endpoints in MedicLab
Verifies SSRF protection in the API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# Import the FastAPI app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from backend.app.main import app
from backend.app.database import get_db, SessionLocal
from backend.app.models import User, UserRole
from backend.app.security import create_access_token, create_user_token_data

client = TestClient(app)


class TestAvatarEndpoints:
    """Test suite for avatar update endpoints"""
    
    def setup_method(self):
        """Setup test data before each test"""
        # Create test user token
        self.test_user_data = {
            "user_id": 1,
            "email": "test@example.com",
            "role": "patient"
        }
        
        token_data = create_user_token_data(
            user_id=self.test_user_data["user_id"],
            email=self.test_user_data["email"],
            role=self.test_user_data["role"]
        )
        
        self.test_token = create_access_token(token_data)
        self.auth_headers = {"Authorization": f"Bearer {self.test_token}"}
    
    @patch('backend.app.routers.users.get_db')
    @patch('backend.app.ssrf_protection.download_avatar_safely')
    @patch('socket.gethostbyname')
    def test_update_avatar_success(self, mock_gethostbyname, mock_download, mock_get_db):
        """Test successful avatar update"""
        # Mock DNS resolution
        mock_gethostbyname.return_value = "8.8.8.8"
        
        # Mock successful download
        mock_download.return_value = (True, "", b"fake_image_data")
        
        # Mock database
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.avatar_url = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        # Test valid avatar URL
        avatar_data = {
            "avatar_url": "https://imgur.com/test.jpg"
        }
        
        response = client.put(
            "/api/users/me/avatar",
            json=avatar_data,
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "avatar_url" in data
        assert data["avatar_url"] == avatar_data["avatar_url"]
        
        # Verify database update was called
        mock_db.commit.assert_called_once()
    
    def test_update_avatar_invalid_domain(self):
        """Test avatar update with invalid domain"""
        avatar_data = {
            "avatar_url": "https://evil.com/malicious.jpg"
        }
        
        response = client.put(
            "/api/users/me/avatar",
            json=avatar_data,
            headers=self.auth_headers
        )
        
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "detail" in data
    
    def test_update_avatar_invalid_scheme(self):
        """Test avatar update with invalid URL scheme"""
        avatar_data = {
            "avatar_url": "ftp://imgur.com/test.jpg"
        }
        
        response = client.put(
            "/api/users/me/avatar",
            json=avatar_data,
            headers=self.auth_headers
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    @patch('backend.app.routers.users.get_db')
    @patch('backend.app.ssrf_protection.download_avatar_safely')
    @patch('socket.gethostbyname')
    def test_update_avatar_ssrf_attempt(self, mock_gethostbyname, mock_download, mock_get_db):
        """Test SSRF attempt detection"""
        # Mock DNS resolution to private IP
        mock_gethostbyname.return_value = "127.0.0.1"
        
        # Mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        avatar_data = {
            "avatar_url": "https://imgur.com/test.jpg"
        }
        
        response = client.put(
            "/api/users/me/avatar",
            json=avatar_data,
            headers=self.auth_headers
        )
        
        assert response.status_code == 422  # Pydantic validation should catch this
    
    @patch('backend.app.routers.users.get_db')
    @patch('backend.app.ssrf_protection.download_avatar_safely')
    @patch('socket.gethostbyname')
    def test_update_avatar_download_failure(self, mock_gethostbyname, mock_download, mock_get_db):
        """Test avatar update when download fails"""
        # Mock DNS resolution
        mock_gethostbyname.return_value = "8.8.8.8"
        
        # Mock download failure
        mock_download.return_value = (False, "Download failed", b"")
        
        # Mock database
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        avatar_data = {
            "avatar_url": "https://imgur.com/test.jpg"
        }
        
        response = client.put(
            "/api/users/me/avatar",
            json=avatar_data,
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Error descargando avatar" in data["detail"]
    
    def test_update_avatar_no_auth(self):
        """Test avatar update without authentication"""
        avatar_data = {
            "avatar_url": "https://imgur.com/test.jpg"
        }
        
        response = client.put(
            "/api/users/me/avatar",
            json=avatar_data
        )
        
        assert response.status_code == 403  # No authorization header
    
    def test_update_avatar_invalid_token(self):
        """Test avatar update with invalid token"""
        avatar_data = {
            "avatar_url": "https://imgur.com/test.jpg"
        }
        
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.put(
            "/api/users/me/avatar",
            json=avatar_data,
            headers=invalid_headers
        )
        
        assert response.status_code == 401
    
    @patch('backend.app.routers.users.get_db')
    def test_get_user_profile(self, mock_get_db):
        """Test getting user profile"""
        # Mock database
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = UserRole.PATIENT
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.avatar_url = None
        mock_user.is_active = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_db.return_value = mock_db
        
        response = client.get(
            "/api/users/me",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
    
    @patch('backend.app.routers.users.get_db')
    def test_get_doctors_list_as_patient(self, mock_get_db):
        """Test getting doctors list as patient"""
        # Mock database
        mock_db = MagicMock()
        mock_doctors = [
            MagicMock(id=2, email="doctor1@example.com", role=UserRole.DOCTOR),
            MagicMock(id=3, email="doctor2@example.com", role=UserRole.DOCTOR)
        ]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_doctors
        mock_get_db.return_value = mock_db
        
        response = client.get(
            "/api/users/doctors",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_doctors_list_as_doctor_forbidden(self):
        """Test that doctors cannot access doctors list"""
        # Create doctor token
        doctor_token_data = create_user_token_data(
            user_id=2,
            email="doctor@example.com",
            role="doctor"
        )
        doctor_token = create_access_token(doctor_token_data)
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
        
        response = client.get(
            "/api/users/doctors",
            headers=doctor_headers
        )
        
        assert response.status_code == 403


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])