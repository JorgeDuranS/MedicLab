import axios from 'axios';
import { getToken, removeToken } from '../utils/auth';

// Base API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, remove it and redirect to login
      removeToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication endpoints
export const authAPI = {
  // Register new user (patient)
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // Login user
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
};

// User management endpoints
export const userAPI = {
  // Get current user profile
  getProfile: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  // Update user avatar
  updateAvatar: async (avatarData) => {
    const response = await api.put('/users/me/avatar', avatarData);
    return response.data;
  },

  // Get list of doctors (for patients creating appointments)
  getDoctors: async () => {
    const response = await api.get('/users/doctors');
    return response.data;
  },

  // Get list of patients (for doctors creating appointments)
  getPatients: async () => {
    const response = await api.get('/users/patients');
    return response.data;
  },
};

// Appointments management endpoints
export const appointmentsAPI = {
  // Get appointments (filtered by user role automatically on backend)
  getAppointments: async (params = {}) => {
    const response = await api.get('/appointments', { params });
    return response.data;
  },

  // Create new appointment
  createAppointment: async (appointmentData) => {
    const response = await api.post('/appointments', appointmentData);
    return response.data;
  },

  // Update appointment (for doctors/admins)
  updateAppointment: async (appointmentId, updateData) => {
    const response = await api.put(`/appointments/${appointmentId}`, updateData);
    return response.data;
  },

  // Cancel appointment
  cancelAppointment: async (appointmentId) => {
    const response = await api.delete(`/appointments/${appointmentId}`);
    return response.data;
  },
};

// Admin endpoints (admin role only)
export const adminAPI = {
  // Get all users
  getAllUsers: async () => {
    const response = await api.get('/admin/users');
    return response.data;
  },

  // Get all appointments
  getAllAppointments: async () => {
    const response = await api.get('/admin/appointments');
    return response.data;
  },

  // Get security logs with filtering and pagination
  getSecurityLogs: async (params = {}) => {
    const response = await api.get('/admin/logs', { params });
    return response.data;
  },

  // Get available log action types
  getLogActions: async () => {
    const response = await api.get('/admin/logs/actions');
    return response.data;
  },
};

// Generic API error handler
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return data.error?.message || 'Datos inválidos';
      case 401:
        return 'No autorizado. Por favor, inicia sesión nuevamente';
      case 403:
        return 'No tienes permisos para realizar esta acción';
      case 404:
        return 'Recurso no encontrado';
      case 429:
        return 'Demasiadas solicitudes. Por favor, intenta más tarde';
      case 500:
        return 'Error interno del servidor. Por favor, intenta más tarde';
      default:
        return data.error?.message || 'Error desconocido';
    }
  } else if (error.request) {
    // Network error
    return 'Error de conexión. Verifica tu conexión a internet';
  } else {
    // Other error
    return error.message || 'Error desconocido';
  }
};

// Export default api instance for custom requests
export default api;