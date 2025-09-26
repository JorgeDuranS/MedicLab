"""
Módulo de seguridad para MedicLab
Implementa hashing de contraseñas, JWT tokens y validación de seguridad
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from functools import wraps

# Configuración de bcrypt para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT
SECRET_KEY = "mediclab-secret-key-change-in-production"  # En producción usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt con sal automática
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> bool:
    """
    Valida que una contraseña cumple con los criterios de fortaleza
    
    Criterios:
    - Mínimo 8 caracteres
    - Al menos una letra minúscula
    - Al menos una letra mayúscula  
    - Al menos un número
    
    Args:
        password: Contraseña a validar
        
    Returns:
        True si cumple criterios, False en caso contrario
        
    Raises:
        ValueError: Con mensaje específico del criterio no cumplido
    """
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    
    if not re.search(r'[a-z]', password):
        raise ValueError("La contraseña debe contener al menos una letra minúscula")
    
    if not re.search(r'[A-Z]', password):
        raise ValueError("La contraseña debe contener al menos una letra mayúscula")
    
    if not re.search(r'\d', password):
        raise ValueError("La contraseña debe contener al menos un número")
    
    return True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT token con información del usuario y rol
    
    Args:
        data: Datos a incluir en el token (user_id, email, role)
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        JWT token codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un JWT token
    
    Args:
        token: JWT token a verificar
        
    Returns:
        Payload decodificado del token
        
    Raises:
        HTTPException: Si el token es inválido o expirado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


def create_user_token_data(user_id: int, email: str, role: str) -> dict:
    """
    Crea el payload de datos para un token JWT de usuario
    
    Args:
        user_id: ID del usuario
        email: Email del usuario
        role: Rol del usuario (patient, doctor, admin)
        
    Returns:
        Diccionario con datos para el token
    """
    return {
        "sub": str(user_id),
        "email": email,
        "role": role
    }


def extract_user_from_token(token: str) -> dict:
    """
    Extrae información del usuario desde un token JWT válido
    
    Args:
        token: JWT token válido
        
    Returns:
        Diccionario con user_id, email y role
    """
    payload = verify_token(token)
    return {
        "user_id": int(payload.get("sub")),
        "email": payload.get("email"),
        "role": payload.get("role")
    }


# HTTP Bearer scheme for JWT token extraction
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Middleware de autenticación JWT para validar tokens en requests
    
    Extrae y valida el JWT token del header Authorization,
    verifica que el token es válido y extrae la información del usuario.
    
    Args:
        credentials: Credenciales HTTP Bearer del header Authorization
        
    Returns:
        Diccionario con información del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o expirado
    """
    from .logging_config import log_security_event
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extraer token del header Authorization
        token = credentials.credentials
        
        # Verificar y decodificar token
        payload = verify_token(token)
        user_id = int(payload.get("sub"))
        email = payload.get("email")
        role = payload.get("role")
        
        if not user_id or not email or not role:
            log_security_event("INVALID_TOKEN", user_id, False, "Token incompleto")
            raise credentials_exception
        
        # Log acceso exitoso
        log_security_event("TOKEN_VALIDATED", user_id, True, f"Rol: {role}")
        
        return {
            "user_id": user_id,
            "email": email,
            "role": role
        }
        
    except JWTError as e:
        log_security_event("INVALID_TOKEN", None, False, f"JWT Error: {str(e)}")
        raise credentials_exception
    except ValueError as e:
        log_security_event("INVALID_TOKEN", None, False, f"Token parsing error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        log_security_event("AUTH_ERROR", None, False, f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno de autenticación"
        )


def get_current_user_with_db(
    current_user: dict = Depends(get_current_user),
    db: Session = None
) -> dict:
    """
    Obtiene el usuario actual con verificación en base de datos
    
    Args:
        current_user: Usuario obtenido del token JWT
        db: Sesión de base de datos
        
    Returns:
        Diccionario con información del usuario y objeto User de BD
        
    Raises:
        HTTPException: Si el usuario no existe o está inactivo
    """
    from .models import User
    from .logging_config import log_security_event
    
    if db is None:
        from .database import SessionLocal
        db = SessionLocal()
        try:
            return _verify_user_in_db(current_user, db)
        finally:
            db.close()
    else:
        return _verify_user_in_db(current_user, db)


def _verify_user_in_db(current_user: dict, db: Session) -> dict:
    """
    Función auxiliar para verificar usuario en base de datos
    """
    from .models import User
    from .logging_config import log_security_event
    
    user_id = current_user['user_id']
    
    # Verificar que el usuario existe en la base de datos
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        log_security_event("INVALID_TOKEN", user_id, False, "Usuario no encontrado en BD")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
        
    # Verificar que el usuario está activo
    if not user.is_active:
        log_security_event("INACTIVE_USER_ACCESS", user_id, False, "Usuario inactivo")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    # Verificar que los datos del token coinciden con la BD
    if user.email != current_user['email'] or user.role.value != current_user['role']:
        log_security_event("TOKEN_DATA_MISMATCH", user_id, False, "Datos del token no coinciden")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # Agregar objeto User completo
    current_user['user'] = user
    return current_user


