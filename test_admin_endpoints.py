"""
Tests for admin endpoints in MedicLab
Verifies admin role validation, security logging, and data access controls
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.main import app
from backend.app.database import get_db, SessionLocal
from backend.app.models import User, Appointment, UserRole, AppointmentStatus
from backend.app.security import create_access_token, create_user_token_data, hash_password

client = TestClient(app)


class TestAdminEndpoints:
    """Test suite for admin endpoints security and functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test data for each test"""
        # Initialize database tables
        from backend.app.database import init_db
        init_db()
        
        db = SessionLocal()
        
        try:
            # Clean up existing test data
            db.query(Appointment).delete()
            db.query(User).delete()
            
            # Create test users
            self.admin_user = User(
                email="admin@mediclab.com",
                password_hash=hash_password("AdminPass123"),
                role=UserRole.ADMIN,
                first_name="Admin",
                last_name="User",
                is_active=True
            )
            
            self.doctor_user = User(
                email="doctor@mediclab.com", 
                password_hash=hash_password("DoctorPass123"),
                role=UserRole.DOCTOR,
                first_name="Dr. María",
                last_name="García",
                is_active=True
            )
            
            self.patient_user = User(
                email="patient@mediclab.com",
                password_hash=hash_password("PatientPass123"),
                role=UserRole.PATIENT,
                first_name="Juan",
                last_name="Pérez",
                is_active=True
            )
            
            db.add_all([self.admin_user, self.doctor_user, self.patient_user])
            db.commit()
            
            # Refresh to get IDs
            db.refresh(self.admin_user)
            db.refresh(self.doctor_user)
            db.refresh(self.patient_user)
            
            # Create test appointment
            self.test_appointment = Appointment(
                patient_id=self.patient_user.id,
                doctor_id=self.doctor_user.id,
                appointment_date=datetime.now() + timedelta(days=1),
                description="Test appointment",
                status=AppointmentStatus.SCHEDULED
            )
            
            db.add(self.test_appointment)
            db.commit()
            db.refresh(self.test_appointment)
            
            # Create JWT tokens
            self.admin_token = create_access_token(
                create_user_token_data(self.admin_user.id, self.admin_user.email, "admin")
            )
            
            self.doctor_token = create_access_token(
                create_user_token_data(self.doctor_user.id, self.doctor_user.email, "doctor")
            )
            
            self.patient_token = create_access_token(
                create_user_token_data(self.patient_user.id, self.patient_user.email, "patient")
            )
            
        finally:
            db.close()
    
    def test_admin_get_all_users_success(self):
        """
        Test successful access to all users by admin
        Requirement 6.1: GET /api/admin/users con verificación de rol admin
        """
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 200
        users = response.json()
        
        # Should return all 3 users
        assert len(users) == 3
        
        # Verify user data structure and no sensitive info
        for user in users:
            assert "id" in user
            assert "email" in user
            assert "role" in user
            assert "first_name" in user
            assert "last_name" in user
            assert "created_at" in user
            assert "is_active" in user
            
            # Requirement 6.4: Excluir información sensible
            assert "password_hash" not in user
            assert "password" not in user
    
    def test_admin_get_all_users_unauthorized_doctor(self):
        """
        Test unauthorized access to users by doctor
        Requirement 6.3: Validación de permisos administrativos
        """
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 403
        assert "Acceso denegado" in response.json()["detail"]
    
    def test_admin_get_all_users_unauthorized_patient(self):
        """
        Test unauthorized access to users by patient
        Requirement 6.3: Validación de permisos administrativos
        """
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        response = client.get("/api/admin/users", headers=headers)
        
        assert response.status_code == 403
        assert "Acceso denegado" in response.json()["detail"]
    
    def test_admin_get_all_users_no_token(self):
        """
        Test access to users without authentication token
        """
        response = client.get("/api/admin/users")
        
        assert response.status_code == 401
    
    def test_admin_get_all_appointments_success(self):
        """
        Test successful access to all appointments by admin
        Requirement 6.2: GET /api/admin/appointments para ver todas las citas del sistema
        """
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.get("/api/admin/appointments", headers=headers)
        
        assert response.status_code == 200
        appointments = response.json()
        
        # Should return at least 1 appointment
        assert len(appointments) >= 1
        
        # Verify appointment data structure
        for appointment in appointments:
            assert "id" in appointment
            assert "patient_id" in appointment
            assert "doctor_id" in appointment
            assert "appointment_date" in appointment
            assert "status" in appointment
            assert "created_at" in appointment
            assert "updated_at" in appointment
            
            # Requirement 6.7: Principio de menor privilegio - include user names
            assert "patient_name" in appointment
            assert "doctor_name" in appointment
    
    def test_admin_get_all_appointments_unauthorized_doctor(self):
        """
        Test unauthorized access to all appointments by doctor
        Requirement 6.3: Validación de permisos administrativos
        """
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        response = client.get("/api/admin/appointments", headers=headers)
        
        assert response.status_code == 403
        assert "Acceso denegado" in response.json()["detail"]
    
    def test_admin_get_all_appointments_unauthorized_patient(self):
        """
        Test unauthorized access to all appointments by patient
        Requirement 6.3: Validación de permisos administrativos
        """
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        response = client.get("/api/admin/appointments", headers=headers)
        
        assert response.status_code == 403
        assert "Acceso denegado" in response.json()["detail"]
    
    def test_admin_get_user_by_id_success(self):
        """
        Test successful access to specific user by admin
        Requirement 6.4: Excluir información sensible
        """
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.get(f"/api/admin/users/{self.patient_user.id}", headers=headers)
        
        assert response.status_code == 200
        user = response.json()
        
        # Verify user data
        assert user["id"] == self.patient_user.id
        assert user["email"] == self.patient_user.email
        assert user["role"] == "patient"
        assert user["first_name"] == self.patient_user.first_name
        assert user["last_name"] == self.patient_user.last_name
        
        # Requirement 6.4: No sensitive information
        assert "password_hash" not in user
        assert "password" not in user
    
    def test_admin_get_user_by_id_not_found(self):
        """
        Test access to non-existent user by admin
        """
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.get("/api/admin/users/99999", headers=headers)
        
        assert response.status_code == 404
        assert "Usuario no encontrado" in response.json()["detail"]
    
    def test_admin_get_appointment_by_id_success(self):
        """
        Test successful access to specific appointment by admin
        """
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.get(f"/api/admin/appointments/{self.test_appointment.id}", headers=headers)
        
        assert response.status_code == 200
        appointment = response.json()
        
        # Verify appointment data
        assert appointment["id"] == self.test_appointment.id
        assert appointment["patient_id"] == self.test_appointment.patient_id
        assert appointment["doctor_id"] == self.test_appointment.doctor_id
        assert appointment["status"] == "scheduled"
        
        # Should include user names
        assert "patient_name" in appointment
        assert "doctor_name" in appointment
        assert "Juan Pérez" in appointment["patient_name"]
        assert "Dr. María García" in appointment["doctor_name"]
    
    def test_admin_get_appointment_by_id_not_found(self):
        """
        Test access to non-existent appointment by admin
        """
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.get("/api/admin/appointments/99999", headers=headers)
        
        assert response.status_code == 404
        assert "Cita no encontrada" in response.json()["detail"]
    
    def test_admin_endpoints_with_invalid_token(self):
        """
        Test admin endpoints with invalid JWT token
        """
        headers = {"Authorization": "Bearer invalid_token"}
        
        # Test users endpoint
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 401
        
        # Test appointments endpoint
        response = client.get("/api/admin/appointments", headers=headers)
        assert response.status_code == 401
    
    def test_admin_endpoints_with_expired_token(self):
        """
        Test admin endpoints with expired JWT token
        """
        # Create expired token (negative expiration)
        expired_token = create_access_token(
            create_user_token_data(self.admin_user.id, self.admin_user.email, "admin"),
            expires_delta=timedelta(seconds=-1)
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        # Test users endpoint
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 401
        
        # Test appointments endpoint  
        response = client.get("/api/admin/appointments", headers=headers)
        assert response.status_code == 401


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])