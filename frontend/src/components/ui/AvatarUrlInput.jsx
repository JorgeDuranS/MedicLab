import React, { useState, useEffect } from 'react';
import { validateAvatarUrl, ALLOWED_DOMAINS, createPreviewUrl } from '../../utils/ssrfProtection';

const AvatarUrlInput = ({ 
  value = '', 
  onChange, 
  onValidationChange,
  disabled = false,
  showPreview = true,
  className = ''
}) => {
  const [inputValue, setInputValue] = useState(value);
  const [validation, setValidation] = useState({ valid: true });
  const [previewUrl, setPreviewUrl] = useState('');
  const [imageLoading, setImageLoading] = useState(false);
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    setInputValue(value);
    if (value) {
      validateAndSetPreview(value);
    } else {
      setPreviewUrl('');
      setValidation({ valid: true });
    }
  }, [value]);

  const validateAndSetPreview = (url) => {
    const validationResult = validateAvatarUrl(url);
    setValidation(validationResult);
    
    if (onValidationChange) {
      onValidationChange(validationResult);
    }

    if (validationResult.valid) {
      const safeUrl = createPreviewUrl(url);
      setPreviewUrl(safeUrl);
      setImageError(false);
    } else {
      setPreviewUrl('');
      setImageError(false);
    }
  };

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    
    if (onChange) {
      onChange(newValue);
    }

    // Debounce validation
    if (newValue.trim()) {
      validateAndSetPreview(newValue);
    } else {
      setValidation({ valid: true });
      setPreviewUrl('');
      if (onValidationChange) {
        onValidationChange({ valid: true });
      }
    }
  };

  const handleImageLoad = () => {
    setImageLoading(false);
    setImageError(false);
  };

  const handleImageError = () => {
    setImageLoading(false);
    setImageError(true);
    setPreviewUrl('');
  };

  const handleImageLoadStart = () => {
    setImageLoading(true);
    setImageError(false);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* URL Input */}
      <div>
        <label htmlFor="avatar-url" className="block text-sm font-medium text-gray-700 mb-1">
          URL de la imagen
        </label>
        <input
          type="url"
          id="avatar-url"
          value={inputValue}
          onChange={handleInputChange}
          disabled={disabled}
          placeholder="https://imgur.com/imagen.jpg"
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-transparent transition-colors ${
            validation.valid 
              ? 'border-gray-300' 
              : 'border-red-300 bg-red-50'
          } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
        />
        
        {/* Validation Error */}
        {!validation.valid && validation.message && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <svg className="w-4 h-4 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {validation.message}
          </p>
        )}
      </div>

      {/* Preview Section */}
      {showPreview && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Vista previa
          </label>
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-full overflow-hidden bg-gray-100 border-2 border-gray-200 flex items-center justify-center">
              {previewUrl && !imageError ? (
                <>
                  {imageLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-teal-400"></div>
                    </div>
                  )}
                  <img
                    src={previewUrl}
                    alt="Vista previa del avatar"
                    className="w-full h-full object-cover"
                    onLoad={handleImageLoad}
                    onError={handleImageError}
                    onLoadStart={handleImageLoadStart}
                  />
                </>
              ) : (
                <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <div className="flex-1">
              {previewUrl && !imageError ? (
                <p className="text-sm text-green-600 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Imagen válida
                </p>
              ) : imageError ? (
                <p className="text-sm text-red-600 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Error al cargar la imagen
                </p>
              ) : (
                <p className="text-sm text-gray-500">
                  Ingresa una URL válida para ver la vista previa
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Allowed Domains Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div className="flex-1">
            <h4 className="text-sm font-medium text-blue-800 mb-2">
              Dominios Permitidos por Seguridad:
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
              {ALLOWED_DOMAINS.map(domain => (
                <div key={domain} className="flex items-center text-sm text-blue-700">
                  <span className="w-2 h-2 bg-blue-400 rounded-full mr-2 flex-shrink-0"></span>
                  <span className="font-mono">{domain}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-blue-600 mt-2">
              Solo se permiten imágenes de estos dominios para proteger contra ataques SSRF
            </p>
          </div>
        </div>
      </div>

      {/* Security Notice */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div className="flex-1">
            <h4 className="text-sm font-medium text-yellow-800 mb-1">
              Aviso de Seguridad
            </h4>
            <p className="text-xs text-yellow-700">
              Las URLs son validadas para prevenir ataques SSRF (Server-Side Request Forgery). 
              No se permiten direcciones IP, dominios internos, o URLs sospechosas.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvatarUrlInput;