import React from 'react';
import Header from './Header';

const Layout = ({ children, onLogout, onNavigateToProfile, onNavigateToDashboard }) => {
  return (
    <div className="dashboard-layout">
      <Header 
        onLogout={onLogout} 
        onNavigateToProfile={onNavigateToProfile}
        onNavigateToDashboard={onNavigateToDashboard}
      />
      <main id="main-content" className="dashboard-container" tabIndex="-1">
        {children}
      </main>
    </div>
  );
};

export default Layout;