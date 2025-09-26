"""
Configuración de logging de seguridad para MedicLab
Implementa logging estructurado para eventos de seguridad
"""

import logging
import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pathlib import Path

# Crear directorio de logs si no existe
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configuración del logger de seguridad
def setup_security_logger():
    """
    Configura el logger de seguridad con archivo rotativo
    """
    security_logger = logging.getLogger('mediclab.security')
    security_logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers si ya están configurados
    if security_logger.handlers:
        return security_logger
    
    # Handler para archivo de logs de seguridad
    security_log_file = LOGS_DIR / "security.log"
    file_handler = logging.FileHandler(security_log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Formato detallado para logs de seguridad
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Handler para consola (desarrollo)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Solo warnings y errores en consola
    console_handler.setFormatter(formatter)
    
    security_logger.addHandler(file_handler)
    security_logger.addHandler(console_handler)
    
    return security_logger


# Instancia global del logger de seguridad
security_logger = setup_security_logger()


def log_security_event(
    action: str, 
    user_id: Optional[int] = None, 
    success: bool = True, 
    details: str = "",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    Registra eventos de seguridad en el archivo de log
    
    Args:
        action: Tipo de acción (LOGIN_ATTEMPT, UNAUTHORIZED_ACCESS, etc.)
        user_id: ID del usuario involucrado (si aplica)
        success: Si la acción fue exitosa
        details: Detalles adicionales del evento
        ip_address: Dirección IP del cliente
        user_agent: User agent del cliente
    """
    # Construir mensaje estructurado
    message_parts = [f"Action: {action}"]
    
    if user_id is not None:
        message_parts.append(f"User: {user_id}")
    
    message_parts.append(f"Success: {success}")
    
    if ip_address:
        message_parts.append(f"IP: {ip_address}")
    
    if details:
        message_parts.append(f"Details: {details}")
    
    if user_agent:
        message_parts.append(f"UserAgent: {user_agent[:100]}")  # Limitar longitud
    
    message = " | ".join(message_parts)
    
    # Log según el resultado
    if success:
        security_logger.info(message)
    else:
        security_logger.warning(message)


def log_authentication_attempt(
    email: str, 
    success: bool, 
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    failure_reason: str = ""
):
    """
    Registra intentos de autenticación
    
    Args:
        email: Email del usuario
        success: Si el login fue exitoso
        user_id: ID del usuario (si login exitoso)
        ip_address: IP del cliente
        failure_reason: Razón del fallo (si aplica)
    """
    details = f"Email: {email}"
    if not success and failure_reason:
        details += f", Reason: {failure_reason}"
    
    log_security_event(
        action="LOGIN_ATTEMPT",
        user_id=user_id,
        success=success,
        details=details,
        ip_address=ip_address
    )


def log_unauthorized_access(
    user_id: Optional[int],
    resource: str,
    required_role: str,
    user_role: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """
    Registra intentos de acceso no autorizado
    
    Args:
        user_id: ID del usuario que intenta acceder
        resource: Recurso al que se intenta acceder
        required_role: Rol requerido para el recurso
        user_role: Rol actual del usuario
        ip_address: IP del cliente
    """
    details = f"Resource: {resource}, Required: {required_role}"
    if user_role:
        details += f", UserRole: {user_role}"
    
    log_security_event(
        action="UNAUTHORIZED_ACCESS",
        user_id=user_id,
        success=False,
        details=details,
        ip_address=ip_address
    )


def log_rate_limit_exceeded(
    endpoint: str,
    ip_address: Optional[str] = None,
    user_id: Optional[int] = None
):
    """
    Registra cuando se excede el rate limit
    
    Args:
        endpoint: Endpoint donde se excedió el límite
        ip_address: IP del cliente
        user_id: ID del usuario (si está autenticado)
    """
    log_security_event(
        action="RATE_LIMIT_EXCEEDED",
        user_id=user_id,
        success=False,
        details=f"Endpoint: {endpoint}",
        ip_address=ip_address
    )


def log_ssrf_attempt(
    url: str,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    reason: str = ""
):
    """
    Registra intentos de SSRF detectados
    
    Args:
        url: URL maliciosa detectada
        user_id: ID del usuario
        ip_address: IP del cliente
        reason: Razón por la que se detectó como maliciosa
    """
    details = f"URL: {url}"
    if reason:
        details += f", Reason: {reason}"
    
    log_security_event(
        action="SSRF_ATTEMPT",
        user_id=user_id,
        success=False,
        details=details,
        ip_address=ip_address
    )


def log_invalid_token(
    token_type: str = "JWT",
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    reason: str = ""
):
    """
    Registra tokens inválidos o expirados
    
    Args:
        token_type: Tipo de token (JWT, etc.)
        user_id: ID del usuario (si se puede extraer)
        ip_address: IP del cliente
        reason: Razón de invalidez
    """
    details = f"TokenType: {token_type}"
    if reason:
        details += f", Reason: {reason}"
    
    log_security_event(
        action="INVALID_TOKEN",
        user_id=user_id,
        success=False,
        details=details,
        ip_address=ip_address
    )


# Eventos de seguridad principales que se registran
SECURITY_EVENTS = [
    "LOGIN_ATTEMPT",
    "UNAUTHORIZED_ACCESS", 
    "RATE_LIMIT_EXCEEDED",
    "SSRF_ATTEMPT",
    "INVALID_TOKEN",
    "PASSWORD_CHANGE",
    "ACCOUNT_LOCKED",
    "SUSPICIOUS_ACTIVITY"
]

# LOG READING AND PROCESSING FUNCTIONS


def parse_log_line(line: str) -> Optional[Dict]:
    """
    Parse a single log line into structured data
    
    Args:
        line: Raw log line from security.log
        
    Returns:
        Dictionary with parsed log data or None if parsing fails
    """
    # Pattern to match log format: 
    # 2025-09-24 22:15:53 - INFO - mediclab.security - Action: TOKEN_VALIDATED | User: 1 | Success: True | Details: Rol: patient
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - ([\w.]+) - (.+)'
    
    match = re.match(pattern, line.strip())
    if not match:
        return None
    
    timestamp_str, level, logger_name, message = match.groups()
    
    try:
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None
    
    # Parse the structured message
    parsed_data = {
        'timestamp': timestamp,
        'level': level,
        'logger_name': logger_name,
        'raw_message': message,
        'action': None,
        'user_id': None,
        'success': None,
        'ip_address': None,
        'details': None,
        'user_agent': None
    }
    
    # Extract structured fields from message
    # Format: Action: VALUE | User: VALUE | Success: VALUE | IP: VALUE | Details: VALUE | UserAgent: VALUE
    fields = message.split(' | ')
    
    for field in fields:
        if ':' in field:
            key, value = field.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key == 'Action':
                parsed_data['action'] = value
            elif key == 'User':
                try:
                    parsed_data['user_id'] = int(value) if value != 'None' else None
                except ValueError:
                    parsed_data['user_id'] = None
            elif key == 'Success':
                parsed_data['success'] = value.lower() == 'true'
            elif key == 'IP':
                parsed_data['ip_address'] = value if value != 'None' else None
            elif key == 'Details':
                parsed_data['details'] = value if value != 'None' else None
            elif key == 'UserAgent':
                parsed_data['user_agent'] = value if value != 'None' else None
    
    return parsed_data


def read_security_logs(
    page: int = 1,
    page_size: int = 20,
    action_type: Optional[str] = None,
    user_id: Optional[int] = None,
    success: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    ip_address: Optional[str] = None
) -> Tuple[List[Dict], int]:
    """
    Read and filter security logs from the log file
    
    Args:
        page: Page number (1-based)
        page_size: Number of logs per page
        action_type: Filter by action type
        user_id: Filter by user ID
        success: Filter by success status
        start_date: Filter by start date
        end_date: Filter by end date
        ip_address: Filter by IP address
        
    Returns:
        Tuple of (filtered_logs, total_count)
    """
    log_file_path = LOGS_DIR / "security.log"
    
    if not log_file_path.exists():
        return [], 0
    
    all_logs = []
    
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parsed_log = parse_log_line(line)
                if parsed_log:
                    all_logs.append(parsed_log)
    except Exception as e:
        security_logger.error(f"Error reading security logs: {e}")
        return [], 0
    
    # Sort by timestamp (most recent first)
    all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Apply filters
    filtered_logs = []
    for log in all_logs:
        # Filter by action type
        if action_type and log['action'] != action_type:
            continue
            
        # Filter by user ID
        if user_id is not None and log['user_id'] != user_id:
            continue
            
        # Filter by success status
        if success is not None and log['success'] != success:
            continue
            
        # Filter by date range
        if start_date and log['timestamp'] < start_date:
            continue
        if end_date and log['timestamp'] > end_date:
            continue
            
        # Filter by IP address
        if ip_address and log['ip_address'] != ip_address:
            continue
            
        filtered_logs.append(log)
    
    total_count = len(filtered_logs)
    
    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_logs = filtered_logs[start_idx:end_idx]
    
    return paginated_logs, total_count


def get_log_statistics() -> Dict:
    """
    Get basic statistics about security logs
    
    Returns:
        Dictionary with log statistics
    """
    log_file_path = LOGS_DIR / "security.log"
    
    if not log_file_path.exists():
        return {
            'total_events': 0,
            'failed_events': 0,
            'success_rate': 0.0,
            'recent_events_24h': 0,
            'top_actions': []
        }
    
    all_logs = []
    
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parsed_log = parse_log_line(line)
                if parsed_log:
                    all_logs.append(parsed_log)
    except Exception as e:
        security_logger.error(f"Error reading security logs for statistics: {e}")
        return {
            'total_events': 0,
            'failed_events': 0,
            'success_rate': 0.0,
            'recent_events_24h': 0,
            'top_actions': []
        }
    
    total_events = len(all_logs)
    failed_events = sum(1 for log in all_logs if log['success'] is False)
    success_rate = ((total_events - failed_events) / total_events * 100) if total_events > 0 else 0.0
    
    # Count recent events (last 24 hours)
    from datetime import timedelta
    now = datetime.now()
    recent_cutoff = now - timedelta(hours=24)
    recent_events_24h = sum(1 for log in all_logs if log['timestamp'] >= recent_cutoff)
    
    # Count top actions
    action_counts = {}
    for log in all_logs:
        action = log['action']
        if action:
            action_counts[action] = action_counts.get(action, 0) + 1
    
    top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'total_events': total_events,
        'failed_events': failed_events,
        'success_rate': round(success_rate, 2),
        'recent_events_24h': recent_events_24h,
        'top_actions': [{'action': action, 'count': count} for action, count in top_actions]
    }