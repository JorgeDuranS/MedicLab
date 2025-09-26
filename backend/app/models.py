"""
SQLAlchemy models for MedicLab
Implements User and Appointment models with proper relationships and enums
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class UserRole(enum.Enum):
    """Enum for user roles in the system"""
    PATIENT = "patient"
    DOCTOR = "doctor" 
    ADMIN = "admin"


class AppointmentStatus(enum.Enum):
    """Enum for appointment status"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    """
    User model representing patients, doctors, and administrators
    Implements secure user management with role-based access
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    # Appointments where this user is the patient
    patient_appointments = relationship(
        "Appointment", 
        foreign_keys="Appointment.patient_id",
        back_populates="patient"
    )
    
    # Appointments where this user is the doctor
    doctor_appointments = relationship(
        "Appointment",
        foreign_keys="Appointment.doctor_id", 
        back_populates="doctor"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"


class Appointment(Base):
    """
    Appointment model representing medical appointments
    Links patients with doctors and manages appointment lifecycle
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship(
        "User", 
        foreign_keys=[patient_id],
        back_populates="patient_appointments"
    )
    
    doctor = relationship(
        "User",
        foreign_keys=[doctor_id], 
        back_populates="doctor_appointments"
    )

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, status='{self.status.value}')>"