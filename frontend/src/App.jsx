import React, { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import PatientDashboard from './pages/PatientDashboard';
import DoctorDashboard from './pages/DoctorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import ProfilePage from './pages/ProfilePage';
import Layout from './components/layout/Layout';
import { getToken, getUserRole, logout } from './utils/auth';

function App() {
  const [currentView, setCurrentView] = useState('loading');
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    // Check if user is logged in and determine their role
    const token = getToken();
    if (token) {
      const role = getUserRole();
      setUserRole(role);
      setCurrentView('dashboard');
    } else {
      setCurrentView('login');
    }
  }, []);

  // Handle login success
  const handleLoginSuccess = () => {
    const role = getUserRole();
    setUserRole(role);
    setCurrentView('dashboard');
  };

  // Handle logout
  const handleLogout = () => {
    logout();
    setCurrentView('login');
    setUserRole(null);
  };

  // Handle navigation to profile
  const handleNavigateToProfile = () => {
    setCurrentView('profile');
  };

  // Handle navigation back to dashboard
  const handleNavigateToDashboard = () => {
    setCurrentView('dashboard');
  };

  // Loading state
  if (currentView === 'loading') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-400 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  // Login page
  if (currentView === 'login') {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  // Dashboard based on user role
  if (currentView === 'dashboard') {
    let DashboardComponent;
    switch (userRole) {
      case 'patient':
        DashboardComponent = PatientDashboard;
        break;
      case 'doctor':
        DashboardComponent = DoctorDashboard;
        break;
      case 'admin':
        DashboardComponent = AdminDashboard;
        break;
      default:
        // Invalid role, redirect to login
        localStorage.removeItem('token');
        setCurrentView('login');
        return <LoginPage onLoginSuccess={handleLoginSuccess} />;
    }

    return (
      <Layout onLogout={handleLogout} onNavigateToProfile={handleNavigateToProfile}>
        <DashboardComponent />
      </Layout>
    );
  }

  // Profile page
  if (currentView === 'profile') {
    return (
      <Layout onLogout={handleLogout} onNavigateToDashboard={handleNavigateToDashboard}>
        <ProfilePage />
      </Layout>
    );
  }

  // Fallback - should not reach here
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-slate-700 mb-4">MedicLab</h1>
        <p className="text-gray-600 mb-4">Error de navegación</p>
        <button
          onClick={() => {
            localStorage.removeItem('token');
            setCurrentView('login');
          }}
          className="bg-teal-400 hover:bg-teal-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          Ir al Login
        </button>
      </div>
    </div>
  )
}

export default App