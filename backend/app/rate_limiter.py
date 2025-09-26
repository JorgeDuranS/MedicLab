"""
Configuración de rate limiting para MedicLab
Implementa limitación de velocidad en memoria para endpoints críticos
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, HTTPException, status
from typing import Optional
import functools
from .logging_config import log_rate_limit_exceeded


# Función para obtener identificador del cliente
def get_client_identifier(request: Request) -> str:
    """
    Obtiene identificador único del cliente para rate limiting
    Usa IP address como identificador principal
    
    Args:
        request: Request de FastAPI
        
    Returns:
        Identificador único del cliente
    """
    # Intentar obtener IP real desde headers de proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Tomar la primera IP de la cadena
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback a IP directa
    return get_remote_address(request)


# Configuración del limiter con backend en memoria
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri="memory://",  # Backend en memoria
    default_limits=["100/hour"]  # Límite por defecto
)


# Configuración de límites específicos por endpoint
RATE_LIMITS = {
    "login": "5/minute",           # 5 intentos de login por minuto
    "register": "3/minute",        # 3 registros por minuto  
    "api_default": "100/hour",     # 100 requests por hora para API general
    "avatar_upload": "3/minute",   # 3 uploads de avatar por minuto
    "appointments": "30/hour",     # 30 operaciones de citas por hora
    "admin": "50/hour"             # 50 operaciones admin por hora
}


def create_rate_limit_decorator(limit_key: str):
    """
    Crea un decorador de rate limiting para un endpoint específico
    
    Args:
        limit_key: Clave del límite en RATE_LIMITS
        
    Returns:
        Decorador para aplicar a endpoints
    """
    limit_string = RATE_LIMITS.get(limit_key, RATE_LIMITS["api_default"])
    
    def decorator(func):
        @functools.wraps(func)
        @limiter.limit(limit_string)
        async def wrapper(request: Request, *args, **kwargs):
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# Decoradores específicos para diferentes tipos de endpoints
login_rate_limit = create_rate_limit_decorator("login")
register_rate_limit = create_rate_limit_decorator("register")
avatar_rate_limit = create_rate_limit_decorator("avatar_upload")
appointments_rate_limit = create_rate_limit_decorator("appointments")
admin_rate_limit = create_rate_limit_decorator("admin")


# Handler personalizado para rate limit exceeded
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Maneja cuando se excede el rate limit
    Registra el evento y retorna error personalizado
    
    Args:
        request: Request que excedió el límite
        exc: Excepción de rate limit
        
    Returns:
        HTTPException con mensaje personalizado
    """
    client_ip = get_client_identifier(request)
    endpoint = request.url.path
    
    # Intentar extraer user_id del token si está disponible
    user_id = None
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Aquí podríamos decodificar el token para obtener user_id
            # Por ahora lo dejamos como None
            pass
    except:
        pass
    
    # Registrar el evento de rate limit excedido
    log_rate_limit_exceeded(
        endpoint=endpoint,
        ip_address=client_ip,
        user_id=user_id
    )
    
    # Retornar error personalizado
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": "Demasiadas solicitudes. Intente nuevamente más tarde.",
            "retry_after": exc.retry_after
        }
    )


def setup_rate_limiting(app):
    """
    Configura rate limiting en la aplicación FastAPI
    
    Args:
        app: Instancia de FastAPI
    """
    # Agregar middleware de rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
    
    # Agregar middleware
    app.add_middleware(SlowAPIMiddleware)


# Función auxiliar para aplicar rate limiting manual
def apply_rate_limit(request: Request, limit_key: str):
    """
    Aplica rate limiting manualmente a una función
    
    Args:
        request: Request de FastAPI
        limit_key: Clave del límite a aplicar
        
    Raises:
        HTTPException: Si se excede el rate limit
    """
    limit_string = RATE_LIMITS.get(limit_key, RATE_LIMITS["api_default"])
    
    try:
        # Verificar límite usando el limiter
        limiter.check_request_limit(request, limit_string)
    except RateLimitExceeded as e:
        # Usar el handler personalizado
        raise custom_rate_limit_handler(request, e)


# Función para obtener información de rate limiting
def get_rate_limit_info(request: Request, limit_key: str) -> dict:
    """
    Obtiene información actual del rate limiting para un cliente
    
    Args:
        request: Request de FastAPI
        limit_key: Clave del límite
        
    Returns:
        Diccionario con información de límites
    """
    client_id = get_client_identifier(request)
    limit_string = RATE_LIMITS.get(limit_key, RATE_LIMITS["api_default"])
    
    # Parsear límite (formato: "X/period")
    try:
        limit_parts = limit_string.split("/")
        max_requests = int(limit_parts[0])
        period = limit_parts[1]
        
        return {
            "client_id": client_id,
            "limit": max_requests,
            "period": period,
            "limit_string": limit_string
        }
    except:
        return {
            "client_id": client_id,
            "limit": "unknown",
            "period": "unknown",
            "limit_string": limit_string
        }


# Middleware personalizado para logging de rate limiting
class RateLimitLoggingMiddleware:
    """
    Middleware para registrar información de rate limiting
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Registrar información de la request para debugging
            client_ip = get_client_identifier(request)
            endpoint = request.url.path
            
            # Continuar con la request normal
            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)