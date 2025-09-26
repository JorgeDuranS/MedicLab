import React, { useState } from 'react';
import { ALLOWED_DOMAINS } from '../../utils/ssrfProtection';

const SSRFProtectionInfo = ({ className = '' }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg ${className}`}>
      {/* Header */}
      <div className="p-4">
        <button
          onClick={toggleExpanded}
          className="w-full flex items-center justify-between text-left focus:outline-none focus:ring-2 focus:ring-blue-400 rounded-md p-1"
          aria-expanded={isExpanded}
        >
          <div className="flex items-center">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-900">
                Protección SSRF Activa
              </h3>
              <p className="text-sm text-blue-700">
                Sistema de seguridad para prevenir ataques Server-Side Request Forgery
              </p>
            </div>
          </div>
          <svg 
            className={`w-5 h-5 text-blue-600 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`} 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-blue-200">
          <div className="mt-4 space-y-6">
            {/* What is SSRF */}
            <div>
              <h4 className="text-md font-semibold text-blue-900 mb-2">
                ¿Qué es un ataque SSRF?
              </h4>
              <p className="text-sm text-blue-800 leading-relaxed">
                Server-Side Request Forgery (SSRF) es un tipo de ataque donde un atacante puede hacer que el servidor 
                realice peticiones HTTP a recursos internos o externos no autorizados. Esto puede exponer información 
                sensible o permitir acceso a servicios internos.
              </p>
            </div>

            {/* Protection Measures */}
            <div>
              <h4 className="text-md font-semibold text-blue-900 mb-3">
                Medidas de Protección Implementadas:
              </h4>
              <div className="space-y-3">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Lista Blanca de Dominios</p>
                    <p className="text-xs text-blue-700">Solo se permiten dominios específicos y confiables</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Bloqueo de IPs Privadas</p>
                    <p className="text-xs text-blue-700">Se rechazan direcciones IP internas y localhost</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Validación de Protocolos</p>
                    <p className="text-xs text-blue-700">Solo HTTP y HTTPS están permitidos</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Detección de Patrones Sospechosos</p>
                    <p className="text-xs text-blue-700">Se analizan URLs en busca de intentos de bypass</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Timeout de Conexión</p>
                    <p className="text-xs text-blue-700">Límite de tiempo para prevenir ataques de DoS</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Allowed Domains */}
            <div>
              <h4 className="text-md font-semibold text-blue-900 mb-3">
                Dominios Permitidos:
              </h4>
              <div className="bg-white rounded-md p-3 border border-blue-200">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {ALLOWED_DOMAINS.map(domain => (
                    <div key={domain} className="flex items-center">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                      <span className="text-sm font-mono text-blue-800">{domain}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Blocked Examples */}
            <div>
              <h4 className="text-md font-semibold text-blue-900 mb-3">
                Ejemplos de URLs Bloqueadas:
              </h4>
              <div className="bg-red-50 rounded-md p-3 border border-red-200">
                <div className="space-y-2">
                  <div className="flex items-center text-sm">
                    <svg className="w-4 h-4 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    <span className="font-mono text-red-700">http://127.0.0.1:8080/admin</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <svg className="w-4 h-4 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    <span className="font-mono text-red-700">https://malicious-site.com/image.jpg</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <svg className="w-4 h-4 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    <span className="font-mono text-red-700">ftp://internal.server.com/file</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Security Info */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-yellow-600 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <h5 className="text-sm font-medium text-yellow-800 mb-1">
                    Nota Importante
                  </h5>
                  <p className="text-xs text-yellow-700">
                    Estas medidas de seguridad se aplican tanto en el frontend como en el backend. 
                    Incluso si alguien intenta bypasear las validaciones del frontend, el backend 
                    realizará las mismas verificaciones para garantizar la seguridad.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SSRFProtectionInfo;