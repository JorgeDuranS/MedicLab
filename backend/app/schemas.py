"""
Pydantic schemas for MedicLab
Implements data validation and serialization for API endpoints
"""

from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from typing import Optional
from datetime import datetime
import re
import socket
import ipaddress
from urllib.parse import urlparse
from .models import UserRole, AppointmentStatus


class UserRegistration(BaseModel):
    """
    Schema for user registration
    Implements secure password validation according to requirement 1.2
    """
    email: EmailStr
    password: str = Field(min_length=8, description="Mínimo 8 caracteres, debe incluir mayúsculas, minúsculas y números")
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role: UserRole = Field(default=UserRole.PATIENT, description="Rol del usuario en el sistema")

    @validator('password')
    def validate_password_strength(cls, v):
        """
        Validador personalizado para contraseñas seguras
        Requirement 1.2: mínimo 8 caracteres, mayúsculas, minúsculas, números
        """
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        return v

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validar que los nombres no estén vacíos y no contengan caracteres especiales"""
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        
        # Permitir solo letras, espacios y algunos caracteres especiales comunes en nombres
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', v):
            raise ValueError('El nombre contiene caracteres no válidos')
        
        return v.strip()

    class Config:
        # Ejemplo de uso en documentación de API
        json_schema_extra = {
            "example": {
                "email": "paciente@ejemplo.com",
                "password": "MiPassword123",
                "first_name": "Juan",
                "last_name": "Pérez",
                "role": "patient"
            }
        }


class UserLogin(BaseModel):
    """
    Schema for user login
    Simple validation for authentication endpoints
    """
    email: EmailStr
    password: str = Field(min_length=1, description="Contraseña del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "paciente@ejemplo.com",
                "password": "MiPassword123"
            }
        }


class UserDisplay(BaseModel):
    """
    Schema for displaying user information
    Excludes sensitive data like password_hash
    """
    id: int
    email: str
    role: UserRole
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    created_at: datetime
    is_active: bool

    class Config:
        # Permite usar objetos SQLAlchemy directamente
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "paciente@ejemplo.com",
                "role": "patient",
                "first_name": "Juan",
                "last_name": "Pérez",
                "avatar_url": "https://imgur.com/avatar.jpg",
                "created_at": "2024-01-15T10:30:00Z",
                "is_active": True
            }
        }


class UserUpdate(BaseModel):
    """
    Schema for updating user profile information
    Allows partial updates of user data
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validar nombres si se proporcionan"""
        if v is not None:
            if not v.strip():
                raise ValueError('El nombre no puede estar vacío')
            
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', v):
                raise ValueError('El nombre contiene caracteres no válidos')
            
            return v.strip()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Juan Carlos",
                "last_name": "Pérez García",
                "avatar_url": "https://imgur.com/new-avatar.jpg"
            }
        }


# ============================================================================
# APPOINTMENT SCHEMAS
# ============================================================================

class AppointmentCreate(BaseModel):
    """
    Schema for creating new appointments
    Implements validation for future dates as critical business rule
    Requirements: 3.1, 3.2
    """
    doctor_id: Optional[int] = Field(None, gt=0, description="ID del médico asignado (para pacientes)")
    patient_id: Optional[int] = Field(None, gt=0, description="ID del paciente asignado (para médicos)")
    appointment_date: datetime = Field(description="Fecha y hora de la cita")
    description: Optional[str] = Field(None, max_length=500, description="Descripción opcional de la cita")

    @validator('appointment_date')
    def validate_future_date(cls, v):
        """
        Validador crítico para fechas futuras
        Requirement 3.3: rechazar fechas en el pasado como regla de negocio crítica
        """
        if v <= datetime.now():
            raise ValueError('La fecha de la cita debe ser en el futuro')
        return v

    @validator('description')
    def validate_description(cls, v):
        """Validar descripción si se proporciona"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None  # Convertir string vacío a None
        return v

    @validator('patient_id')
    def validate_patient_doctor_ids(cls, v, values):
        """Validar que se proporcione doctor_id O patient_id, pero no ambos"""
        doctor_id = values.get('doctor_id')
        
        # Debe haber exactamente uno de los dos
        if (doctor_id is None) == (v is None):
            raise ValueError('Debe especificar doctor_id (para pacientes) O patient_id (para médicos), pero no ambos')
        
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "doctor_id": 2,
                "appointment_date": "2024-02-15T14:30:00",
                "description": "Consulta de seguimiento"
            }
        }


