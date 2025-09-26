"""
OWASP Top 10 Security Tests for MedicLab
Tests specific vulnerabilities from OWASP Top 10 2021
Requirements: 3.3, 2.6, 4.5, 3.2
"""

import pytest
import sys
import os
import sqlite3
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
import requests

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.main import app
from backend.app.database import get_db, Base
from backend.app.models import User, Appointment, UserRole, AppointmentStatus
from backend.app.security import create_access_token, create_user_token_data, hash_password

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_owasp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestSQLInjectionPrevention:
    """
    Test SQL injection prevention through parameterized queries
    OWASP Top 10 #3: Injection
    Requirements: 3.3
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Setup clean test database for each test"""
        Base.metadata.create_all(bind=engine)
        
        # Create test users and appointments
        db = TestingSessionLocal()
        
        self.patient = User(
            email="patient_sql@test.com",
            password_hash=hash_password("PatientPass123"),
            role=UserRole.PATIENT,
            first_name="Juan",
            last_name="Pérez",
            is_active=True
        )
        
        self.doctor = User(
            email="doctor_sql@test.com",
            password_hash=hash_password("DoctorPass123"),
            role=UserRole.DOCTOR,
            first_name="Dra. María",
            last_name="García",
            is_active=True
        )
        
        db.add_all([self.patient, self.doctor])
        db.commit()
        db.refresh(self.patient)
        db.refresh(self.doctor)
        
        self.appointment = Appointment(
            patient_id=self.patient.id,
            doctor_id=self.doctor.id,
            appointment_date=datetime.now() + timedelta(days=1),
            description="Test appointment",
            status=AppointmentStatus.SCHEDULED
        )
        
        db.add(self.appointment)
        db.commit()
        db.refresh(self.appointment)
        
        # Create tokens
        self.patient_token = create_access_token(
            create_user_token_data(self.patient.id, self.patient.email, "patient")
        )
        self.doctor_token = create_access_token(
            create_user_token_data(self.doctor.id, self.doctor.email, "doctor")
        )
        
        db.close()
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_sql_injection_in_appointment_description(self):
        """Test SQL injection attempts in appointment description field"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # SQL injection payloads
        malicious_descriptions = [
            "'; DROP TABLE appointments; --",
            "' OR '1'='1",
            "'; UPDATE users SET role='admin' WHERE id=1; --",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users (email, role) VALUES ('hacker@evil.com', 'admin'); --"
        ]
        
        for malicious_desc in malicious_descriptions:
            appointment_data = {
                "doctor_id": self.doctor.id,
                "appointment_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "description": malicious_desc
            }
            
            response = client.post("/api/appointments/", json=appointment_data, headers=headers)
            
            # Should either succeed (storing the malicious string safely) or fail with validation error
            # But should NOT cause SQL injection
            assert response.status_code in [200, 201, 400, 422]
            
            # Verify database integrity - tables should still exist
            db = TestingSessionLocal()
            try:
                # Check that users table still exists and has expected data
                users = db.query(User).all()
                assert len(users) >= 2  # Our test users should still exist
                
                # Check that appointments table still exists
                appointments = db.query(Appointment).all()
                assert len(appointments) >= 1  # Original appointment should exist
                
                # Verify no unauthorized admin users were created
                admin_users = db.query(User).filter(User.role == UserRole.ADMIN).all()
                assert len(admin_users) == 0  # No admin users should exist from injection
                
            finally:
                db.close()
    
    def test_sql_injection_in_user_registration(self):
        """Test SQL injection attempts in user registration fields"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin'; UPDATE users SET role='admin' WHERE email='admin@test.com'; --",
            "' OR 1=1 --",
            "'; INSERT INTO users (email, role) VALUES ('injected@evil.com', 'admin'); --"
        ]
        
        for malicious_input in malicious_inputs:
            registration_data = {
                "email": f"test_{hash(malicious_input)}@test.com",  # Unique email
                "password": "ValidPass123",
                "first_name": malicious_input,  # Inject in first_name
                "last_name": "Test",
                "role": "patient"
            }
            
            response = client.post("/api/auth/register", json=registration_data)
            
            # Should either succeed or fail with validation error, but not cause injection
            assert response.status_code in [201, 400, 422, 429]  # 429 for rate limiting
            
            # Verify database integrity
            db = TestingSessionLocal()
            try:
                # Check that no unauthorized admin users were created
                admin_users = db.query(User).filter(User.role == UserRole.ADMIN).all()
                assert len(admin_users) == 0
                
                # Check that users table still exists
                all_users = db.query(User).all()
                assert len(all_users) >= 2  # At least our original test users
                
            finally:
                db.close()
    
    def test_sql_injection_in_login_email(self):
        """Test SQL injection attempts in login email field"""
        malicious_emails = [
            "' OR '1'='1' --",
            "admin@test.com'; DROP TABLE users; --",
            "' UNION SELECT password_hash FROM users WHERE role='admin' --"
        ]
        
        for malicious_email in malicious_emails:
            login_data = {
                "email": malicious_email,
                "password": "AnyPassword123"
            }
            
            response = client.post("/api/auth/login", json=login_data)
            
            # Should fail authentication, not cause injection
            assert response.status_code in [401, 400, 422, 429]  # 429 for rate limiting
            
            # Verify database integrity
            db = TestingSessionLocal()
            try:
                # Check that users table still exists
                users = db.query(User).all()
                assert len(users) >= 2  # Our test users should still exist
                
            finally:
                db.close()
    
    def test_parameterized_queries_in_appointment_filtering(self):
        """Test that appointment filtering uses parameterized queries"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # This should only return appointments for the authenticated patient
        response = client.get("/api/appointments/", headers=headers)
        assert response.status_code == 200
        
        appointments = response.json()
        # Should only see patient's own appointments
        for appointment in appointments:
            assert appointment["patient_id"] == self.patient.id
    
    def test_database_connection_integrity_after_injection_attempts(self):
        """Test that database connection remains stable after injection attempts"""
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        
        # Make multiple requests with potential injection payloads
        injection_payloads = [
            "'; DROP DATABASE mediclab; --",
            "' OR 1=1; DELETE FROM appointments; --",
            "'; SHUTDOWN; --"
        ]
        
        for payload in injection_payloads:
            # Try injection in appointment update
            update_data = {
                "description": payload,
                "status": "completed"
            }
            
            response = client.put(f"/api/appointments/{self.appointment.id}", 
                                json=update_data, headers=headers)
            
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
        
        # Verify database is still functional
        db = TestingSessionLocal()
        try:
            # Should be able to query normally
            users = db.query(User).all()
            appointments = db.query(Appointment).all()
            
            assert len(users) >= 2
            assert len(appointments) >= 1
            
        finally:
            db.close()


class TestBrokenAccessControl:
    """
    Test broken access control vulnerabilities
    OWASP Top 10 #1: Broken Access Control
    Requirements: 2.6
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_users(self):
        """Setup test users with different roles and data"""
        Base.metadata.create_all(bind=engine)
        
        db = TestingSessionLocal()
        
        # Create multiple patients
        self.patient1 = User(
            email="patient1@test.com",
            password_hash=hash_password("Patient1Pass123"),
            role=UserRole.PATIENT,
            first_name="Juan",
            last_name="Pérez",
            is_active=True
        )
        
        self.patient2 = User(
            email="patient2@test.com",
            password_hash=hash_password("Patient2Pass123"),
            role=UserRole.PATIENT,
            first_name="María",
            last_name="González",
            is_active=True
        )
        
        # Create multiple doctors
        self.doctor1 = User(
            email="doctor1@test.com",
            password_hash=hash_password("Doctor1Pass123"),
            role=UserRole.DOCTOR,
            first_name="Dr. Carlos",
            last_name="López",
            is_active=True
        )
        
        self.doctor2 = User(
            email="doctor2@test.com",
            password_hash=hash_password("Doctor2Pass123"),
            role=UserRole.DOCTOR,
            first_name="Dra. Ana",
            last_name="Martín",
            is_active=True
        )
        
        self.admin = User(
            email="admin@test.com",
            password_hash=hash_password("AdminPass123"),
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="Sistema",
            is_active=True
        )
        
        db.add_all([self.patient1, self.patient2, self.doctor1, self.doctor2, self.admin])
        db.commit()
        
        # Refresh to get IDs
        for user in [self.patient1, self.patient2, self.doctor1, self.doctor2, self.admin]:
            db.refresh(user)
        
        # Create appointments with different patient-doctor combinations
        self.appointment1 = Appointment(
            patient_id=self.patient1.id,
            doctor_id=self.doctor1.id,
            appointment_date=datetime.now() + timedelta(days=1),
            description="Patient1 with Doctor1",
            status=AppointmentStatus.SCHEDULED
        )
        
        self.appointment2 = Appointment(
            patient_id=self.patient2.id,
            doctor_id=self.doctor2.id,
            appointment_date=datetime.now() + timedelta(days=2),
            description="Patient2 with Doctor2",
            status=AppointmentStatus.SCHEDULED
        )
        
        self.appointment3 = Appointment(
            patient_id=self.patient1.id,
            doctor_id=self.doctor2.id,
            appointment_date=datetime.now() + timedelta(days=3),
            description="Patient1 with Doctor2",
            status=AppointmentStatus.SCHEDULED
        )
        
        db.add_all([self.appointment1, self.appointment2, self.appointment3])
        db.commit()
        
        for appointment in [self.appointment1, self.appointment2, self.appointment3]:
            db.refresh(appointment)
        
        # Create tokens
        self.patient1_token = create_access_token(
            create_user_token_data(self.patient1.id, self.patient1.email, "patient")
        )
        self.patient2_token = create_access_token(
            create_user_token_data(self.patient2.id, self.patient2.email, "patient")
        )
        self.doctor1_token = create_access_token(
            create_user_token_data(self.doctor1.id, self.doctor1.email, "doctor")
        )
        self.doctor2_token = create_access_token(
            create_user_token_data(self.doctor2.id, self.doctor2.email, "doctor")
        )
        self.admin_token = create_access_token(
            create_user_token_data(self.admin.id, self.admin.email, "admin")
        )
        
        db.close()
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_patient_cannot_access_other_patient_appointments(self):
        """Test that patients cannot access other patients' appointments"""
        headers = {"Authorization": f"Bearer {self.patient1_token}"}
        response = client.get("/api/appointments/", headers=headers)
        
        assert response.status_code == 200
        appointments = response.json()
        
        # Patient1 should only see their own appointments
        for appointment in appointments:
            assert appointment["patient_id"] == self.patient1.id
        
        # Should see 2 appointments (appointment1 and appointment3)
        patient1_appointments = [a for a in appointments if a["patient_id"] == self.patient1.id]
        assert len(patient1_appointments) == 2
    
    def test_doctor_cannot_access_other_doctor_appointments(self):
        """Test that doctors cannot access other doctors' appointments"""
        headers = {"Authorization": f"Bearer {self.doctor1_token}"}
        response = client.get("/api/appointments/", headers=headers)
        
        assert response.status_code == 200
        appointments = response.json()
        
        # Doctor1 should only see appointments where they are the doctor
        for appointment in appointments:
            assert appointment["doctor_id"] == self.doctor1.id
        
        # Should see 1 appointment (appointment1)
        doctor1_appointments = [a for a in appointments if a["doctor_id"] == self.doctor1.id]
        assert len(doctor1_appointments) == 1
    
    def test_patient_cannot_update_appointments(self):
        """Test that patients cannot update appointments"""
        headers = {"Authorization": f"Bearer {self.patient1_token}"}
        
        update_data = {
            "description": "Patient trying to update",
            "status": "completed"
        }
        
        response = client.put(f"/api/appointments/{self.appointment1.id}", 
                            json=update_data, headers=headers)
        
        assert response.status_code == 403
        error_response = response.json()
        assert "error" in error_response
    
    def test_doctor_cannot_update_other_doctor_appointments(self):
        """Test that doctors cannot update other doctors' appointments"""
        headers = {"Authorization": f"Bearer {self.doctor1_token}"}
        
        update_data = {
            "description": "Doctor1 trying to update Doctor2's appointment",
            "status": "completed"
        }
        
        # Try to update appointment2 (belongs to doctor2)
        response = client.put(f"/api/appointments/{self.appointment2.id}", 
                            json=update_data, headers=headers)
        
        assert response.status_code == 403
        error_response = response.json()
        assert "error" in error_response
    
    def test_patient_cannot_access_admin_endpoints(self):
        """Test that patients cannot access admin-only endpoints"""
        headers = {"Authorization": f"Bearer {self.patient1_token}"}
        
        # Try to access admin users endpoint
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 403
        
        # Try to access admin appointments endpoint
        response = client.get("/api/admin/appointments", headers=headers)
        assert response.status_code == 403
    
    def test_doctor_cannot_access_admin_endpoints(self):
        """Test that doctors cannot access admin-only endpoints"""
        headers = {"Authorization": f"Bearer {self.doctor1_token}"}
        
        # Try to access admin users endpoint
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 403
        
        # Try to access admin appointments endpoint
        response = client.get("/api/admin/appointments", headers=headers)
        assert response.status_code == 403
    
    def test_horizontal_privilege_escalation_prevention(self):
        """Test prevention of horizontal privilege escalation"""
        # Patient1 tries to access Patient2's profile by manipulating user ID
        headers = {"Authorization": f"Bearer {self.patient1_token}"}
        
        # Try to access another user's profile (if such endpoint existed)
        # This tests the principle - in our current API, /api/users/me only returns current user
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        # Should only return patient1's data
        assert user_data["id"] == self.patient1.id
        assert user_data["email"] == self.patient1.email
    
    def test_vertical_privilege_escalation_prevention(self):
        """Test prevention of vertical privilege escalation"""
        # Patient tries to perform admin actions
        headers = {"Authorization": f"Bearer {self.patient1_token}"}
        
        # Try to access all users (admin function)
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 403
        
        # Try to access all appointments (admin function)
        response = client.get("/api/admin/appointments", headers=headers)
        assert response.status_code == 403
    
    def test_insecure_direct_object_reference_prevention(self):
        """Test prevention of insecure direct object references"""
        headers = {"Authorization": f"Bearer {self.patient1_token}"}
        
        # Patient1 tries to access appointment that belongs to Patient2
        # by directly referencing the appointment ID
        response = client.get(f"/api/appointments/{self.appointment2.id}", headers=headers)
        
        # Should either return 403 (forbidden) or 404 (not found)
        # Both are acceptable as they prevent access
        assert response.status_code in [403, 404]
    
    def test_admin_can_access_all_resources(self):
        """Test that admin can access all resources (positive test)"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Admin should be able to access all users
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 5  # All our test users
        
        # Admin should be able to access all appointments
        response = client.get("/api/admin/appointments", headers=headers)
        assert response.status_code == 200
        appointments = response.json()
        assert len(appointments) == 3  # All our test appointments


class TestSSRFProtection:
    """
    Test Server-Side Request Forgery (SSRF) protection
    OWASP Top 10 #10: Server-Side Request Forgery
    Requirements: 4.5
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_user(self):
        """Setup test user for avatar update tests"""
        Base.metadata.create_all(bind=engine)
        
        db = TestingSessionLocal()
        
        self.user = User(
            email="ssrf_test@test.com",
            password_hash=hash_password("SSRFTest123"),
            role=UserRole.PATIENT,
            first_name="SSRF",
            last_name="Test",
            is_active=True
        )
        
        db.add(self.user)
        db.commit()
        db.refresh(self.user)
        
        self.user_token = create_access_token(
            create_user_token_data(self.user.id, self.user.email, "patient")
        )
        
        db.close()
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_ssrf_protection_localhost_urls(self):
        """Test SSRF protection against localhost URLs"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        malicious_urls = [
            "http://127.0.0.1:8080/admin",
            "http://localhost:3000/internal",
            "https://127.0.0.1:22/ssh",
            "http://0.0.0.0:8000/api",
            "https://localhost/admin/users"
        ]
        
        for url in malicious_urls:
            avatar_data = {"avatar_url": url}
            response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
            
            # Should reject the request
            assert response.status_code == 400
            error_response = response.json()
            assert "error" in error_response
    
    def test_ssrf_protection_private_ip_ranges(self):
        """Test SSRF protection against private IP ranges"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        private_ip_urls = [
            "http://10.0.0.1/internal",
            "https://172.16.0.1:8080/admin",
            "http://192.168.1.1/router",
            "https://169.254.169.254/metadata",  # AWS metadata service
            "http://10.10.10.10:22/ssh"
        ]
        
        for url in private_ip_urls:
            avatar_data = {"avatar_url": url}
            response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
            
            # Should reject the request
            assert response.status_code == 400
            error_response = response.json()
            assert "error" in error_response
    
    def test_ssrf_protection_cloud_metadata_services(self):
        """Test SSRF protection against cloud metadata services"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        metadata_urls = [
            "http://169.254.169.254/latest/meta-data/",  # AWS
            "http://metadata.google.internal/computeMetadata/v1/",  # GCP
            "http://169.254.169.254/metadata/instance",  # Azure
            "http://100.100.100.200/latest/meta-data/"  # Alibaba Cloud
        ]
        
        for url in metadata_urls:
            avatar_data = {"avatar_url": url}
            response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
            
            # Should reject the request
            assert response.status_code == 400
            error_response = response.json()
            assert "error" in error_response
    
    def test_ssrf_protection_invalid_schemes(self):
        """Test SSRF protection against invalid URL schemes"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        invalid_scheme_urls = [
            "ftp://imgur.com/avatar.jpg",
            "file:///etc/passwd",
            "gopher://evil.com:70/",
            "ldap://internal.company.com/",
            "dict://127.0.0.1:11211/"
        ]
        
        for url in invalid_scheme_urls:
            avatar_data = {"avatar_url": url}
            response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
            
            # Should reject the request
            assert response.status_code == 400
            error_response = response.json()
            assert "error" in error_response
    
    def test_ssrf_protection_domain_whitelist(self):
        """Test SSRF protection domain whitelist enforcement"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test non-whitelisted domains
        non_whitelisted_urls = [
            "https://evil.com/avatar.jpg",
            "https://malicious-site.org/image.png",
            "https://attacker.net/profile.gif",
            "https://suspicious-domain.com/avatar.jpeg"
        ]
        
        for url in non_whitelisted_urls:
            avatar_data = {"avatar_url": url}
            response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
            
            # Should reject the request
            assert response.status_code == 400
            error_response = response.json()
            assert "error" in error_response
            assert "Dominio no permitido" in error_response["error"]["message"]
    
    @patch('requests.get')
    def test_ssrf_protection_valid_domains_allowed(self, mock_get):
        """Test that valid whitelisted domains are allowed"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_get.return_value = mock_response
        
        valid_urls = [
            "https://imgur.com/avatar.jpg",
            "https://i.imgur.com/profile.png",
            "https://gravatar.com/avatar/hash.jpg"
        ]
        
        for url in valid_urls:
            with patch('socket.gethostbyname', return_value='1.2.3.4'):  # Mock public IP
                avatar_data = {"avatar_url": url}
                response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
                
                # Should accept the request
                assert response.status_code == 200
    
    def test_ssrf_protection_dns_rebinding_prevention(self):
        """Test protection against DNS rebinding attacks"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # URLs that might resolve to private IPs through DNS manipulation
        dns_rebinding_urls = [
            "https://imgur.com.evil.com/avatar.jpg",  # Subdomain confusion
            "https://127.0.0.1.imgur.com/avatar.jpg",  # IP in subdomain
            "https://imgur.com@127.0.0.1/avatar.jpg"   # URL with embedded IP
        ]
        
        for url in dns_rebinding_urls:
            avatar_data = {"avatar_url": url}
            response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
            
            # Should reject the request due to domain validation
            assert response.status_code == 400
            error_response = response.json()
            assert "error" in error_response
    
    @patch('requests.get')
    def test_ssrf_protection_timeout_enforcement(self, mock_get):
        """Test that request timeouts are enforced to prevent DoS"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Mock timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with patch('socket.gethostbyname', return_value='1.2.3.4'):
            avatar_data = {"avatar_url": "https://imgur.com/slow-response.jpg"}
            response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
            
            # Should handle timeout gracefully
            assert response.status_code == 400
            error_response = response.json()
            assert "error" in error_response
    
    @patch('requests.get')
    def test_ssrf_protection_content_type_validation(self, mock_get):
        """Test that content type validation prevents non-image responses"""
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Mock response with non-image content type
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}  # Not an image
        mock_get.return_value = mock_response
        
        with patch('socket.gethostbyname', return_value='1.2.3.4'):
            avatar_data = {"avatar_url": "https://imgur.com/malicious.html"}
            response = client.put("/api/users/me/avatar", json=avatar_data, headers=headers)
            
            # Should reject non-image content
            assert response.status_code == 400
            error_response = response.json()
            assert "error" in error_response


