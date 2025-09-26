"""
Appointments router for MedicLab
Implements secure appointment management with role-based access control
Requirements: 2.1, 2.6, 3.1, 3.2, 3.3
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from ..database import get_db
from ..models import Appointment, User, UserRole, AppointmentStatus
from ..schemas import AppointmentCreate, AppointmentUpdate, AppointmentDisplay
from ..security import get_current_user, require_patient_role, require_doctor_role, require_doctor_or_admin_role
from ..logging_config import log_security_event
from ..rate_limiter import limiter, RATE_LIMITS, get_client_identifier

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("/", response_model=List[AppointmentDisplay])
@limiter.limit(RATE_LIMITS["api_default"])
async def get_appointments(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las citas según el rol del usuario
    
    - Pacientes: Solo sus propias citas como paciente
    - Médicos: Solo las citas asignadas a ellos
    - Administradores: Todas las citas del sistema
    
    Implementa:
    - Filtrado por rol según token JWT (Req 2.1, 2.6)
    - Logging de acceso autorizado (Req 2.6)
    - Rate limiting para prevenir abuso (Req 1.3)
    
    Args:
        request: Request de FastAPI para rate limiting
        current_user: Usuario actual obtenido del token JWT
        db: Sesión de base de datos
        
    Returns:
        Lista de citas filtradas según el rol del usuario
        
    Raises:
        HTTPException: Si hay errores de acceso o base de datos
    """
    client_ip = get_client_identifier(request)
    user_id = current_user['user_id']
    user_role = current_user['role']
    
    try:
        # Verificar que el usuario existe en la base de datos
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            log_security_event(
                action="UNAUTHORIZED_ACCESS",
                user_id=user_id,
                success=False,
                details="Usuario no encontrado o inactivo",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autorizado"
            )
        
        # Construir query base
        query = db.query(Appointment).join(User, Appointment.patient_id == User.id)
        
        # Filtrar según rol del usuario
        if user_role == 'patient':
            # Pacientes: Solo sus propias citas como paciente (Req 2.1)
            query = query.filter(Appointment.patient_id == user_id)
            log_details = f"Paciente consultó sus citas"
            
        elif user_role == 'doctor':
            # Médicos: Solo las citas asignadas a ellos (Req 2.2)
            query = query.filter(Appointment.doctor_id == user_id)
            log_details = f"Médico consultó su agenda"
            
        elif user_role == 'admin':
            # Administradores: Todas las citas del sistema (Req 2.3)
            log_details = f"Administrador consultó todas las citas"
            
        else:
            # Rol no reconocido
            log_security_event(
                action="UNAUTHORIZED_ACCESS",
                user_id=user_id,
                success=False,
                details=f"Rol no reconocido: {user_role}",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol de usuario no válido"
            )
        
        # Ejecutar query básica
        appointments = query.all()
        
        # Construir respuesta con información completa
        result = []
        for appointment in appointments:
            # Obtener información del paciente y médico
            patient = db.query(User).filter(User.id == appointment.patient_id).first()
            doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
            
            appointment_display = AppointmentDisplay(
                id=appointment.id,
                patient_id=appointment.patient_id,
                doctor_id=appointment.doctor_id,
                appointment_date=appointment.appointment_date,
                description=appointment.description,
                status=appointment.status,
                created_at=appointment.created_at,
                updated_at=appointment.updated_at,
                patient_name=f"{patient.first_name} {patient.last_name}" if patient else None,
                doctor_name=f"{doctor.first_name} {doctor.last_name}" if doctor else None
            )
            result.append(appointment_display)
        
        # Log acceso exitoso (Req 2.6)
        log_security_event(
            action="APPOINTMENTS_ACCESS",
            user_id=user_id,
            success=True,
            details=f"{log_details}. Citas encontradas: {len(result)}",
            ip_address=client_ip
        )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error inesperado
        log_security_event(
            action="APPOINTMENTS_ACCESS_ERROR",
            user_id=user_id,
            success=False,
            details=f"Error inesperado: {str(e)}",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/", response_model=AppointmentDisplay, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMITS["api_default"])
async def create_appointment(
    request: Request,
    appointment_data: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva cita médica
    
    - Pacientes: Pueden crear citas para sí mismos
    - Médicos: Pueden crear citas para pacientes (asignándose como doctor)
    - Administradores: Pueden crear cualquier cita
    
    Implementa:
    - Validación de patient_id según token JWT para pacientes (Req 3.1)
    - Validación de fechas futuras como regla de negocio crítica (Req 3.2, 3.3)
    - Sanitización de datos usando Pydantic (Req 3.1)
    - Consultas parametrizadas para prevenir inyección SQL (Req 3.4)
    
    Args:
        request: Request de FastAPI para rate limiting
        appointment_data: Datos de la cita validados por Pydantic
        current_user: Usuario actual obtenido del token JWT
        db: Sesión de base de datos
        
    Returns:
        AppointmentDisplay: Información de la cita creada
        
    Raises:
        HTTPException: Si hay errores de validación o autorización
    """
    client_ip = get_client_identifier(request)
    user_id = current_user['user_id']
    user_role = current_user['role']
    
    try:
        # Verificar que el usuario existe en la base de datos
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            log_security_event(
                action="UNAUTHORIZED_ACCESS",
                user_id=user_id,
                success=False,
                details="Usuario no encontrado o inactivo",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autorizado"
            )
        
        # Determinar doctor_id y patient_id según el rol del usuario y los datos recibidos
        if user_role == 'patient':
            # Pacientes: Deben especificar doctor_id, ellos son el paciente
            if not appointment_data.doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Los pacientes deben especificar un médico"
                )
            
            doctor_id = appointment_data.doctor_id
            patient_id = user_id
            
            # Validar que el médico existe
            doctor = db.query(User).filter(
                User.id == doctor_id,
                User.role == UserRole.DOCTOR,
                User.is_active == True
            ).first()
            
            if not doctor:
                log_security_event(
                    action="APPOINTMENT_CREATION_FAILED",
                    user_id=user_id,
                    success=False,
                    details=f"Médico no válido: {doctor_id}",
                    ip_address=client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El médico especificado no existe o no está activo"
                )
            
            log_details = f"Paciente creó cita para sí mismo con Dr. {doctor.first_name} {doctor.last_name}"
            
        elif user_role == 'doctor':
            # Médicos: Deben especificar patient_id, ellos son el doctor
            if not appointment_data.patient_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Los médicos deben especificar un paciente"
                )
            
            doctor_id = user_id
            patient_id = appointment_data.patient_id
            
            # Validar que el paciente existe
            patient = db.query(User).filter(
                User.id == patient_id,
                User.role == UserRole.PATIENT,
                User.is_active == True
            ).first()
            
            if not patient:
                log_security_event(
                    action="APPOINTMENT_CREATION_FAILED",
                    user_id=user_id,
                    success=False,
                    details=f"Paciente no válido: {patient_id}",
                    ip_address=client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El paciente especificado no existe o no está activo"
                )
            
            log_details = f"Médico creó cita para {patient.first_name} {patient.last_name}"
            
        elif user_role == 'admin':
            # Administradores: Pueden especificar cualquiera de los dos
            if appointment_data.doctor_id:
                # Admin especifica médico (como paciente)
                doctor_id = appointment_data.doctor_id
                patient_id = user_id
                
                doctor = db.query(User).filter(
                    User.id == doctor_id,
                    User.role == UserRole.DOCTOR,
                    User.is_active == True
                ).first()
                
                if not doctor:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El médico especificado no existe o no está activo"
                    )
                
                log_details = f"Administrador creó cita para sí mismo con Dr. {doctor.first_name} {doctor.last_name}"
                
            elif appointment_data.patient_id:
                # Admin especifica paciente (como médico)
                doctor_id = user_id
                patient_id = appointment_data.patient_id
                
                patient = db.query(User).filter(
                    User.id == patient_id,
                    User.role == UserRole.PATIENT,
                    User.is_active == True
                ).first()
                
                if not patient:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El paciente especificado no existe o no está activo"
                    )
                
                log_details = f"Administrador creó cita para {patient.first_name} {patient.last_name}"
            
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe especificar doctor_id o patient_id"
                )
            
        else:
            log_security_event(
                action="UNAUTHORIZED_ACCESS",
                user_id=user_id,
                success=False,
                details=f"Rol no reconocido: {user_role}",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol de usuario no válido"
            )
        
        # Validar que el paciente existe (si es diferente del usuario actual)
        if patient_id != user_id:
            patient = db.query(User).filter(
                User.id == patient_id,
                User.is_active == True
            ).first()
            
            if not patient:
                log_security_event(
                    action="APPOINTMENT_CREATION_FAILED",
                    user_id=user_id,
                    success=False,
                    details=f"Paciente no válido: {patient_id}",
                    ip_address=client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El paciente especificado no existe o no está activo"
                )
        
        # Crear nueva cita (Req 3.4: consultas parametrizadas automáticas con SQLAlchemy)
        new_appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_data.appointment_date,
            description=appointment_data.description,
            status=AppointmentStatus.SCHEDULED
        )
        
        # Guardar en base de datos
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        
        # Obtener información completa para la respuesta
        patient = db.query(User).filter(User.id == patient_id).first()
        doctor = db.query(User).filter(User.id == doctor_id).first()
        
        # Log creación exitosa
        log_security_event(
            action="APPOINTMENT_CREATED",
            user_id=user_id,
            success=True,
            details=f"{log_details}. Cita ID: {new_appointment.id}, Fecha: {appointment_data.appointment_date}",
            ip_address=client_ip
        )
        
        # Construir respuesta
        appointment_display = AppointmentDisplay(
            id=new_appointment.id,
            patient_id=new_appointment.patient_id,
            doctor_id=new_appointment.doctor_id,
            appointment_date=new_appointment.appointment_date,
            description=new_appointment.description,
            status=new_appointment.status,
            created_at=new_appointment.created_at,
            updated_at=new_appointment.updated_at,
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else None,
            doctor_name=f"{doctor.first_name} {doctor.last_name}" if doctor else None
        )
        
        return appointment_display
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error inesperado
        log_security_event(
            action="APPOINTMENT_CREATION_ERROR",
            user_id=user_id,
            success=False,
            details=f"Error inesperado: {str(e)}",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear la cita"
        )


@router.put("/{appointment_id}", response_model=AppointmentDisplay)
@limiter.limit(RATE_LIMITS["api_default"])
async def update_appointment(
    request: Request,
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza una cita médica existente
    
    - Médicos: Pueden actualizar solo las citas asignadas a ellos
    - Administradores: Pueden actualizar cualquier cita
    - Pacientes: No tienen acceso a este endpoint
    
    Implementa:
    - Validación que el médico sea el doctor_id asignado (Req 2.3, 5.2)
    - Actualización de estado de citas (completada, cancelada) (Req 5.3)
    - Logging de intentos de acceso no autorizado (Req 5.2)
    - Validación de fechas futuras si se actualiza la fecha (Req 3.3)
    
    Args:
        request: Request de FastAPI para rate limiting
        appointment_id: ID de la cita a actualizar
        appointment_data: Datos de actualización validados por Pydantic
        current_user: Usuario actual obtenido del token JWT
        db: Sesión de base de datos
        
    Returns:
        AppointmentDisplay: Información de la cita actualizada
        
    Raises:
        HTTPException: Si hay errores de validación, autorización o la cita no existe
    """
    client_ip = get_client_identifier(request)
    user_id = current_user['user_id']
    user_role = current_user['role']
    
    try:
        # Verificar que el usuario existe en la base de datos
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            log_security_event(
                action="UNAUTHORIZED_ACCESS",
                user_id=user_id,
                success=False,
                details="Usuario no encontrado o inactivo",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autorizado"
            )
        
        # Buscar la cita a actualizar
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            log_security_event(
                action="APPOINTMENT_UPDATE_FAILED",
                user_id=user_id,
                success=False,
                details=f"Cita no encontrada: {appointment_id}",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cita no encontrada"
            )
        
        # Validar permisos según rol del usuario
        if user_role == 'doctor':
            # Médicos: Solo pueden actualizar citas asignadas a ellos (Req 2.3, 5.2)
            if appointment.doctor_id != user_id:
                log_security_event(
                    action="UNAUTHORIZED_APPOINTMENT_ACCESS",
                    user_id=user_id,
                    success=False,
                    details=f"Médico {user_id} intentó actualizar cita {appointment_id} del médico {appointment.doctor_id}",
                    ip_address=client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para actualizar esta cita"
                )
            log_details = f"Médico actualizó su cita {appointment_id}"
            
        elif user_role == 'admin':
            # Administradores: Pueden actualizar cualquier cita
            log_details = f"Administrador actualizó cita {appointment_id}"
            
        else:
            # Pacientes y otros roles no tienen acceso
            log_security_event(
                action="UNAUTHORIZED_ACCESS",
                user_id=user_id,
                success=False,
                details=f"Rol {user_role} intentó actualizar cita {appointment_id}",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para actualizar citas"
            )
        
        # Actualizar campos proporcionados
        update_data = appointment_data.model_dump(exclude_unset=True)
        
        if update_data:
            for field, value in update_data.items():
                setattr(appointment, field, value)
            
            # Actualizar timestamp de modificación
            appointment.updated_at = datetime.now(timezone.utc)
            
            # Guardar cambios
            db.commit()
            db.refresh(appointment)
            
            # Log actualización exitosa
            log_security_event(
                action="APPOINTMENT_UPDATED",
                user_id=user_id,
                success=True,
                details=f"{log_details}. Campos actualizados: {list(update_data.keys())}",
                ip_address=client_ip
            )
        else:
            # No hay datos para actualizar
            log_security_event(
                action="APPOINTMENT_UPDATE_EMPTY",
                user_id=user_id,
                success=True,
                details=f"Actualización vacía para cita {appointment_id}",
                ip_address=client_ip
            )
        
        # Obtener información completa para la respuesta
        patient = db.query(User).filter(User.id == appointment.patient_id).first()
        doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
        
        # Construir respuesta
        appointment_display = AppointmentDisplay(
            id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_date=appointment.appointment_date,
            description=appointment.description,
            status=appointment.status,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else None,
            doctor_name=f"{doctor.first_name} {doctor.last_name}" if doctor else None
        )
        
        return appointment_display
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error inesperado
        log_security_event(
            action="APPOINTMENT_UPDATE_ERROR",
            user_id=user_id,
            success=False,
            details=f"Error inesperado: {str(e)}",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al actualizar la cita"
        )