class AppointmentUpdate(BaseModel):
    """
    Schema for updating existing appointments
    Allows partial updates of appointment data
    """
    appointment_date: Optional[datetime] = Field(None, description="Nueva fecha y hora de la cita")
    description: Optional[str] = Field(None, max_length=500, description="Nueva descripción de la cita")
    status: Optional[AppointmentStatus] = Field(None, description="Nuevo estado de la cita")

    @validator('appointment_date')
    def validate_future_date(cls, v):
        """
        Validador para fechas futuras en actualizaciones
        Requirement 3.3: rechazar fechas en el pasado como regla de negocio crítica
        """
        if v is not None and v <= datetime.now():
            raise ValueError('La fecha de la cita debe ser en el futuro')
        return v

    @validator('description')
    def validate_description(cls, v):
        """Validar descripción si se proporciona"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None  # Convertir string vacío a None
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "appointment_date": "2024-02-16T15:00:00",
                "description": "Consulta de control actualizada",
                "status": "completed"
            }
        }


class AppointmentDisplay(BaseModel):
    """
    Schema for displaying appointment information
    Includes related user information for complete appointment view
    """
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    description: Optional[str]
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    
    # Información del paciente y médico para display completo
    patient_name: Optional[str] = Field(None, description="Nombre completo del paciente")
    doctor_name: Optional[str] = Field(None, description="Nombre completo del médico")

    class Config:
        # Permite usar objetos SQLAlchemy directamente
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "patient_id": 3,
                "doctor_id": 2,
                "appointment_date": "2024-02-15T14:30:00",
                "description": "Consulta de seguimiento",
                "status": "scheduled",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "patient_name": "Juan Pérez",
                "doctor_name": "Dra. María García"
            }
        }


# ============================================================================
# AVATAR SCHEMAS
# ============================================================================

class AvatarUpdate(BaseModel):
    """
    Schema for updating user avatar with SSRF protection
    Implements URL validation and domain whitelist
    Requirements: 4.1, 4.4
    """
    avatar_url: HttpUrl = Field(description="URL de la imagen de avatar")

    @validator('avatar_url')
    def validate_avatar_url(cls, v):
        """
        Validador completo para URLs de avatar con protección SSRF
        Requirements: 4.1, 4.2, 4.4
        """
        url_str = str(v)
        
        # 1. Validar esquema (HttpUrl ya valida http/https)
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError('La URL debe usar esquema http o https')
        
        # 2. Validar dominio en whitelist
        parsed = urlparse(url_str)
        allowed_domains = [
            'imgur.com',
            'postimg.cc', 
            'gravatar.com',
            'i.imgur.com',
            'www.gravatar.com'
        ]
        
        if parsed.hostname not in allowed_domains:
            raise ValueError(f'Dominio no permitido. Dominios permitidos: {", ".join(allowed_domains)}')
        
        # 3. Resolver dominio y validar que no sea IP privada (protección SSRF)
        try:
            ip = socket.gethostbyname(parsed.hostname)
            if cls._is_private_ip(ip):
                raise ValueError('No se permiten direcciones IP privadas o internas')
        except socket.gaierror:
            raise ValueError('El dominio no se puede resolver')
        
        # 4. Validar extensión de archivo de imagen
        path = parsed.path.lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if not any(path.endswith(ext) for ext in allowed_extensions):
            # Permitir URLs sin extensión explícita (como Gravatar)
            if 'gravatar.com' not in parsed.hostname:
                raise ValueError(f'Extensión de archivo no válida. Permitidas: {", ".join(allowed_extensions)}')
        
        return v

    @staticmethod
    def _is_private_ip(ip: str) -> bool:
        """
        Detecta IPs privadas/internas para prevenir SSRF
        Requirement 4.2: bloquear direcciones IP internas
        """
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            private_ranges = [
                ipaddress.IPv4Network('127.0.0.0/8'),      # Loopback
                ipaddress.IPv4Network('10.0.0.0/8'),       # Private Class A
                ipaddress.IPv4Network('172.16.0.0/12'),    # Private Class B
                ipaddress.IPv4Network('192.168.0.0/16'),   # Private Class C
                ipaddress.IPv4Network('169.254.0.0/16'),   # Link-local
                ipaddress.IPv4Network('224.0.0.0/4'),      # Multicast
                ipaddress.IPv4Network('240.0.0.0/4'),      # Reserved
            ]
            return any(ip_obj in network for network in private_ranges)
        except ipaddress.AddressValueError:
            # Si no es IPv4 válida, rechazar por seguridad
            return True

    class Config:
        json_schema_extra = {
            "example": {
                "avatar_url": "https://imgur.com/avatar123.jpg"
            }
        }

# SECURITY LOGS SCHEMAS

class SecurityLogEntry(BaseModel):
    """
    Schema for displaying security log entries
    Used for admin dashboard log viewer
    """
    timestamp: datetime = Field(description="Fecha y hora del evento")
    level: str = Field(description="Nivel del log (INFO, WARNING, ERROR)")
    action: str = Field(description="Tipo de acción realizada")
    user_id: Optional[int] = Field(None, description="ID del usuario involucrado")
    success: bool = Field(description="Si la acción fue exitosa")
    ip_address: Optional[str] = Field(None, description="Dirección IP del cliente")
    details: Optional[str] = Field(None, description="Detalles adicionales del evento")
    user_agent: Optional[str] = Field(None, description="User agent del cliente")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00Z",
                "level": "WARNING",
                "action": "UNAUTHORIZED_ACCESS",
                "user_id": 123,
                "success": False,
                "ip_address": "192.168.1.100",
                "details": "Usuario intentó acceder a endpoint de admin",
                "user_agent": "Mozilla/5.0..."
            }
        }


class SecurityLogsResponse(BaseModel):
    """
    Schema for paginated security logs response
    """
    logs: list[SecurityLogEntry] = Field(description="Lista de entradas de log")
    total_count: int = Field(description="Total de logs disponibles")
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")
    total_pages: int = Field(description="Total de páginas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "logs": [],
                "total_count": 150,
                "page": 1,
                "page_size": 20,
                "total_pages": 8
            }
        }


class LogsFilter(BaseModel):
    """
    Schema for filtering security logs
    """
    action_type: Optional[str] = Field(None, description="Filtrar por tipo de acción")
    user_id: Optional[int] = Field(None, description="Filtrar por ID de usuario")
    success: Optional[bool] = Field(None, description="Filtrar por éxito/fallo")
    start_date: Optional[datetime] = Field(None, description="Fecha de inicio")
    end_date: Optional[datetime] = Field(None, description="Fecha de fin")
    ip_address: Optional[str] = Field(None, description="Filtrar por IP")
    page: int = Field(1, ge=1, description="Número de página")
    page_size: int = Field(20, ge=1, le=100, description="Tamaño de página")

    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "LOGIN_ATTEMPT",
                "success": False,
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z",
                "page": 1,
                "page_size": 20
            }
        }