def require_role(allowed_roles: list):
    """
    Decorador para verificar que el usuario tiene uno de los roles permitidos
    
    Args:
        allowed_roles: Lista de roles permitidos (ej: ["patient", "doctor"])
        
    Returns:
        Decorador que valida el rol del usuario
        
    Raises:
        HTTPException: Si el usuario no tiene el rol requerido
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el parámetro current_user en kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                # Si no está en kwargs, buscar en args (asumiendo que es el último parámetro)
                for arg in args:
                    if isinstance(arg, dict) and 'role' in arg:
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            user_role = current_user.get('role')
            if user_role not in allowed_roles:
                from .logging_config import log_security_event
                log_security_event(
                    "UNAUTHORIZED_ACCESS", 
                    current_user.get('user_id'), 
                    False, 
                    f"Rol {user_role} no permitido. Requerido: {allowed_roles}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acceso denegado. Rol requerido: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def require_patient_role(current_user: dict = Depends(get_current_user)):
    """
    Dependency para endpoints que requieren rol de paciente
    
    Args:
        current_user: Usuario actual obtenido del token JWT
        
    Returns:
        Información del usuario si tiene rol de paciente
        
    Raises:
        HTTPException: Si el usuario no es paciente
    """
    if current_user['role'] != 'patient':
        from .logging_config import log_security_event
        log_security_event(
            "UNAUTHORIZED_ACCESS", 
            current_user['user_id'], 
            False, 
            f"Rol {current_user['role']} intentó acceso de paciente"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de paciente"
        )
    return current_user


async def require_doctor_role(current_user: dict = Depends(get_current_user)):
    """
    Dependency para endpoints que requieren rol de médico
    
    Args:
        current_user: Usuario actual obtenido del token JWT
        
    Returns:
        Información del usuario si tiene rol de médico
        
    Raises:
        HTTPException: Si el usuario no es médico
    """
    if current_user['role'] != 'doctor':
        from .logging_config import log_security_event
        log_security_event(
            "UNAUTHORIZED_ACCESS", 
            current_user['user_id'], 
            False, 
            f"Rol {current_user['role']} intentó acceso de médico"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de médico"
        )
    return current_user


async def require_admin_role(current_user: dict = Depends(get_current_user)):
    """
    Dependency para endpoints que requieren rol de administrador
    
    Implementa validación de permisos administrativos con logging de seguridad
    Requirements: 6.3, 6.5, 6.6
    
    Args:
        current_user: Usuario actual obtenido del token JWT
        
    Returns:
        Información del usuario si tiene rol de administrador
        
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if current_user['role'] != 'admin':
        from .logging_config import log_security_event
        log_security_event(
            "UNAUTHORIZED_ADMIN_ACCESS", 
            current_user['user_id'], 
            False, 
            f"Rol {current_user['role']} intentó acceso administrativo no autorizado"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de administrador"
        )
    
    # Log successful admin access
    from .logging_config import log_security_event
    log_security_event(
        "ADMIN_ACCESS_GRANTED", 
        current_user['user_id'], 
        True, 
        "Acceso administrativo autorizado"
    )
    
    return current_user


async def require_doctor_or_admin_role(current_user: dict = Depends(get_current_user)):
    """
    Dependency para endpoints que requieren rol de médico o administrador
    
    Args:
        current_user: Usuario actual obtenido del token JWT
        
    Returns:
        Información del usuario si tiene rol de médico o administrador
        
    Raises:
        HTTPException: Si el usuario no es médico ni administrador
    """
    if current_user['role'] not in ['doctor', 'admin']:
        from .logging_config import log_security_event
        log_security_event(
            "UNAUTHORIZED_ACCESS", 
            current_user['user_id'], 
            False, 
            f"Rol {current_user['role']} intentó acceso de médico/admin"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de médico o administrador"
        )
    return current_user


def require_admin_role_decorator(func):
    """
    Decorador para endpoints administrativos con logging de seguridad
    
    Implementa principio de menor privilegio y logging de intentos no autorizados
    Requirements: 6.3, 6.5, 6.6
    
    Args:
        func: Función del endpoint a proteger
        
    Returns:
        Función decorada con validación de rol admin
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        from .logging_config import log_security_event
        
        # Buscar current_user en los argumentos
        current_user = None
        for key, value in kwargs.items():
            if key == 'current_user' and isinstance(value, dict) and 'role' in value:
                current_user = value
                break
        
        if not current_user:
            # Buscar en args si no está en kwargs
            for arg in args:
                if isinstance(arg, dict) and 'role' in arg:
                    current_user = arg
                    break
        
        if not current_user:
            log_security_event(
                "ADMIN_ACCESS_NO_USER", 
                None, 
                False, 
                "Intento de acceso admin sin usuario autenticado"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autenticado"
            )
        
        # Validar rol de administrador
        if current_user.get('role') != 'admin':
            log_security_event(
                "UNAUTHORIZED_ADMIN_ACCESS", 
                current_user.get('user_id'), 
                False, 
                f"Rol {current_user.get('role')} intentó acceso administrativo a {func.__name__}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Se requiere rol de administrador"
            )
        
        # Log acceso administrativo exitoso
        log_security_event(
            "ADMIN_FUNCTION_ACCESS", 
            current_user.get('user_id'), 
            True, 
            f"Admin accedió a función: {func.__name__}"
        )
        
        # Ejecutar función original
        try:
            result = await func(*args, **kwargs)
            
            # Log operación administrativa exitosa
            log_security_event(
                "ADMIN_OPERATION_SUCCESS", 
                current_user.get('user_id'), 
                True, 
                f"Operación administrativa exitosa: {func.__name__}"
            )
            
            return result
            
        except Exception as e:
            # Log error en operación administrativa
            log_security_event(
                "ADMIN_OPERATION_ERROR", 
                current_user.get('user_id'), 
                False, 
                f"Error en operación administrativa {func.__name__}: {str(e)}"
            )
            raise
    
    return wrapper