import React, { useState } from 'react';
import { validateAvatarUrl } from '../../utils/ssrfProtection';

const SSRFValidationDemo = ({ className = '' }) => {
  const [testUrl, setTestUrl] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [isVisible, setIsVisible] = useState(false);

  // Example URLs for testing
  const exampleUrls = {
    valid: [
      'https://imgur.com/image.jpg',
      'https://postimg.cc/photo.png',
      'https://gravatar.com/avatar/123.jpg'
    ],
    invalid: [
      'http://127.0.0.1:8080/admin',
      'https://malicious-site.com/image.jpg',
      'ftp://internal.server.com/file',
      'http://192.168.1.1/config',
      'https://localhost:3000/api/users'
    ]
  };

  const handleTestUrl = () => {
    if (!testUrl.trim()) {
      setValidationResult({ valid: false, message: 'Ingresa una URL para probar' });
      return;
    }

    const result = validateAvatarUrl(testUrl);
    setValidationResult(result);
  };

  const handleExampleClick = (url) => {
    setTestUrl(url);
    const result = validateAvatarUrl(url);
    setValidationResult(result);
  };

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  if (!isVisible) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
        <button
          onClick={toggleVisibility}
          className="w-full flex items-center justify-between text-left hover:bg-gray-100 rounded-md p-2 transition-colors"
        >
          <div className="flex items-center">
            <svg className="w-5 h-5 text-gray-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-medium text-gray-700">
              Demostración de Validación SSRF
            </span>
          </div>
          <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900">
              Demostración de Validación SSRF
            </h3>
          </div>
          <button
            onClick={toggleVisibility}
            className="text-gray-400 hover:text-gray-600 p-1 rounded-md"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Prueba diferentes URLs para ver cómo funciona la protección SSRF
        </p>
      </div>

      <div className="p-4 space-y-6">
        {/* URL Test Input */}
        <div>
          <label htmlFor="test-url" className="block text-sm font-medium text-gray-700 mb-2">
            URL a probar:
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              id="test-url"
              value={testUrl}
              onChange={(e) => setTestUrl(e.target.value)}
              placeholder="Ingresa una URL para probar..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
            />
            <button
              onClick={handleTestUrl}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-colors"
            >
              Probar
            </button>
          </div>
        </div>

        {/* Validation Result */}
        {validationResult && (
          <div className={`p-3 rounded-md border ${
            validationResult.valid 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-start">
              {validationResult.valid ? (
                <svg className="w-5 h-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              )}
              <div>
                <p className={`text-sm font-medium ${
                  validationResult.valid ? 'text-green-800' : 'text-red-800'
                }`}>
                  {validationResult.valid ? 'URL Válida' : 'URL Bloqueada'}
                </p>
                {validationResult.message && (
                  <p className={`text-xs mt-1 ${
                    validationResult.valid ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {validationResult.message}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Example URLs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Valid Examples */}
          <div>
            <h4 className="text-sm font-medium text-green-800 mb-2 flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              URLs Válidas
            </h4>
            <div className="space-y-1">
              {exampleUrls.valid.map((url, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(url)}
                  className="w-full text-left text-xs font-mono text-green-700 bg-green-50 hover:bg-green-100 px-2 py-1 rounded border border-green-200 transition-colors"
                >
                  {url}
                </button>
              ))}
            </div>
          </div>

          {/* Invalid Examples */}
          <div>
            <h4 className="text-sm font-medium text-red-800 mb-2 flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              URLs Bloqueadas
            </h4>
            <div className="space-y-1">
              {exampleUrls.invalid.map((url, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(url)}
                  className="w-full text-left text-xs font-mono text-red-700 bg-red-50 hover:bg-red-100 px-2 py-1 rounded border border-red-200 transition-colors"
                >
                  {url}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
          <p className="text-xs text-blue-700">
            <strong>Nota:</strong> Esta demostración muestra cómo funciona la validación en tiempo real. 
            Las mismas validaciones se aplican cuando actualizas tu avatar.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SSRFValidationDemo;