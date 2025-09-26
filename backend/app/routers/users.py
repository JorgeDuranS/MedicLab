"""
Users router for MedicLab
Handles user profile management including secure avatar updates with SSRF protection
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserDisplay, AvatarUpdate, UserUpdate
from ..security import get_current_user
from ..ssrf_protection import validate_avatar_url, download_avatar_safely, log_ssrf_attempt
from ..logging_config import log_security_event
from ..rate_limiter import limiter

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/me", response_model=UserDisplay)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el perfil del usuario actual
    
    Returns:
        Información del perfil del usuario autenticado
    """
    user = db.query(User).filter(User.id == current_user['user_id']).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    log_security_event("PROFILE_ACCESS", current_user['user_id'], True, "Acceso a perfil propio")
    return user


@router.put("/me/avatar")
@limiter.limit("3/minute")  # Rate limiting específico para avatar uploads
async def update_user_avatar(
    request: Request,
    avatar_data: AvatarUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el avatar del usuario con protección SSRF completa
    
    Args:
        avatar_data: Datos del avatar con URL validada
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Mensaje de confirmación y nueva URL del avatar
        
    Requirements: 4.1, 4.2, 4.3, 4.5
    """
    user_id = current_user['user_id']
    avatar_url = str(avatar_data.avatar_url)
    
    # Obtener IP del cliente para logging
    client_ip = request.client.host
    
    try:
        # 1. Validación adicional de URL (ya validada en schema, pero doble verificación)
        is_valid, error_msg = validate_avatar_url(avatar_url)
        if not is_valid:
            log_ssrf_attempt(avatar_url, user_id, client_ip, f"URL validation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # 2. Descargar imagen de forma segura para verificar que es accesible
        success, error_msg, image_data = download_avatar_safely(avatar_url, timeout=5)
        if not success:
            log_ssrf_attempt(avatar_url, user_id, client_ip, f"Download failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error descargando avatar: {error_msg}"
            )
        
        # 3. Obtener usuario de la base de datos
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # 4. Actualizar avatar en base de datos
        old_avatar = user.avatar_url
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        
        # 5. Log evento exitoso
        log_security_event(
            "AVATAR_UPDATED", 
            user_id, 
            True, 
            f"Avatar actualizado de {old_avatar} a {avatar_url}, tamaño: {len(image_data)} bytes"
        )
        
        return {
            "message": "Avatar actualizado exitosamente",
            "avatar_url": avatar_url,
            "size_bytes": len(image_data)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (ya tienen el status code correcto)
        raise
    except Exception as e:
        # Log error inesperado
        log_security_event(
            "AVATAR_UPDATE_ERROR", 
            user_id, 
            False, 
            f"Error inesperado: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno actualizando avatar"
        )


@router.put("/me", response_model=UserDisplay)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil del usuario actual
    
    Args:
        user_data: Datos a actualizar del usuario
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Información actualizada del usuario
    """
    user_id = current_user['user_id']
    
    # Obtener usuario de la base de datos
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar campos proporcionados
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    log_security_event("PROFILE_UPDATED", user_id, True, f"Campos actualizados: {list(update_data.keys())}")
    
    return user


@router.get("/doctors", response_model=List[UserDisplay])
async def get_available_doctors(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de médicos disponibles para agendar citas
    
    Solo accesible para pacientes y administradores
    
    Returns:
        Lista de médicos activos en el sistema
    """
    # Verificar que el usuario es paciente o admin
    if current_user['role'] not in ['patient', 'admin']:
        log_security_event(
            "UNAUTHORIZED_ACCESS", 
            current_user['user_id'], 
            False, 
            f"Rol {current_user['role']} intentó acceder a lista de médicos"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo pacientes y administradores pueden ver la lista de médicos"
        )
    
    # Obtener médicos activos
    doctors = db.query(User).filter(
        User.role == UserRole.DOCTOR,
        User.is_active == True
    ).all()
    
    log_security_event("DOCTORS_LIST_ACCESS", current_user['user_id'], True, f"Listó {len(doctors)} médicos")
    
    return doctors

@router.get("/patients", response_model=List[UserDisplay])
async def get_available_patients(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de pacientes disponibles para agendar citas
    
    Solo accesible para médicos y administradores
    
    Returns:
        Lista de pacientes activos en el sistema
    """
    # Verificar que el usuario es médico o admin
    if current_user['role'] not in ['doctor', 'admin']:
        log_security_event(
            "UNAUTHORIZED_ACCESS", 
            current_user['user_id'], 
            False, 
            f"Rol {current_user['role']} intentó acceder a lista de pacientes"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo médicos y administradores pueden ver la lista de pacientes"
        )
    
    # Obtener pacientes activos
    patients = db.query(User).filter(
        User.role == UserRole.PATIENT,
        User.is_active == True
    ).all()
    
    log_security_event("PATIENTS_LIST_ACCESS", current_user['user_id'], True, f"Listó {len(patients)} pacientes")
    
    return patients