class TestInputValidationAndBusinessRules:
    """
    Test input validation and critical business rules
    OWASP Top 10 #3: Injection & #4: Insecure Design
    Requirements: 3.2
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test data for validation tests"""
        Base.metadata.create_all(bind=engine)
        
        db = TestingSessionLocal()
        
        self.patient = User(
            email="validation_test@test.com",
            password_hash=hash_password("ValidationTest123"),
            role=UserRole.PATIENT,
            first_name="Validation",
            last_name="Test",
            is_active=True
        )
        
        self.doctor = User(
            email="doctor_validation@test.com",
            password_hash=hash_password("DoctorValidation123"),
            role=UserRole.DOCTOR,
            first_name="Dr. Validation",
            last_name="Test",
            is_active=True
        )
        
        db.add_all([self.patient, self.doctor])
        db.commit()
        
        for user in [self.patient, self.doctor]:
            db.refresh(user)
        
        self.patient_token = create_access_token(
            create_user_token_data(self.patient.id, self.patient.email, "patient")
        )
        self.doctor_token = create_access_token(
            create_user_token_data(self.doctor.id, self.doctor.email, "doctor")
        )
        
        db.close()
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_appointment_past_date_validation(self):
        """Test critical business rule: appointments cannot be in the past"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # Try to create appointment with past date
        past_dates = [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(hours=1),
            datetime.now() - timedelta(minutes=30)
        ]
        
        for past_date in past_dates:
            appointment_data = {
                "doctor_id": self.doctor.id,
                "appointment_date": past_date.isoformat(),
                "description": "Past appointment test"
            }
            
            response = client.post("/api/appointments/", json=appointment_data, headers=headers)
            
            # Should reject past dates
            assert response.status_code in [400, 422]
            error_response = response.json()
            assert "error" in error_response
    
    def test_appointment_future_date_validation(self):
        """Test that future dates are accepted (positive test)"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # Create appointment with future date
        future_date = datetime.now() + timedelta(days=1)
        appointment_data = {
            "doctor_id": self.doctor.id,
            "appointment_date": future_date.isoformat(),
            "description": "Future appointment test"
        }
        
        response = client.post("/api/appointments/", json=appointment_data, headers=headers)
        
        # Should accept future dates
        assert response.status_code in [200, 201]
    
    def test_user_registration_email_validation(self):
        """Test email format validation in user registration"""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user.domain.com",
            "user@domain",
            "user space@domain.com"
        ]
        
        for invalid_email in invalid_emails:
            registration_data = {
                "email": invalid_email,
                "password": "ValidPass123",
                "first_name": "Test",
                "last_name": "User",
                "role": "patient"
            }
            
            response = client.post("/api/auth/register", json=registration_data)
            
            # Should reject invalid emails
            assert response.status_code in [400, 422, 429]  # 429 for rate limiting
    
    def test_user_registration_password_strength_validation(self):
        """Test password strength validation"""
        weak_passwords = [
            "weak",           # Too short
            "password",       # No uppercase, no numbers
            "PASSWORD",       # No lowercase, no numbers
            "Password",       # No numbers
            "12345678",       # No letters
            "Pass123"         # Too short
        ]
        
        for weak_password in weak_passwords:
            registration_data = {
                "email": f"test_{hash(weak_password)}@test.com",
                "password": weak_password,
                "first_name": "Test",
                "last_name": "User",
                "role": "patient"
            }
            
            response = client.post("/api/auth/register", json=registration_data)
            
            # Should reject weak passwords
            assert response.status_code in [400, 422, 429]  # 429 for rate limiting
    
    def test_appointment_description_length_validation(self):
        """Test appointment description length limits"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # Test extremely long description
        very_long_description = "A" * 1000  # 1000 characters
        
        appointment_data = {
            "doctor_id": self.doctor.id,
            "appointment_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "description": very_long_description
        }
        
        response = client.post("/api/appointments/", json=appointment_data, headers=headers)
        
        # Should either accept (if within limits) or reject with validation error
        assert response.status_code in [200, 201, 400, 422]
    
    def test_appointment_required_fields_validation(self):
        """Test that required fields are validated"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # Test missing required fields
        incomplete_data_sets = [
            {"doctor_id": self.doctor.id},  # Missing date and description
            {"appointment_date": (datetime.now() + timedelta(days=1)).isoformat()},  # Missing doctor_id
            {"description": "Test appointment"},  # Missing doctor_id and date
            {}  # Missing everything
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = client.post("/api/appointments/", json=incomplete_data, headers=headers)
            
            # Should reject incomplete data
            assert response.status_code in [400, 422]
            error_response = response.json()
            assert "error" in error_response
    
    def test_user_name_validation(self):
        """Test user name field validation"""
        invalid_names = [
            "",              # Empty name
            " ",             # Whitespace only
            "A" * 200,       # Too long
            "123",           # Numbers only
            "!@#$%"          # Special characters only
        ]
        
        for invalid_name in invalid_names:
            registration_data = {
                "email": f"test_{hash(invalid_name)}@test.com",
                "password": "ValidPass123",
                "first_name": invalid_name,
                "last_name": "ValidLastName",
                "role": "patient"
            }
            
            response = client.post("/api/auth/register", json=registration_data)
            
            # Should reject invalid names
            assert response.status_code in [400, 422, 429]  # 429 for rate limiting
    
    def test_appointment_doctor_existence_validation(self):
        """Test that appointments can only be created with existing doctors"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # Try to create appointment with non-existent doctor
        appointment_data = {
            "doctor_id": 99999,  # Non-existent doctor ID
            "appointment_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "description": "Test appointment with invalid doctor"
        }
        
        response = client.post("/api/appointments/", json=appointment_data, headers=headers)
        
        # Should reject non-existent doctor
        assert response.status_code in [400, 404, 422]
        error_response = response.json()
        assert "error" in error_response
    
    def test_data_sanitization_in_responses(self):
        """Test that sensitive data is sanitized in API responses"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # Get user profile
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        
        # Verify sensitive fields are not exposed
        sensitive_fields = ["password", "password_hash", "secret", "token"]
        for field in sensitive_fields:
            assert field not in user_data
            assert field not in str(user_data).lower()
    
    def test_xss_prevention_in_text_fields(self):
        """Test XSS prevention in text input fields"""
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>"
        ]
        
        for xss_payload in xss_payloads:
            appointment_data = {
                "doctor_id": self.doctor.id,
                "appointment_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "description": xss_payload
            }
            
            response = client.post("/api/appointments/", json=appointment_data, headers=headers)
            
            # Should either sanitize the input or reject it
            if response.status_code in [200, 201]:
                # If accepted, verify the response doesn't contain executable script
                appointment = response.json()
                # The description should be sanitized or escaped
                assert "<script>" not in appointment.get("description", "")
                assert "javascript:" not in appointment.get("description", "")


if __name__ == "__main__":
    print("Running OWASP Top 10 Security Tests for MedicLab...")
    pytest.main([__file__, "-v", "--tb=short"])