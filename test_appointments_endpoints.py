"""
Test para endpoints de citas médicas
Verifica la implementación de GET y POST /api/appointments para pacientes
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.main import app
from backend.app.database import get_db, init_db
from backend.app.models import User, UserRole, Appointment, AppointmentStatus
from backend.app.security import create_access_token, create_user_token_data
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurar base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_appointments.db"
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

@pytest.fixture(scope="function")
def setup_test_db():
    """Configurar base de datos de prueba"""
    # Crear tablas
    from backend.app.database import Base
    Base.metadata.create_all(bind=engine)
    
    # Crear usuarios de prueba
    db = TestingSessionLocal()
    
    # Paciente de prueba
    patient = User(
        email="paciente@test.com",
        password_hash="$2b$12$test_hash",
        role=UserRole.PATIENT,
        first_name="Juan",
        last_name="Pérez",
        is_active=True
    )
    
    # Médico de prueba
    doctor = User(
        email="doctor@test.com",
        password_hash="$2b$12$test_hash",
        role=UserRole.DOCTOR,
        first_name="Dra. María",
        last_name="García",
        is_active=True
    )
    
    # Admin de prueba
    admin = User(
        email="admin@test.com",
        password_hash="$2b$12$test_hash",
        role=UserRole.ADMIN,
        first_name="Admin",
        last_name="Sistema",
        is_active=True
    )
    
    db.add_all([patient, doctor, admin])
    db.commit()
    db.refresh(patient)
    db.refresh(doctor)
    db.refresh(admin)
    
    # Crear cita de prueba
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=datetime.now() + timedelta(days=1),
        description="Consulta de prueba",
        status=AppointmentStatus.SCHEDULED
    )
    
    db.add(appointment)
    db.commit()
    
    yield {
        "patient": patient,
        "doctor": doctor,
        "admin": admin,
        "appointment": appointment
    }
    
    # Limpiar base de datos
    db.close()
    Base.metadata.drop_all(bind=engine)

def create_test_token(user_id: int, email: str, role: str):
    """Crear token JWT de prueba"""
    token_data = create_user_token_data(user_id, email, role)
    return create_access_token(token_data)

def test_get_appointments_as_patient(setup_test_db):
    """Test: Paciente obtiene solo sus propias citas"""
    test_data = setup_test_db
    patient = test_data["patient"]
    
    # Crear token de paciente
    token = create_test_token(patient.id, patient.email, patient.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Hacer request
    response = client.get("/api/appointments/", headers=headers)
    
    # Verificar respuesta
    assert response.status_code == 200
    appointments = response.json()
    assert len(appointments) == 1
    assert appointments[0]["patient_id"] == patient.id
    assert appointments[0]["patient_name"] == "Juan Pérez"

def test_get_appointments_as_doctor(setup_test_db):
    """Test: Médico obtiene solo sus citas asignadas"""
    test_data = setup_test_db
    doctor = test_data["doctor"]
    
    # Crear token de médico
    token = create_test_token(doctor.id, doctor.email, doctor.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Hacer request
    response = client.get("/api/appointments/", headers=headers)
    
    # Verificar respuesta
    assert response.status_code == 200
    appointments = response.json()
    assert len(appointments) == 1
    assert appointments[0]["doctor_id"] == doctor.id
    assert appointments[0]["doctor_name"] == "Dra. María García"

def test_get_appointments_as_admin(setup_test_db):
    """Test: Admin obtiene todas las citas"""
    test_data = setup_test_db
    admin = test_data["admin"]
    
    # Crear token de admin
    token = create_test_token(admin.id, admin.email, admin.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Hacer request
    response = client.get("/api/appointments/", headers=headers)
    
    # Verificar respuesta
    assert response.status_code == 200
    appointments = response.json()
    assert len(appointments) == 1  # Solo hay una cita en la BD de prueba

def test_create_appointment_as_patient(setup_test_db):
    """Test: Paciente crea cita para sí mismo"""
    test_data = setup_test_db
    patient = test_data["patient"]
    doctor = test_data["doctor"]
    
    # Crear token de paciente
    token = create_test_token(patient.id, patient.email, patient.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Datos de la nueva cita
    appointment_data = {
        "doctor_id": doctor.id,
        "appointment_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "description": "Nueva consulta de prueba"
    }
    
    # Hacer request
    response = client.post("/api/appointments/", json=appointment_data, headers=headers)
    
    # Verificar respuesta
    assert response.status_code == 201
    appointment = response.json()
    assert appointment["patient_id"] == patient.id
    assert appointment["doctor_id"] == doctor.id
    assert appointment["description"] == "Nueva consulta de prueba"
    assert appointment["status"] == "scheduled"

def test_create_appointment_invalid_doctor(setup_test_db):
    """Test: Error al crear cita con médico inválido"""
    test_data = setup_test_db
    patient = test_data["patient"]
    
    # Crear token de paciente
    token = create_test_token(patient.id, patient.email, patient.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Datos con médico inválido
    appointment_data = {
        "doctor_id": 999,  # ID que no existe
        "appointment_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "description": "Consulta con médico inexistente"
    }
    
    # Hacer request
    response = client.post("/api/appointments/", json=appointment_data, headers=headers)
    
    # Verificar error
    assert response.status_code == 400
    assert "médico especificado no existe" in response.json()["detail"]

def test_create_appointment_past_date(setup_test_db):
    """Test: Error al crear cita con fecha en el pasado"""
    test_data = setup_test_db
    patient = test_data["patient"]
    doctor = test_data["doctor"]
    
    # Crear token de paciente
    token = create_test_token(patient.id, patient.email, patient.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Datos con fecha en el pasado
    appointment_data = {
        "doctor_id": doctor.id,
        "appointment_date": (datetime.now() - timedelta(days=1)).isoformat(),
        "description": "Cita en el pasado"
    }
    
    # Hacer request
    response = client.post("/api/appointments/", json=appointment_data, headers=headers)
    
    # Verificar error de validación
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("fecha de la cita debe ser en el futuro" in str(error) for error in error_detail)

def test_update_appointment_as_doctor(setup_test_db):
    """Test: Médico actualiza su propia cita"""
    test_data = setup_test_db
    doctor = test_data["doctor"]
    appointment = test_data["appointment"]
    
    # Crear token de médico
    token = create_test_token(doctor.id, doctor.email, doctor.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Datos de actualización
    update_data = {
        "description": "Consulta actualizada por médico",
        "status": "completed"
    }
    
    # Hacer request
    response = client.put(f"/api/appointments/{appointment.id}", json=update_data, headers=headers)
    
    # Verificar respuesta
    assert response.status_code == 200
    updated_appointment = response.json()
    assert updated_appointment["description"] == "Consulta actualizada por médico"
    assert updated_appointment["status"] == "completed"
    assert updated_appointment["doctor_id"] == doctor.id

def test_update_appointment_as_admin(setup_test_db):
    """Test: Admin actualiza cualquier cita"""
    test_data = setup_test_db
    admin = test_data["admin"]
    appointment = test_data["appointment"]
    
    # Crear token de admin
    token = create_test_token(admin.id, admin.email, admin.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Datos de actualización
    update_data = {
        "status": "cancelled",
        "description": "Cita cancelada por administrador"
    }
    
    # Hacer request
    response = client.put(f"/api/appointments/{appointment.id}", json=update_data, headers=headers)
    
    # Verificar respuesta
    assert response.status_code == 200
    updated_appointment = response.json()
    assert updated_appointment["status"] == "cancelled"
    assert updated_appointment["description"] == "Cita cancelada por administrador"

def test_update_appointment_unauthorized_doctor(setup_test_db):
    """Test: Médico no puede actualizar cita de otro médico"""
    test_data = setup_test_db
    appointment = test_data["appointment"]
    
    # Crear otro médico
    db = TestingSessionLocal()
    other_doctor = User(
        email="otro_doctor@test.com",
        password_hash="$2b$12$test_hash",
        role=UserRole.DOCTOR,
        first_name="Dr. Carlos",
        last_name="López",
        is_active=True
    )
    db.add(other_doctor)
    db.commit()
    db.refresh(other_doctor)
    
    # Crear token del otro médico
    token = create_test_token(other_doctor.id, other_doctor.email, other_doctor.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Intentar actualizar cita que no le pertenece
    update_data = {
        "description": "Intento de actualización no autorizada"
    }
    
    response = client.put(f"/api/appointments/{appointment.id}", json=update_data, headers=headers)
    
    # Verificar error de autorización
    assert response.status_code == 403
    assert "No tiene permisos para actualizar esta cita" in response.json()["detail"]
    
    db.close()

def test_update_appointment_as_patient_forbidden(setup_test_db):
    """Test: Paciente no puede actualizar citas"""
    test_data = setup_test_db
    patient = test_data["patient"]
    appointment = test_data["appointment"]
    
    # Crear token de paciente
    token = create_test_token(patient.id, patient.email, patient.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Intentar actualizar cita
    update_data = {
        "description": "Intento de actualización por paciente"
    }
    
    response = client.put(f"/api/appointments/{appointment.id}", json=update_data, headers=headers)
    
    # Verificar error de autorización
    assert response.status_code == 403
    assert "No tiene permisos para actualizar citas" in response.json()["detail"]

def test_update_nonexistent_appointment(setup_test_db):
    """Test: Error al actualizar cita inexistente"""
    test_data = setup_test_db
    doctor = test_data["doctor"]
    
    # Crear token de médico
    token = create_test_token(doctor.id, doctor.email, doctor.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Intentar actualizar cita inexistente
    update_data = {
        "description": "Actualización de cita inexistente"
    }
    
    response = client.put("/api/appointments/999", json=update_data, headers=headers)
    
    # Verificar error
    assert response.status_code == 404
    assert "Cita no encontrada" in response.json()["detail"]

def test_update_appointment_with_past_date(setup_test_db):
    """Test: Error al actualizar cita con fecha en el pasado"""
    test_data = setup_test_db
    doctor = test_data["doctor"]
    appointment = test_data["appointment"]
    
    # Crear token de médico
    token = create_test_token(doctor.id, doctor.email, doctor.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Intentar actualizar con fecha en el pasado
    update_data = {
        "appointment_date": (datetime.now() - timedelta(days=1)).isoformat()
    }
    
    response = client.put(f"/api/appointments/{appointment.id}", json=update_data, headers=headers)
    
    # Verificar error de validación
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("fecha de la cita debe ser en el futuro" in str(error) for error in error_detail)

def test_unauthorized_access(setup_test_db):
    """Test: Error al acceder sin token"""
    # Hacer request sin token
    response = client.get("/api/appointments/")
    
    # Verificar error de autenticación (403 es correcto para HTTPBearer sin header)
    assert response.status_code == 403

if __name__ == "__main__":
    print("Ejecutando tests de endpoints de citas...")
    pytest.main([__file__, "-v"])