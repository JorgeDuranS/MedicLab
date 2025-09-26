// SSRF Protection utilities for frontend validation

// Allowed domains for avatar images (must match backend configuration)
export const ALLOWED_DOMAINS = [
  'imgur.com',
  'postimg.cc', 
  'gravatar.com'
];

// Private IP ranges to block (additional frontend validation)
const PRIVATE_IP_RANGES = [
  /^127\./,           // 127.0.0.0/8 (localhost)
  /^10\./,            // 10.0.0.0/8 (private)
  /^172\.(1[6-9]|2[0-9]|3[0-1])\./,  // 172.16.0.0/12 (private)
  /^192\.168\./,      // 192.168.0.0/16 (private)
  /^169\.254\./,      // 169.254.0.0/16 (link-local)
  /^0\./,             // 0.0.0.0/8 (reserved)
  /^224\./,           // 224.0.0.0/4 (multicast)
  /^240\./            // 240.0.0.0/4 (reserved)
];

/**
 * Validates if a URL is safe from SSRF attacks
 * @param {string} url - The URL to validate
 * @returns {Object} - { valid: boolean, message?: string }
 */
export const validateAvatarUrl = (url) => {
  if (!url || typeof url !== 'string') {
    return { valid: false, message: 'La URL es requerida' };
  }

  // Trim whitespace
  url = url.trim();

  if (!url) {
    return { valid: false, message: 'La URL no puede estar vacía' };
  }

  let urlObj;
  try {
    urlObj = new URL(url);
  } catch (error) {
    return { valid: false, message: 'URL inválida. Verifica el formato' };
  }

  // Check protocol - only allow HTTP and HTTPS
  if (!['http:', 'https:'].includes(urlObj.protocol)) {
    return { 
      valid: false, 
      message: 'Solo se permiten URLs con protocolo HTTP o HTTPS' 
    };
  }

  // Get hostname and normalize
  const hostname = urlObj.hostname.toLowerCase();

  // Check if hostname is an IP address
  if (isIPAddress(hostname)) {
    return { 
      valid: false, 
      message: 'No se permiten direcciones IP directas. Usa un dominio válido' 
    };
  }

  // Check against allowed domains
  const isAllowedDomain = ALLOWED_DOMAINS.some(domain => {
    const normalizedDomain = domain.toLowerCase();
    return hostname === normalizedDomain || hostname.endsWith('.' + normalizedDomain);
  });

  if (!isAllowedDomain) {
    return { 
      valid: false, 
      message: `Dominio no permitido. Usa uno de: ${ALLOWED_DOMAINS.join(', ')}` 
    };
  }

  // Additional checks for suspicious patterns
  if (containsSuspiciousPatterns(url)) {
    return { 
      valid: false, 
      message: 'URL contiene patrones sospechosos' 
    };
  }

  return { valid: true };
};

/**
 * Checks if a string is an IP address
 * @param {string} hostname - The hostname to check
 * @returns {boolean}
 */
const isIPAddress = (hostname) => {
  // IPv4 pattern
  const ipv4Pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
  
  // IPv6 pattern (simplified)
  const ipv6Pattern = /^([0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}$/i;
  
  if (ipv4Pattern.test(hostname)) {
    // Validate IPv4 ranges
    const parts = hostname.split('.');
    return parts.every(part => {
      const num = parseInt(part, 10);
      return num >= 0 && num <= 255;
    });
  }
  
  return ipv6Pattern.test(hostname);
};

/**
 * Checks for suspicious patterns in URLs
 * @param {string} url - The URL to check
 * @returns {boolean}
 */
const containsSuspiciousPatterns = (url) => {
  const suspiciousPatterns = [
    // URL encoding attempts to bypass filters
    /%[0-9a-f]{2}/i,
    // Double encoding
    /%25[0-9a-f]{2}/i,
    // Unicode encoding
    /\\u[0-9a-f]{4}/i,
    // Localhost variations
    /localhost/i,
    // Internal network indicators
    /internal/i,
    /admin/i,
    /management/i,
    // Suspicious ports
    /:22[^0-9]/, // SSH
    /:23[^0-9]/, // Telnet
    /:3389/,     // RDP
    /:5432/,     // PostgreSQL
    /:3306/,     // MySQL
    /:6379/,     // Redis
    /:27017/,    // MongoDB
  ];

  return suspiciousPatterns.some(pattern => pattern.test(url));
};

/**
 * Gets a user-friendly error message for common SSRF validation failures
 * @param {string} url - The URL that failed validation
 * @returns {string}
 */
export const getSSRFErrorMessage = (url) => {
  if (!url) return 'URL requerida';
  
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    
    if (isIPAddress(hostname)) {
      return 'No se permiten direcciones IP. Usa un nombre de dominio válido.';
    }
    
    if (!ALLOWED_DOMAINS.some(domain => 
      hostname === domain.toLowerCase() || hostname.endsWith('.' + domain.toLowerCase())
    )) {
      return `Dominio no permitido. Solo se permiten: ${ALLOWED_DOMAINS.join(', ')}`;
    }
    
  } catch (error) {
    return 'Formato de URL inválido';
  }
  
  return 'URL no válida por razones de seguridad';
};

/**
 * Validates multiple URLs at once
 * @param {string[]} urls - Array of URLs to validate
 * @returns {Object[]} - Array of validation results
 */
export const validateMultipleUrls = (urls) => {
  return urls.map(url => ({
    url,
    ...validateAvatarUrl(url)
  }));
};

/**
 * Checks if a URL is from an allowed domain (quick check)
 * @param {string} url - The URL to check
 * @returns {boolean}
 */
export const isAllowedDomain = (url) => {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    
    return ALLOWED_DOMAINS.some(domain => {
      const normalizedDomain = domain.toLowerCase();
      return hostname === normalizedDomain || hostname.endsWith('.' + normalizedDomain);
    });
  } catch (error) {
    return false;
  }
};

/**
 * Sanitizes a URL by removing potentially dangerous components
 * @param {string} url - The URL to sanitize
 * @returns {string} - Sanitized URL
 */
export const sanitizeUrl = (url) => {
  if (!url) return '';
  
  try {
    const urlObj = new URL(url.trim());
    
    // Remove fragment and some query parameters that could be used maliciously
    urlObj.hash = '';
    
    // Remove potentially dangerous query parameters
    const dangerousParams = ['redirect', 'callback', 'return', 'url', 'next'];
    dangerousParams.forEach(param => {
      urlObj.searchParams.delete(param);
    });
    
    return urlObj.toString();
  } catch (error) {
    return url.trim();
  }
};

/**
 * Creates a preview-safe URL for displaying images
 * @param {string} url - The original URL
 * @returns {string} - Safe URL for preview
 */
export const createPreviewUrl = (url) => {
  const validation = validateAvatarUrl(url);
  if (!validation.valid) {
    return '';
  }
  
  return sanitizeUrl(url);
};

export default {
  ALLOWED_DOMAINS,
  validateAvatarUrl,
  getSSRFErrorMessage,
  validateMultipleUrls,
  isAllowedDomain,
  sanitizeUrl,
  createPreviewUrl
};