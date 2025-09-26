"""
Admin router for MedicLab
Implements administrative endpoints with proper role verification and security logging
Requirements: 6.1, 6.2, 6.4, 6.7
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import User, Appointment
from ..schemas import UserDisplay, AppointmentDisplay
from ..security import require_admin_role
from ..logging_config import log_security_event

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_role)]
)


@router.get("/users", response_model=List[UserDisplay])
async def get_all_users(
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """
    Get all users in the system (admin only)
    
    Requirement 6.1: Crear GET /api/admin/users con verificación de rol admin
    Requirement 6.4: Excluir información sensible como hashes de contraseñas en respuestas
    
    Args:
        current_user: Admin user from JWT token
        db: Database session
        
    Returns:
        List of all users without sensitive information
    """
    try:
        # Log admin access to user list
        log_security_event(
            "ADMIN_USER_LIST_ACCESS", 
            current_user['user_id'], 
            True, 
            "Admin accessed complete user list"
        )
        
        # Query all users from database
        users = db.query(User).all()
        
        # Convert to UserDisplay schema (automatically excludes password_hash)
        user_list = []
        for user in users:
            user_display = UserDisplay(
                id=user.id,
                email=user.email,
                role=user.role,
                first_name=user.first_name,
                last_name=user.last_name,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
                is_active=user.is_active
            )
            user_list.append(user_display)
        
        return user_list
        
    except Exception as e:
        # Log error accessing user list
        log_security_event(
            "ADMIN_USER_LIST_ERROR", 
            current_user['user_id'], 
            False, 
            f"Error accessing user list: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener lista de usuarios"
        )


@router.get("/appointments", response_model=List[AppointmentDisplay])
async def get_all_appointments(
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """
    Get all appointments in the system (admin only)
    
    Requirement 6.2: Implementar GET /api/admin/appointments para ver todas las citas del sistema
    Requirement 6.7: Implementar principio de menor privilegio en respuestas de datos
    
    Args:
        current_user: Admin user from JWT token
        db: Database session
        
    Returns:
        List of all appointments with patient and doctor names
    """
    try:
        # Log admin access to appointments
        log_security_event(
            "ADMIN_APPOINTMENTS_ACCESS", 
            current_user['user_id'], 
            True, 
            "Admin accessed complete appointments list"
        )
        
        # Query all appointments (we'll get user info separately to avoid JOIN complexity)
        appointments = db.query(Appointment).all()
        
        # Convert to AppointmentDisplay schema with user names
        appointment_list = []
        for appointment in appointments:
            # Get patient and doctor information
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
                patient_name=f"{patient.first_name} {patient.last_name}" if patient else "Usuario no encontrado",
                doctor_name=f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Médico no encontrado"
            )
            appointment_list.append(appointment_display)
        
        return appointment_list
        
    except Exception as e:
        # Log error accessing appointments
        log_security_event(
            "ADMIN_APPOINTMENTS_ERROR", 
            current_user['user_id'], 
            False, 
            f"Error accessing appointments: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener lista de citas"
        )


@router.get("/users/{user_id}", response_model=UserDisplay)
async def get_user_by_id(
    user_id: int,
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """
    Get specific user by ID (admin only)
    
    Requirement 6.4: Excluir información sensible como hashes de contraseñas en respuestas
    
    Args:
        user_id: ID of the user to retrieve
        current_user: Admin user from JWT token
        db: Database session
        
    Returns:
        User information without sensitive data
    """
    try:
        # Log admin access to specific user
        log_security_event(
            "ADMIN_USER_DETAIL_ACCESS", 
            current_user['user_id'], 
            True, 
            f"Admin accessed user details for user_id: {user_id}"
        )
        
        # Query specific user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            log_security_event(
                "ADMIN_USER_NOT_FOUND", 
                current_user['user_id'], 
                False, 
                f"Admin tried to access non-existent user_id: {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Convert to UserDisplay schema (excludes password_hash)
        return UserDisplay(
            id=user.id,
            email=user.email,
            role=user.role,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            is_active=user.is_active
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected error
        log_security_event(
            "ADMIN_USER_DETAIL_ERROR", 
            current_user['user_id'], 
            False, 
            f"Error accessing user {user_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener información del usuario"
        )


@router.get("/appointments/{appointment_id}", response_model=AppointmentDisplay)
async def get_appointment_by_id(
    appointment_id: int,
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """
    Get specific appointment by ID (admin only)
    
    Args:
        appointment_id: ID of the appointment to retrieve
        current_user: Admin user from JWT token
        db: Database session
        
    Returns:
        Appointment information with patient and doctor names
    """
    try:
        # Log admin access to specific appointment
        log_security_event(
            "ADMIN_APPOINTMENT_DETAIL_ACCESS", 
            current_user['user_id'], 
            True, 
            f"Admin accessed appointment details for appointment_id: {appointment_id}"
        )
        
        # Query specific appointment
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            log_security_event(
                "ADMIN_APPOINTMENT_NOT_FOUND", 
                current_user['user_id'], 
                False, 
                f"Admin tried to access non-existent appointment_id: {appointment_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cita no encontrada"
            )
        
        # Get patient and doctor information
        patient = db.query(User).filter(User.id == appointment.patient_id).first()
        doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
        
        # Convert to AppointmentDisplay schema
        return AppointmentDisplay(
            id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_date=appointment.appointment_date,
            description=appointment.description,
            status=appointment.status,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else "Usuario no encontrado",
            doctor_name=f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Médico no encontrado"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected error
        log_security_event(
            "ADMIN_APPOINTMENT_DETAIL_ERROR", 
            current_user['user_id'], 
            False, 
            f"Error accessing appointment {appointment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener información de la cita"
        )

@router.get("/logs", response_model=dict)
async def get_security_logs(
    page: int = 1,
    page_size: int = 20,
    action_type: Optional[str] = None,
    user_id: Optional[int] = None,
    success: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ip_address: Optional[str] = None,
    current_user: dict = Depends(require_admin_role)
):
    """
    Get security logs with filtering and pagination (admin only)
    
    Args:
        page: Page number (default: 1)
        page_size: Number of logs per page (default: 20, max: 100)
        action_type: Filter by action type
        user_id: Filter by user ID
        success: Filter by success status
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        ip_address: Filter by IP address
        current_user: Admin user from JWT token
        
    Returns:
        Paginated security logs with metadata
    """
    from ..logging_config import read_security_logs, get_log_statistics
    from datetime import datetime
    
    try:
        # Log admin access to security logs
        log_security_event(
            "ADMIN_LOGS_ACCESS", 
            current_user['user_id'], 
            True, 
            f"Admin accessed security logs - Page: {page}, Filters: action={action_type}, user={user_id}, success={success}"
        )
        
        # Validate and convert date parameters
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha de inicio inválido. Use formato ISO: YYYY-MM-DDTHH:MM:SS"
                )
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha de fin inválido. Use formato ISO: YYYY-MM-DDTHH:MM:SS"
                )
        
        # Validate page_size
        if page_size > 100:
            page_size = 100
        elif page_size < 1:
            page_size = 20
        
        # Read and filter logs
        logs, total_count = read_security_logs(
            page=page,
            page_size=page_size,
            action_type=action_type,
            user_id=user_id,
            success=success,
            start_date=start_datetime,
            end_date=end_datetime,
            ip_address=ip_address
        )
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        
        # Convert logs to response format
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'timestamp': log['timestamp'].isoformat(),
                'level': log['level'],
                'action': log['action'],
                'user_id': log['user_id'],
                'success': log['success'],
                'ip_address': log['ip_address'],
                'details': log['details'],
                'user_agent': log['user_agent']
            })
        
        # Get statistics
        stats = get_log_statistics()
        
        return {
            'logs': formatted_logs,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'statistics': stats
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error accessing security logs
        log_security_event(
            "ADMIN_LOGS_ERROR", 
            current_user['user_id'], 
            False, 
            f"Error accessing security logs: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener logs de seguridad"
        )


@router.get("/logs/actions", response_model=List[str])
async def get_available_log_actions(
    current_user: dict = Depends(require_admin_role)
):
    """
    Get list of available log action types for filtering
    
    Returns:
        List of available action types
    """
    from ..logging_config import SECURITY_EVENTS
    
    try:
        # Log admin access to log actions
        log_security_event(
            "ADMIN_LOG_ACTIONS_ACCESS", 
            current_user['user_id'], 
            True, 
            "Admin accessed available log action types"
        )
        
        return SECURITY_EVENTS
        
    except Exception as e:
        # Log error
        log_security_event(
            "ADMIN_LOG_ACTIONS_ERROR", 
            current_user['user_id'], 
            False, 
            f"Error accessing log action types: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener tipos de acciones"
        )