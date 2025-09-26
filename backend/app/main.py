"""
MedicLab FastAPI Application
Sistema de citas médicas con implementación de seguridad OWASP Top 10
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from datetime import datetime
from typing import Union

from .database import init_db
from .rate_limiter import setup_rate_limiting
from .routers import auth, appointments, users, admin
from .logging_config import log_security_event, security_logger

app = FastAPI(
    title="MedicLab API",
    description="Sistema de citas médicas con implementación de seguridad OWASP Top 10",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS configuration - Configuración restrictiva para producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development
        "http://127.0.0.1:3000",  # Alternative localhost
        # Agregar dominios de producción aquí
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Setup rate limiting
setup_rate_limiting(app)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Manejo global de excepciones HTTP con logging de seguridad
    """
    # Log eventos de seguridad relevantes
    if exc.status_code == 401:
        log_security_event(
            action="UNAUTHORIZED_REQUEST",
            success=False,
            details=f"Path: {request.url.path}, Status: {exc.status_code}",
            ip_address=request.client.host if request.client else None
        )
    elif exc.status_code == 403:
        log_security_event(
            action="FORBIDDEN_ACCESS",
            success=False,
            details=f"Path: {request.url.path}, Status: {exc.status_code}",
            ip_address=request.client.host if request.client else None
        )
    elif exc.status_code >= 500:
        log_security_event(
            action="SERVER_ERROR",
            success=False,
            details=f"Path: {request.url.path}, Status: {exc.status_code}, Detail: {exc.detail}",
            ip_address=request.client.host if request.client else None
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejo de errores de validación de entrada
    """
    log_security_event(
        action="VALIDATION_ERROR",
        success=False,
        details=f"Path: {request.url.path}, Errors: {len(exc.errors)}",
        ip_address=request.client.host if request.client else None
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Los datos proporcionados no son válidos",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejo de excepciones generales no capturadas
    """
    # Log error interno sin exponer detalles
    security_logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)} | "
        f"Path: {request.url.path} | "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )
    
    log_security_event(
        action="INTERNAL_ERROR",
        success=False,
        details=f"Path: {request.url.path}, Exception: {type(exc).__name__}",
        ip_address=request.client.host if request.client else None
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Ha ocurrido un error interno. Por favor, inténtelo más tarde.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path)
            }
        }
    )


# Register routers (they already have their prefixes defined)
app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup_event():
    """
    Inicialización de la aplicación al arranque
    """
    try:
        # Inicializar base de datos
        init_db()
        
        # Log inicio exitoso
        security_logger.info("MedicLab API started successfully")
        log_security_event(
            action="APPLICATION_STARTUP",
            success=True,
            details="Database initialized, security logging active"
        )
        
    except Exception as e:
        security_logger.error(f"Failed to start application: {str(e)}")
        log_security_event(
            action="APPLICATION_STARTUP",
            success=False,
            details=f"Startup error: {str(e)}"
        )
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Limpieza al cerrar la aplicación
    """
    security_logger.info("MedicLab API shutting down")
    log_security_event(
        action="APPLICATION_SHUTDOWN",
        success=True,
        details="Application shutdown initiated"
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API
    """
    return {
        "message": "MedicLab API - Sistema de Citas Médicas",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint para monitoreo
    """
    return {
        "status": "healthy",
        "service": "mediclab-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/api/info", tags=["Info"])
async def api_info():
    """
    Información de la API y endpoints disponibles
    """
    return {
        "api": "MedicLab",
        "version": "1.0.0",
        "description": "Sistema de citas médicas con implementación de seguridad OWASP Top 10",
        "endpoints": {
            "auth": "/api/auth",
            "appointments": "/api/appointments",
            "users": "/api/users",
            "admin": "/api/admin"
        },
        "security_features": [
            "JWT Authentication",
            "Role-based Access Control",
            "Rate Limiting",
            "SSRF Protection",
            "Security Logging",
            "Input Validation"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configuración para desarrollo
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )