// JWT token management utilities

const TOKEN_KEY = 'mediclab_token';
const USER_KEY = 'mediclab_user';

// Token management functions
export const getToken = () => {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch (error) {
    console.error('Error getting token from localStorage:', error);
    return null;
  }
};

export const setToken = (token) => {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch (error) {
    console.error('Error setting token in localStorage:', error);
  }
};

export const removeToken = () => {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (error) {
    console.error('Error removing token from localStorage:', error);
  }
};

// User data management functions
export const getUser = () => {
  try {
    const userData = localStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error('Error getting user data from localStorage:', error);
    return null;
  }
};

export const setUser = (user) => {
  try {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (error) {
    console.error('Error setting user data in localStorage:', error);
  }
};

// JWT token validation and parsing
export const isTokenValid = (token = null) => {
  const tokenToCheck = token || getToken();
  
  if (!tokenToCheck) {
    return false;
  }

  try {
    // Parse JWT token to check expiration
    const payload = JSON.parse(atob(tokenToCheck.split('.')[1]));
    const currentTime = Date.now() / 1000;
    
    // Check if token is expired
    if (payload.exp && payload.exp < currentTime) {
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Error validating token:', error);
    return false;
  }
};

export const getTokenPayload = (token = null) => {
  const tokenToCheck = token || getToken();
  
  if (!tokenToCheck) {
    return null;
  }

  try {
    return JSON.parse(atob(tokenToCheck.split('.')[1]));
  } catch (error) {
    console.error('Error parsing token payload:', error);
    return null;
  }
};

// Authentication status functions
export const isAuthenticated = () => {
  const token = getToken();
  return token && isTokenValid(token);
};

export const getCurrentUser = () => {
  if (!isAuthenticated()) {
    return null;
  }
  
  // Try to get user from localStorage first
  let user = getUser();
  
  // If not in localStorage, try to get from token payload
  if (!user) {
    const payload = getTokenPayload();
    if (payload) {
      user = {
        id: payload.sub,
        email: payload.email,
        role: payload.role,
      };
    }
  }
  
  return user;
};

// Role verification functions
export const getUserRole = () => {
  const user = getCurrentUser();
  return user?.role || null;
};

export const hasRole = (requiredRole) => {
  const userRole = getUserRole();
  return userRole === requiredRole;
};

export const isPatient = () => hasRole('patient');
export const isDoctor = () => hasRole('doctor');
export const isAdmin = () => hasRole('admin');

// Role-based access control
export const canAccessPatientFeatures = () => {
  return isPatient() || isDoctor() || isAdmin();
};

export const canAccessDoctorFeatures = () => {
  return isDoctor() || isAdmin();
};

export const canAccessAdminFeatures = () => {
  return isAdmin();
};

// Login/logout functions
export const login = (token, user) => {
  setToken(token);
  setUser(user);
};

export const logout = () => {
  removeToken();
  // Note: Redirect handling is done by the calling component
};

// Redirect functions based on role
export const getDefaultRedirectPath = (role) => {
  switch (role) {
    case 'patient':
      return '/dashboard';
    case 'doctor':
      return '/dashboard';
    case 'admin':
      return '/admin';
    default:
      return '/dashboard';
  }
};

export const redirectToRoleDashboard = () => {
  const role = getUserRole();
  if (role) {
    const path = getDefaultRedirectPath(role);
    window.location.href = path;
  }
};

// Route protection utilities
export const requireAuth = () => {
  if (!isAuthenticated()) {
    window.location.href = '/login';
    return false;
  }
  return true;
};

export const requireRole = (requiredRole) => {
  if (!requireAuth()) {
    return false;
  }
  
  if (!hasRole(requiredRole)) {
    // Redirect to appropriate dashboard or show error
    redirectToRoleDashboard();
    return false;
  }
  
  return true;
};

export const requireAnyRole = (allowedRoles) => {
  if (!requireAuth()) {
    return false;
  }
  
  const userRole = getUserRole();
  if (!allowedRoles.includes(userRole)) {
    redirectToRoleDashboard();
    return false;
  }
  
  return true;
};

// Auto-logout on token expiration
export const setupTokenExpirationCheck = () => {
  const checkInterval = 60000; // Check every minute
  
  const checkTokenExpiration = () => {
    if (getToken() && !isTokenValid()) {
      console.log('Token expired, logging out...');
      logout();
    }
  };
  
  // Check immediately
  checkTokenExpiration();
  
  // Set up interval check
  return setInterval(checkTokenExpiration, checkInterval);
};

// Initialize auth utilities
export const initializeAuth = () => {
  // Clean up invalid tokens on app start
  if (getToken() && !isTokenValid()) {
    removeToken();
  }
  
  // Set up token expiration monitoring
  return setupTokenExpirationCheck();
};