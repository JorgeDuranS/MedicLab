import React from 'react';
import { getUserRole } from '../../utils/auth';

const Navigation = ({ currentView, onViewChange }) => {
  const userRole = getUserRole();

  const getNavigationItems = () => {
    const baseItems = [
      { id: 'dashboard', label: 'Dashboard', icon: 'home' }
    ];

    switch (userRole) {
      case 'patient':
        return [
          ...baseItems,
          { id: 'appointments', label: 'Mis Citas', icon: 'calendar' },
          { id: 'profile', label: 'Perfil', icon: 'user' }
        ];
      case 'doctor':
        return [
          ...baseItems,
          { id: 'appointments', label: 'Mi Agenda', icon: 'calendar' },
          { id: 'patients', label: 'Pacientes', icon: 'users' },
          { id: 'profile', label: 'Perfil', icon: 'user' }
        ];
      case 'admin':
        return [
          ...baseItems,
          { id: 'users', label: 'Usuarios', icon: 'users' },
          { id: 'appointments', label: 'Todas las Citas', icon: 'calendar' },
          { id: 'reports', label: 'Reportes', icon: 'chart' }
        ];
      default:
        return baseItems;
    }
  };

  const getIcon = (iconName) => {
    const iconClasses = "h-5 w-5";
    
    switch (iconName) {
      case 'home':
        return (
          <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        );
      case 'calendar':
        return (
          <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        );
      case 'user':
        return (
          <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        );
      case 'users':
        return (
          <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
          </svg>
        );
      case 'chart':
        return (
          <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        );
      default:
        return (
          <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        );
    }
  };

  const navigationItems = getNavigationItems();

  return (
    <nav className="bg-card border-r border-professional-200" aria-label="Navegación principal">
      <div className="px-4 py-6">
        <ul className="space-y-2">
          {navigationItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => onViewChange && onViewChange(item.id)}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 focusable ${
                  currentView === item.id
                    ? 'bg-mint-100 text-mint-800 border-l-4 border-mint-500'
                    : 'text-professional-600 hover:text-professional-800 hover:bg-professional-50'
                }`}
                aria-current={currentView === item.id ? 'page' : undefined}
              >
                <span className="mr-3">
                  {getIcon(item.icon)}
                </span>
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;