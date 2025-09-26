import React, { useState } from 'react';
import { authAPI, handleAPIError } from '../../services/api';
import { login, getDefaultRedirectPath } from '../../utils/auth';

const Login = ({ onSwitchToRegister, onLoginSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear field-specific error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    
    // Clear general error
    if (generalError) {
      setGeneralError('');
    }
  };

  // Validate form data
  const validateForm = () => {
    const newErrors = {};

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Ingresa un email válido';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setGeneralError('');

    try {
      const response = await authAPI.login({
        email: formData.email.trim(),
        password: formData.password
      });

      // Extract token and user data from response
      const { access_token, user } = response;
      
      // Store authentication data
      login(access_token, user);
      
      // Call onLoginSuccess if provided, otherwise use default redirect
      if (onLoginSuccess) {
        onLoginSuccess();
      } else {
        // Fallback to redirect
        const redirectPath = getDefaultRedirectPath(user.role);
        window.location.href = redirectPath;
      }
      
    } catch (error) {
      const errorMessage = handleAPIError(error);
      setGeneralError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="card max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-heading-1 mb-2">MedicLab</h1>
          <p className="text-body-small">Inicia sesión en tu cuenta</p>
        </div>

        {/* General Error Message */}
        {generalError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{generalError}</p>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email Field */}
          <div>
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`form-input ${errors.email ? 'border-red-500 focus:ring-red-500' : ''}`}
              placeholder="tu@email.com"
              disabled={isLoading}
            />
            {errors.email && (
              <p className="form-error">{errors.email}</p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="form-label">
              Contraseña
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`form-input ${errors.password ? 'border-red-500 focus:ring-red-500' : ''}`}
              placeholder="Tu contraseña"
              disabled={isLoading}
            />
            {errors.password && (
              <p className="form-error">{errors.password}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={`btn-primary w-full ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>

        {/* Switch to Register */}
        <div className="mt-6 text-center">
          <p className="text-body-small">
            ¿No tienes cuenta?{' '}
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="text-mint-600 hover:text-mint-700 font-medium focus:outline-none focus:underline"
              disabled={isLoading}
            >
              Regístrate aquí
            </button>
          </p>
        </div>

        {/* Demo Credentials Info */}
        <div className="mt-8 p-4 bg-mint-50 border border-mint-200 rounded-md">
          <h4 className="text-sm font-medium text-mint-800 mb-2">Credenciales de Demo:</h4>
          <div className="text-xs text-mint-700 space-y-1">
            <p><strong>Paciente:</strong> patient@mediclab.com / Patient123!</p>
            <p><strong>Médico:</strong> dr.garcia@mediclab.com / Doctor123!</p>
            <p><strong>Admin:</strong> admin@mediclab.com / Admin123!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;