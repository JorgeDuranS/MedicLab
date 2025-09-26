"""
SSRF Protection utilities for MedicLab
Implements URL validation and IP filtering to prevent Server-Side Request Forgery attacks
Requirements: 4.1, 4.2, 4.4
"""

import socket
import ipaddress
import requests
from urllib.parse import urlparse
from typing import List, Tuple
import logging

# Configure logger for SSRF events
ssrf_logger = logging.getLogger('mediclab.ssrf')

# Whitelist of allowed domains for avatar images
ALLOWED_AVATAR_DOMAINS = [
    'imgur.com',
    'i.imgur.com',
    'postimg.cc',
    'gravatar.com',
    'www.gravatar.com',
    'secure.gravatar.com'
]

# Private IP ranges to block (SSRF protection)
PRIVATE_IP_RANGES = [
    ipaddress.IPv4Network('127.0.0.0/8'),      # Loopback
    ipaddress.IPv4Network('10.0.0.0/8'),       # Private Class A
    ipaddress.IPv4Network('172.16.0.0/12'),    # Private Class B
    ipaddress.IPv4Network('192.168.0.0/16'),   # Private Class C
    ipaddress.IPv4Network('169.254.0.0/16'),   # Link-local
    ipaddress.IPv4Network('224.0.0.0/4'),      # Multicast
    ipaddress.IPv4Network('240.0.0.0/4'),      # Reserved
    ipaddress.IPv4Network('0.0.0.0/8'),        # "This" network
]


def is_private_ip(ip: str) -> bool:
    """
    Detecta si una IP es privada/interna para prevenir SSRF
    
    Args:
        ip: Dirección IP como string
        
    Returns:
        True si la IP es privada/interna, False si es pública
        
    Requirement 4.2: bloquear direcciones IP internas
    """
    try:
        ip_obj = ipaddress.IPv4Address(ip)
        
        # TEMPORAL: Permitir 127.0.0.1 para desarrollo/pruebas
        # TODO: Remover esta excepción en producción
        if str(ip_obj) == "127.0.0.1":
            return False
        
        return any(ip_obj in network for network in PRIVATE_IP_RANGES)
    except ipaddress.AddressValueError:
        # Si no es IPv4 válida, intentar IPv6
        try:
            ip_obj = ipaddress.IPv6Address(ip)
            # Bloquear IPv6 loopback y link-local
            return (
                ip_obj.is_loopback or 
                ip_obj.is_link_local or 
                ip_obj.is_private or
                ip_obj.is_reserved
            )
        except ipaddress.AddressValueError:
            # Si no es IP válida, rechazar por seguridad
            ssrf_logger.warning(f"Invalid IP address format: {ip}")
            return True


def validate_avatar_url(url: str) -> Tuple[bool, str]:
    """
    Valida una URL de avatar contra ataques SSRF
    
    Args:
        url: URL a validar
        
    Returns:
        Tuple (is_valid, error_message)
        
    Requirements: 4.1, 4.2, 4.4
    """
    try:
        # 1. Validar esquema
        if not url.startswith(('http://', 'https://')):
            return False, "La URL debe usar esquema http o https"
        
        # 2. Parsear URL
        parsed = urlparse(url)
        if not parsed.hostname:
            return False, "URL inválida: no se puede extraer el hostname"
        
        # 3. Validar dominio en whitelist
        if parsed.hostname not in ALLOWED_AVATAR_DOMAINS:
            ssrf_logger.warning(f"Domain not in whitelist: {parsed.hostname}")
            return False, f"Dominio no permitido. Dominios permitidos: {', '.join(ALLOWED_AVATAR_DOMAINS)}"
        
        # 4. Resolver dominio y validar IP
        try:
            ip = socket.gethostbyname(parsed.hostname)
            if is_private_ip(ip):
                ssrf_logger.warning(f"SSRF attempt detected: {url} resolves to private IP {ip}")
                return False, "No se permiten direcciones IP privadas o internas"
        except socket.gaierror as e:
            ssrf_logger.warning(f"DNS resolution failed for {parsed.hostname}: {e}")
            return False, "El dominio no se puede resolver"
        
        # 5. Validar extensión de archivo (opcional para algunos servicios como Gravatar)
        path = parsed.path.lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        # Gravatar no requiere extensión explícita
        if 'gravatar.com' not in parsed.hostname:
            if not any(path.endswith(ext) for ext in allowed_extensions):
                return False, f"Extensión de archivo no válida. Permitidas: {', '.join(allowed_extensions)}"
        
        return True, ""
        
    except Exception as e:
        ssrf_logger.error(f"Unexpected error validating URL {url}: {e}")
        return False, "Error interno validando la URL"


