import React from 'react';
import { AuthContainer } from '../components/auth';

const LoginPage = ({ onLoginSuccess }) => {
  return <AuthContainer onLoginSuccess={onLoginSuccess} />;
};

export default LoginPage;