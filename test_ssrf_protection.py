"""
Tests for SSRF protection functionality in MedicLab
Verifies URL validation and IP filtering for avatar uploads
"""

import pytest
from unittest.mock import patch, MagicMock
import socket

# Import the functions to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from backend.app.ssrf_protection import (
    is_private_ip, 
    validate_avatar_url, 
    download_avatar_safely,
    ALLOWED_AVATAR_DOMAINS
)


class TestSSRFProtection:
    """Test suite for SSRF protection functions"""
    
    def test_is_private_ip_detection(self):
        """Test detection of private/internal IP addresses"""
        # Private IPs should return True
        assert is_private_ip("127.0.0.1") == True  # Loopback
        assert is_private_ip("10.0.0.1") == True   # Private Class A
        assert is_private_ip("172.16.0.1") == True # Private Class B
        assert is_private_ip("192.168.1.1") == True # Private Class C
        assert is_private_ip("169.254.1.1") == True # Link-local
        
        # Public IPs should return False
        assert is_private_ip("8.8.8.8") == False   # Google DNS
        assert is_private_ip("1.1.1.1") == False   # Cloudflare DNS
        assert is_private_ip("208.67.222.222") == False # OpenDNS
        
        # Invalid IPs should return True (fail safe)
        assert is_private_ip("invalid.ip") == True
        assert is_private_ip("999.999.999.999") == True
    
    def test_validate_avatar_url_scheme_validation(self):
        """Test URL scheme validation (http/https only)"""
        # Valid schemes
        valid, _ = validate_avatar_url("https://imgur.com/image.jpg")
        assert valid == True
        
        valid, _ = validate_avatar_url("http://imgur.com/image.jpg")
        assert valid == True
        
        # Invalid schemes
        valid, error = validate_avatar_url("ftp://imgur.com/image.jpg")
        assert valid == False
        assert "esquema" in error.lower()
        
        valid, error = validate_avatar_url("file:///etc/passwd")
        assert valid == False
        assert "esquema" in error.lower()
    
    def test_validate_avatar_url_domain_whitelist(self):
        """Test domain whitelist validation"""
        # Allowed domains
        for domain in ALLOWED_AVATAR_DOMAINS:
            valid, _ = validate_avatar_url(f"https://{domain}/image.jpg")
            assert valid == True, f"Domain {domain} should be allowed"
        
        # Disallowed domains
        disallowed_domains = [
            "evil.com",
            "malicious.site",
            "internal.company.com",
            "localhost"
        ]
        
        for domain in disallowed_domains:
            valid, error = validate_avatar_url(f"https://{domain}/image.jpg")
            assert valid == False
            assert "no permitido" in error.lower()
    
    @patch('socket.gethostbyname')
    def test_validate_avatar_url_ip_resolution(self, mock_gethostbyname):
        """Test IP resolution and private IP blocking"""
        # Mock DNS resolution to return private IP
        mock_gethostbyname.return_value = "127.0.0.1"
        
        valid, error = validate_avatar_url("https://imgur.com/image.jpg")
        assert valid == False
        assert "privadas" in error.lower()
        
        # Mock DNS resolution to return public IP
        mock_gethostbyname.return_value = "8.8.8.8"
        
        valid, _ = validate_avatar_url("https://imgur.com/image.jpg")
        assert valid == True
        
        # Mock DNS resolution failure
        mock_gethostbyname.side_effect = socket.gaierror("Name resolution failed")
        
        valid, error = validate_avatar_url("https://imgur.com/image.jpg")
        assert valid == False
        assert "resolver" in error.lower()
    
    def test_validate_avatar_url_file_extensions(self):
        """Test file extension validation"""
        # Valid extensions
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        for ext in valid_extensions:
            with patch('socket.gethostbyname', return_value="8.8.8.8"):
                valid, _ = validate_avatar_url(f"https://imgur.com/image{ext}")
                assert valid == True, f"Extension {ext} should be allowed"
        
        # Invalid extensions for non-Gravatar domains
        with patch('socket.gethostbyname', return_value="8.8.8.8"):
            valid, error = validate_avatar_url("https://imgur.com/file.txt")
            assert valid == False
            assert "extensión" in error.lower()
        
        # Gravatar should allow URLs without explicit extensions
        with patch('socket.gethostbyname', return_value="8.8.8.8"):
            valid, _ = validate_avatar_url("https://gravatar.com/avatar/hash")
            assert valid == True
    
    @patch('requests.get')
    @patch('socket.gethostbyname')
    def test_download_avatar_safely_success(self, mock_gethostbyname, mock_requests_get):
        """Test successful avatar download"""
        # Mock DNS resolution
        mock_gethostbyname.return_value = "8.8.8.8"
        
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_requests_get.return_value = mock_response
        
        success, error, data = download_avatar_safely("https://imgur.com/image.jpg")
        
        assert success == True
        assert error == ""
        assert data == b'fake_image_data'
        
        # Verify request was made with correct parameters
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        assert call_args[1]['timeout'] == 5
        assert call_args[1]['stream'] == True
        assert call_args[1]['allow_redirects'] == False
    
    @patch('requests.get')
    @patch('socket.gethostbyname')
    def test_download_avatar_safely_invalid_content_type(self, mock_gethostbyname, mock_requests_get):
        """Test download failure due to invalid content type"""
        # Mock DNS resolution
        mock_gethostbyname.return_value = "8.8.8.8"
        
        # Mock response with invalid content type
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_requests_get.return_value = mock_response
        
        success, error, data = download_avatar_safely("https://imgur.com/image.jpg")
        
        assert success == False
        assert "contenido no válido" in error.lower()
        assert data == b''
    
    @patch('requests.get')
    @patch('socket.gethostbyname')
    def test_download_avatar_safely_size_limit(self, mock_gethostbyname, mock_requests_get):
        """Test download failure due to size limit"""
        # Mock DNS resolution
        mock_gethostbyname.return_value = "8.8.8.8"
        
        # Mock response with large content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        # Simulate large file by returning chunks that exceed limit
        large_chunk = b'x' * (6 * 1024 * 1024)  # 6MB chunk
        mock_response.iter_content.return_value = [large_chunk]
        mock_requests_get.return_value = mock_response
        
        success, error, data = download_avatar_safely("https://imgur.com/image.jpg")
        
        assert success == False
        assert "demasiado grande" in error.lower()
        assert data == b''
    
    @patch('requests.get')
    def test_download_avatar_safely_invalid_url(self, mock_requests_get):
        """Test download failure due to invalid URL"""
        success, error, data = download_avatar_safely("https://evil.com/image.jpg")
        
        assert success == False
        assert "no permitido" in error.lower()
        assert data == b''
        
        # Verify no HTTP request was made
        mock_requests_get.assert_not_called()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])