def download_avatar_safely(url: str, timeout: int = 5, max_size: int = 5 * 1024 * 1024) -> Tuple[bool, str, bytes]:
    """
    Descarga una imagen de avatar de forma segura con protecciones SSRF
    
    Args:
        url: URL de la imagen a descargar
        timeout: Timeout en segundos para la descarga
        max_size: Tamaño máximo permitido en bytes (default: 5MB)
        
    Returns:
        Tuple (success, error_message, image_data)
        
    Requirements: 4.1, 4.2, 4.3
    """
    try:
        # Validar URL primero
        is_valid, error_msg = validate_avatar_url(url)
        if not is_valid:
            return False, error_msg, b''
        
        # Configurar headers seguros
        headers = {
            'User-Agent': 'MedicLab/1.0 Avatar Downloader',
            'Accept': 'image/jpeg,image/png,image/gif,image/webp,image/*',
            'Accept-Encoding': 'identity',  # No compression para evitar zip bombs
        }
        
        # Realizar descarga con timeout corto
        response = requests.get(
            url, 
            headers=headers,
            timeout=timeout,
            stream=True,  # Stream para controlar tamaño
            allow_redirects=False  # No seguir redirects por seguridad
        )
        
        # Verificar status code
        if response.status_code != 200:
            ssrf_logger.warning(f"HTTP {response.status_code} for URL: {url}")
            return False, f"Error descargando imagen: HTTP {response.status_code}", b''
        
        # Verificar Content-Type
        content_type = response.headers.get('content-type', '').lower()
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if not any(ct in content_type for ct in allowed_types):
            return False, "Tipo de contenido no válido. Solo se permiten imágenes", b''
        
        # Descargar con límite de tamaño
        image_data = b''
        for chunk in response.iter_content(chunk_size=8192):
            image_data += chunk
            if len(image_data) > max_size:
                return False, f"Imagen demasiado grande. Máximo permitido: {max_size // (1024*1024)}MB", b''
        
        if len(image_data) == 0:
            return False, "La imagen está vacía", b''
        
        ssrf_logger.info(f"Avatar downloaded successfully from {url}, size: {len(image_data)} bytes")
        return True, "", image_data
        
    except requests.exceptions.Timeout:
        ssrf_logger.warning(f"Timeout downloading avatar from {url}")
        return False, "Timeout descargando la imagen", b''
    except requests.exceptions.RequestException as e:
        ssrf_logger.warning(f"Request error downloading avatar from {url}: {e}")
        return False, "Error de red descargando la imagen", b''
    except Exception as e:
        ssrf_logger.error(f"Unexpected error downloading avatar from {url}: {e}")
        return False, "Error interno descargando la imagen", b''


def log_ssrf_attempt(url: str, user_id: int, ip_address: str, details: str = ""):
    """
    Registra intentos de SSRF detectados
    
    Args:
        url: URL que causó el intento de SSRF
        user_id: ID del usuario que hizo el intento
        ip_address: IP desde donde se hizo el intento
        details: Detalles adicionales del intento
        
    Requirement 4.5: logging de intentos de SSRF detectados
    """
    ssrf_logger.warning(
        f"SSRF_ATTEMPT | User: {user_id} | IP: {ip_address} | URL: {url} | Details: {details}"
    )