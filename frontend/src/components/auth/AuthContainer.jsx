import React, { useState, useEffect } from 'react';
import { isAuthenticated, redirectToRoleDashboard } from '../../utils/auth';
import Login from './Login';
import Register from './Register';

const AuthContainer = ({ onLoginSuccess }) => {
  const [currentView, setCurrentView] = useState('login'); // 'login' or 'register'

  // Check if user is already authenticated on component mount
  useEffect(() => {
    if (isAuthenticated()) {
      // User is already logged in, call onLoginSuccess if provided
      if (onLoginSuccess) {
        onLoginSuccess();
      } else {
        // Fallback to redirect function
        redirectToRoleDashboard();
      }
    }
  }, [onLoginSuccess]);

  // Switch to register view
  const handleSwitchToRegister = () => {
    setCurrentView('register');
  };

  // Switch to login view
  const handleSwitchToLogin = () => {
    setCurrentView('login');
  };

  // Render current view
  if (currentView === 'register') {
    return (
      <Register onSwitchToLogin={handleSwitchToLogin} />
    );
  }

  return (
    <Login 
      onSwitchToRegister={handleSwitchToRegister} 
      onLoginSuccess={onLoginSuccess}
    />
  );
};

export default AuthContainer;