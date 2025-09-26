import React, { useState, useEffect, useRef } from 'react';
import { logout, getUserRole, getCurrentUser } from '../../utils/auth';

const Header = ({ onLogout, onNavigateToProfile, onNavigateToDashboard }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);
  const userRole = getUserRole();
  const currentUser = getCurrentUser();

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    logout();
    if (onLogout) {
      onLogout();
    }
  };

  const getRoleDisplayName = (role) => {
    switch (role) {
      case 'patient':
        return 'Paciente';
      case 'doctor':
        return 'Médico';
      case 'admin':
        return 'Administrador';
      default:
        return 'Usuario';
    }
  };

  const getRolePillColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      case 'doctor':
        return 'bg-teal-100 text-teal-800';
      case 'patient':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const toggleUserMenu = () => {
    setIsUserMenuOpen(!isUserMenuOpen);
  };

  const handleProfileClick = () => {
    if (onNavigateToProfile) {
      onNavigateToProfile();
    }
    setIsUserMenuOpen(false);
  };

  const handleDashboardClick = () => {
    if (onNavigateToDashboard) {
      onNavigateToDashboard();
    }
    setIsUserMenuOpen(false);
  };

  return (
    <>
      {/* Skip link for accessibility */}
      <a href="#main-content" className="skip-link focusable">
        Saltar al contenido principal
      </a>
      
      <header className="header-container">
        <div className="header-content">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="header-logo">
                <span className="text-mint-500">Medic</span>Lab
              </h1>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <div className="flex items-center space-x-4">
                {/* User Info */}
                <div className="header-user-info flex items-center space-x-3">
                  <p className="text-body-main text-professional-800">
                    {currentUser?.first_name} {currentUser?.last_name}
                  </p>
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${getRolePillColor(userRole)}`}>
                    {getRoleDisplayName(userRole)}
                  </span>
                </div>

                {/* User Menu Dropdown */}
                <div className="relative" ref={userMenuRef}>
                  <button
                    onClick={toggleUserMenu}
                    className="flex items-center space-x-2 p-2 rounded-md hover:bg-professional-100 focusable"
                    aria-expanded={isUserMenuOpen}
                    aria-label="Menú de usuario"
                  >
                    {/* User Avatar */}
                    <div className="header-avatar">
                      {currentUser?.avatar_url ? (
                        <img
                          src={currentUser.avatar_url}
                          alt="Avatar"
                          className="h-8 w-8 rounded-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <span className="text-white text-sm font-medium">
                        {currentUser?.first_name?.[0]}{currentUser?.last_name?.[0]}
                      </span>
                    </div>
                    <svg className="w-4 h-4 text-professional-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>

                  {/* Dropdown Menu */}
                  {isUserMenuOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                      <div className="py-1">
                        {onNavigateToDashboard && (
                          <button
                            onClick={handleDashboardClick}
                            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 focusable"
                          >
                            Dashboard
                          </button>
                        )}
                        {onNavigateToProfile && (
                          <button
                            onClick={handleProfileClick}
                            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 focusable"
                          >
                            Mi Perfil
                          </button>
                        )}
                        <hr className="my-1" />
                        <button
                          onClick={handleLogout}
                          className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 focusable"
                        >
                          Cerrar Sesión
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2 rounded-md text-professional-600 hover:text-professional-800 hover:bg-professional-100 focusable"
              aria-expanded={isMenuOpen}
              aria-label="Abrir menú principal"
            >
              <svg
                className="h-6 w-6"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 border-t border-professional-200">
              {/* User Info Mobile */}
              <div className="flex items-center space-x-3 px-3 py-2">
                <div className="h-10 w-10 rounded-full bg-mint-500 flex items-center justify-center">
                  {currentUser?.avatar_url ? (
                    <img
                      src={currentUser.avatar_url}
                      alt="Avatar"
                      className="h-10 w-10 rounded-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <span className="text-white font-medium">
                    {currentUser?.first_name?.[0]}{currentUser?.last_name?.[0]}
                  </span>
                </div>
                <div>
                  <p className="text-body-main text-professional-800">
                    {currentUser?.first_name} {currentUser?.last_name}
                  </p>
                  <span className={`inline-block mt-1 px-2 py-1 text-xs font-medium rounded-full ${getRolePillColor(userRole)}`}>
                    {getRoleDisplayName(userRole)}
                  </span>
                </div>
              </div>

              {/* Navigation Links Mobile */}
              <div className="px-3 py-2 space-y-2">
                {onNavigateToDashboard && (
                  <button
                    onClick={handleDashboardClick}
                    className="w-full text-left px-3 py-2 text-sm text-professional-700 hover:bg-professional-100 rounded-md focusable"
                  >
                    Dashboard
                  </button>
                )}
                {onNavigateToProfile && (
                  <button
                    onClick={handleProfileClick}
                    className="w-full text-left px-3 py-2 text-sm text-professional-700 hover:bg-professional-100 rounded-md focusable"
                  >
                    Mi Perfil
                  </button>
                )}
                <button
                  onClick={handleLogout}
                  className="w-full btn-secondary focusable"
                  aria-label="Cerrar sesión"
                >
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </div>
        )}
      </header>
    </>
  );
};

export default Header;