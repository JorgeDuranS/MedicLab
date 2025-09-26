"""
Database configuration for MedicLab
Implements SQLAlchemy engine and session management for SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL for SQLite
DATABASE_URL = "sqlite:///./database.db"

# Create SQLAlchemy engine
# check_same_thread=False is needed for SQLite to work with FastAPI
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session
    Used with FastAPI's Depends() for dependency injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database by creating all tables and default users
    This function should be called on application startup
    Requirements: 8.2, 8.4
    """
    # Import models to ensure they are registered with Base
    from . import models
    from .security import hash_password
    from .logging_config import log_security_event, security_logger
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        security_logger.info("Database tables created successfully")
        
        # Create default users for testing and demonstration
        create_default_users()
        
        log_security_event(
            action="DATABASE_INITIALIZED",
            success=True,
            details="Tables created and default users initialized"
        )
        
    except Exception as e:
        security_logger.error(f"Database initialization failed: {str(e)}")
        log_security_event(
            action="DATABASE_INITIALIZATION_FAILED",
            success=False,
            details=f"Error: {str(e)}"
        )
        raise


def create_default_users():
    """
    Create default users for testing and demonstration
    - Admin user for system administration
    - Doctor users for medical appointments
    - Patient users for testing appointments
    """
    from .models import User, UserRole
    from .security import hash_password
    from .logging_config import security_logger
    
    db = SessionLocal()
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            security_logger.info(f"Database already has {existing_users} users, skipping default user creation")
            return
        
        # Default users data
        default_users = [
            # Admin user
            {
                "email": "admin@mediclab.com",
                "password": "Admin123!",
                "role": UserRole.ADMIN,
                "first_name": "Administrador",
                "last_name": "Sistema"
            },
            # Doctor users
            {
                "email": "dr.garcia@mediclab.com", 
                "password": "Doctor123!",
                "role": UserRole.DOCTOR,
                "first_name": "Dr. Carlos",
                "last_name": "García"
            },
            {
                "email": "dr.martinez@mediclab.com",
                "password": "Doctor123!",
                "role": UserRole.DOCTOR,
                "first_name": "Dra. Ana",
                "last_name": "Martínez"
            },
            {
                "email": "dr.lopez@mediclab.com",
                "password": "Doctor123!",
                "role": UserRole.DOCTOR,
                "first_name": "Dr. Luis",
                "last_name": "López"
            },
            # Patient users for testing
            {
                "email": "patient@mediclab.com",
                "password": "Patient123!",
                "role": UserRole.PATIENT,
                "first_name": "Paciente",
                "last_name": "Prueba"
            },
            {
                "email": "paciente1@example.com",
                "password": "Patient123!",
                "role": UserRole.PATIENT,
                "first_name": "María",
                "last_name": "González"
            },
            {
                "email": "paciente2@example.com",
                "password": "Patient123!",
                "role": UserRole.PATIENT,
                "first_name": "Juan",
                "last_name": "Pérez"
            },
            {
                "email": "paciente3@example.com",
                "password": "Patient123!",
                "role": UserRole.PATIENT,
                "first_name": "Carmen",
                "last_name": "Rodríguez"
            }
        ]
        
        # Create users
        created_users = []
        for user_data in default_users:
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_active=True
            )
            db.add(user)
            created_users.append(f"{user_data['role'].value}: {user_data['email']}")
        
        # Commit all users
        db.commit()
        
        security_logger.info(f"Created {len(default_users)} default users:")
        for user_info in created_users:
            security_logger.info(f"  - {user_info}")
        
        # Log security event
        from .logging_config import log_security_event
        log_security_event(
            action="DEFAULT_USERS_CREATED",
            success=True,
            details=f"Created {len(default_users)} default users for testing"
        )
        
    except Exception as e:
        db.rollback()
        security_logger.error(f"Failed to create default users: {str(e)}")
        from .logging_config import log_security_event
        log_security_event(
            action="DEFAULT_USERS_CREATION_FAILED",
            success=False,
            details=f"Error: {str(e)}"
        )
        raise
    finally:
        db.close()


def create_sample_appointments():
    """
    Create sample appointments for demonstration purposes
    This function can be called separately if needed for testing
    """
    from .models import User, Appointment, UserRole, AppointmentStatus
    from datetime import datetime, timedelta
    from .logging_config import security_logger
    
    db = SessionLocal()
    try:
        # Check if appointments already exist
        existing_appointments = db.query(Appointment).count()
        if existing_appointments > 0:
            security_logger.info(f"Database already has {existing_appointments} appointments")
            return
        
        # Get doctors and patients
        doctors = db.query(User).filter(User.role == UserRole.DOCTOR).all()
        patients = db.query(User).filter(User.role == UserRole.PATIENT).all()
        
        if not doctors or not patients:
            security_logger.warning("No doctors or patients found, skipping sample appointments")
            return
        
        # Create sample appointments
        sample_appointments = []
        base_date = datetime.now() + timedelta(days=1)  # Start from tomorrow
        
        for i, patient in enumerate(patients[:3]):  # Limit to first 3 patients
            for j in range(2):  # 2 appointments per patient
                appointment_date = base_date + timedelta(days=i*3 + j*7, hours=9 + j*2)
                doctor = doctors[j % len(doctors)]
                
                appointment = Appointment(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    appointment_date=appointment_date,
                    description=f"Consulta médica general - Paciente: {patient.first_name}",
                    status=AppointmentStatus.SCHEDULED
                )
                sample_appointments.append(appointment)
                db.add(appointment)
        
        db.commit()
        security_logger.info(f"Created {len(sample_appointments)} sample appointments")
        
    except Exception as e:
        db.rollback()
        security_logger.error(f"Failed to create sample appointments: {str(e)}")
        raise
    finally:
        db.close()