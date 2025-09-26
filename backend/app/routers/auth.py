"""
Authentication router for MedicLab
Implements secure user registration and login with rate limiting and security logging
Requirements: 1.1, 1.2, 1.3, 1.4
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserRegistration, UserLogin, UserDisplay
from ..security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_user_token_data,
    validate_password_strength,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..logging_config import log_authentication_attempt, log_security_event
from ..rate_limiter import limiter, RATE_LIMITS, get_client_identifier

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserDisplay, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMITS["register"])
async def register_user(
    request: Request,
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en el sistema
    
    Implementa:
    - Validación de contraseña segura (Req 1.2)
    - Hashing bcrypt con sal (Req 1.1)
    - Rate limiting para prevenir spam (Req 1.3)
    - Logging de eventos de registro (Req 1.4)
    
    Args:
        request: Request de FastAPI para rate limiting
        user_data: Datos de registro validados por Pydantic
        db: Sesión de base de datos
        
    Returns:
        UserDisplay: Información del usuario creado (sin contraseña)
        
    Raises:
        HTTPException: Si el email ya existe o hay errores de validación
    """
    client_ip = get_client_identifier(request)
    
    try:
        # 1. Verificar si el email ya existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            # Log intento de registro con email duplicado
            log_security_event(
                action="REGISTRATION_ATTEMPT",
                success=False,
                details=f"Email already exists: {user_data.email}",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado en el sistema"
            )
        
        # 2. Validar fortaleza de contraseña (redundante con Pydantic, pero por seguridad)
        try:
            validate_password_strength(user_data.password)
        except ValueError as e:
            log_security_event(
                action="REGISTRATION_ATTEMPT",
                success=False,
                details=f"Weak password for email: {user_data.email}",
                ip_address=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # 3. Hashear contraseña usando bcrypt
        password_hash = hash_password(user_data.password)
        
        # 4. Crear nuevo usuario
        new_user = User(
            email=user_data.email,
            password_hash=password_hash,
            role=user_data.role,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True
        )
        
        # 5. Guardar en base de datos
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 6. Log registro exitoso
        log_security_event(
            action="USER_REGISTRATION",
            user_id=new_user.id,
            success=True,
            details=f"New user registered: {user_data.email}, Role: {user_data.role.value}",
            ip_address=client_ip
        )
        
        # 7. Retornar información del usuario (sin contraseña)
        return UserDisplay.model_validate(new_user)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error inesperado
        log_security_event(
            action="REGISTRATION_ERROR",
            success=False,
            details=f"Unexpected error during registration: {str(e)}",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante el registro"
        )


@router.post("/login")
@limiter.limit(RATE_LIMITS["login"])
async def login_user(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y genera JWT token
    
    Implementa:
    - Verificación de credenciales con bcrypt (Req 1.1)
    - Rate limiting contra ataques de fuerza bruta (Req 1.3)
    - Logging de intentos exitosos y fallidos (Req 1.4)
    - Generación de JWT con información de rol (Req 1.5)
    
    Args:
        request: Request de FastAPI para rate limiting
        login_data: Credenciales de login validadas por Pydantic
        db: Sesión de base de datos
        
    Returns:
        dict: Token de acceso, tipo de token, información del usuario
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    client_ip = get_client_identifier(request)
    user_agent = request.headers.get("User-Agent", "")
    
    try:
        # 1. Buscar usuario por email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            # Log intento con email inexistente
            log_authentication_attempt(
                email=login_data.email,
                success=False,
                ip_address=client_ip,
                failure_reason="Email not found"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 2. Verificar si la cuenta está activa
        if not user.is_active:
            log_authentication_attempt(
                email=login_data.email,
                success=False,
                user_id=user.id,
                ip_address=client_ip,
                failure_reason="Account inactive"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta desactivada",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 3. Verificar contraseña
        if not verify_password(login_data.password, user.password_hash):
            # Log intento con contraseña incorrecta
            log_authentication_attempt(
                email=login_data.email,
                success=False,
                user_id=user.id,
                ip_address=client_ip,
                failure_reason="Invalid password"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 4. Crear datos para el token JWT
        token_data = create_user_token_data(
            user_id=user.id,
            email=user.email,
            role=user.role.value
        )
        
        # 5. Generar token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        # 6. Log login exitoso
        log_authentication_attempt(
            email=login_data.email,
            success=True,
            user_id=user.id,
            ip_address=client_ip
        )
        
        # 7. Retornar token y información del usuario
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # En segundos
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "avatar_url": user.avatar_url
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error inesperado
        log_security_event(
            action="LOGIN_ERROR",
            success=False,
            details=f"Unexpected error during login: {str(e)}",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante el login"
        )


@router.post("/logout")
async def logout_user(request: Request):
    """
    Endpoint de logout (principalmente para logging)
    
    Nota: En JWT stateless, el logout real se maneja en el frontend
    eliminando el token. Este endpoint sirve para logging de seguridad.
    
    Args:
        request: Request de FastAPI
        
    Returns:
        dict: Mensaje de confirmación
    """
    client_ip = get_client_identifier(request)
    
    # Intentar extraer información del usuario del token si está presente
    user_id = None
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from ..security import extract_user_from_token
            token = auth_header.split(" ")[1]
            user_info = extract_user_from_token(token)
            user_id = user_info.get("user_id")
    except:
        # Si no se puede extraer, continuar sin user_id
        pass
    
    # Log evento de logout
    log_security_event(
        action="USER_LOGOUT",
        user_id=user_id,
        success=True,
        details="User logged out",
        ip_address=client_ip
    )
    
    return {
        "message": "Logout exitoso",
        "detail": "El token debe ser eliminado del cliente"
    }