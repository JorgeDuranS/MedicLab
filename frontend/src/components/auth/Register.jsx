import React, { useState } from 'react';
import { authAPI, handleAPIError } from '../../services/api';
import { login, getDefaultRedirectPath } from '../../utils/auth';

const Register = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');
  const [passwordStrength, setPasswordStrength] = useState({
    score: 0,
    feedback: []
  });

  // Password strength validation
  const validatePasswordStrength = (password) => {
    const feedback = [];
    let score = 0;

    if (password.length >= 8) {
      score += 1;
    } else {
      feedback.push('Mínimo 8 caracteres');
    }

    if (/[a-z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Al menos una letra minúscula');
    }

    if (/[A-Z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Al menos una letra mayúscula');
    }

    if (/\d/.test(password)) {
      score += 1;
    } else {
      feedback.push('Al menos un número');
    }

    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      score += 1;
      feedback.push('Excelente: incluye símbolos especiales');
    }

    return { score, feedback };
  };

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

    // Update password strength for password field
    if (name === 'password') {
      const strength = validatePasswordStrength(value);
      setPasswordStrength(strength);
    }
  };

  // Validate form data
  const validateForm = () => {
    const newErrors = {};

    // First name validation
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'El nombre es requerido';
    } else if (formData.first_name.trim().length < 2) {
      newErrors.first_name = 'El nombre debe tener al menos 2 caracteres';
    }

    // Last name validation
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'El apellido es requerido';
    } else if (formData.last_name.trim().length < 2) {
      newErrors.last_name = 'El apellido debe tener al menos 2 caracteres';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Ingresa un email válido';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else {
      const strength = validatePasswordStrength(formData.password);
      if (strength.score < 4) {
        newErrors.password = 'La contraseña no cumple con los requisitos de seguridad';
      }
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Confirma tu contraseña';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden';
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
      const response = await authAPI.register({
        email: formData.email.trim(),
        password: formData.password,
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim()
      });

      // Extract token and user data from response
      const { access_token, user } = response;
      
      // Store authentication data
      login(access_token, user);
      
      // Redirect to patient dashboard (new registrations are patients by default)
      const redirectPath = getDefaultRedirectPath(user.role);
      window.location.href = redirectPath;
      
    } catch (error) {
      const errorMessage = handleAPIError(error);
      setGeneralError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Get password strength color
  const getPasswordStrengthColor = (score) => {
    if (score < 2) return 'bg-red-500';
    if (score < 3) return 'bg-yellow-500';
    if (score < 4) return 'bg-blue-500';
    return 'bg-green-500';
  };

  // Get password strength text
  const getPasswordStrengthText = (score) => {
    if (score < 2) return 'Débil';
    if (score < 3) return 'Regular';
    if (score < 4) return 'Buena';
    return 'Excelente';
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-8">
      <div className="card max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-heading-1 mb-2">MedicLab</h1>
          <p className="text-body-small">Crea tu cuenta de paciente</p>
        </div>

        {/* General Error Message */}
        {generalError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{generalError}</p>
          </div>
        )}

        {/* Register Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name Fields Row */}
          <div className="grid grid-cols-2 gap-4">
            {/* First Name */}
            <div>
              <label htmlFor="first_name" className="form-label">
                Nombre
              </label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className={`form-input ${errors.first_name ? 'border-red-500 focus:ring-red-500' : ''}`}
                placeholder="Juan"
                disabled={isLoading}
              />
              {errors.first_name && (
                <p className="form-error">{errors.first_name}</p>
              )}
            </div>

            {/* Last Name */}
            <div>
              <label htmlFor="last_name" className="form-label">
                Apellido
              </label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className={`form-input ${errors.last_name ? 'border-red-500 focus:ring-red-500' : ''}`}
                placeholder="Pérez"
                disabled={isLoading}
              />
              {errors.last_name && (
                <p className="form-error">{errors.last_name}</p>
              )}
            </div>
          </div>

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
              placeholder="Contraseña segura"
              disabled={isLoading}
            />
            
            {/* Password Strength Indicator */}
            {formData.password && (
              <div className="mt-2">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${getPasswordStrengthColor(passwordStrength.score)}`}
                      style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-professional-600">
                    {getPasswordStrengthText(passwordStrength.score)}
                  </span>
                </div>
                
                {/* Password Requirements */}
                {passwordStrength.feedback.length > 0 && (
                  <div className="text-xs text-professional-600">
                    <p className="mb-1">Requisitos:</p>
                    <ul className="list-disc list-inside space-y-0.5">
                      {passwordStrength.feedback.map((item, index) => (
                        <li key={index} className={item.includes('Excelente') ? 'text-green-600' : ''}>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            {errors.password && (
              <p className="form-error">{errors.password}</p>
            )}
          </div>

          {/* Confirm Password Field */}
          <div>
            <label htmlFor="confirmPassword" className="form-label">
              Confirmar Contraseña
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className={`form-input ${errors.confirmPassword ? 'border-red-500 focus:ring-red-500' : ''}`}
              placeholder="Repite tu contraseña"
              disabled={isLoading}
            />
            {errors.confirmPassword && (
              <p className="form-error">{errors.confirmPassword}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={`btn-primary w-full ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading ? 'Creando cuenta...' : 'Crear Cuenta'}
          </button>
        </form>

        {/* Switch to Login */}
        <div className="mt-6 text-center">
          <p className="text-body-small">
            ¿Ya tienes cuenta?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="text-mint-600 hover:text-mint-700 font-medium focus:outline-none focus:underline"
              disabled={isLoading}
            >
              Inicia sesión aquí
            </button>
          </p>
        </div>

        {/* Registration Info */}
        <div className="mt-8 p-4 bg-mint-50 border border-mint-200 rounded-md">
          <h4 className="text-sm font-medium text-mint-800 mb-2">Información:</h4>
          <p className="text-xs text-mint-700">
            Al registrarte, se creará una cuenta de paciente. Los médicos y administradores 
            son creados por el sistema administrativo.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;