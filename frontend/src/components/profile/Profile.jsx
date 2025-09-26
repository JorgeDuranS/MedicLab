import React, { useState, useEffect } from 'react';
import { userAPI, handleAPIError } from '../../services/api';
import { getCurrentUser } from '../../utils/auth';
import AvatarUrlInput from '../ui/AvatarUrlInput';
import SSRFProtectionInfo from '../ui/SSRFProtectionInfo';
import SSRFValidationDemo from '../ui/SSRFValidationDemo';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [avatarUrl, setAvatarUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isValidUrl, setIsValidUrl] = useState(true);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      const userData = await userAPI.getProfile();
      setUser(userData);
      setAvatarUrl(userData.avatar_url || '');
    } catch (error) {
      setError(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUrlChange = (url) => {
    setAvatarUrl(url);
    setError('');
    setSuccess('');
  };

  const handleValidationChange = (validation) => {
    setIsValidUrl(validation.valid);
  };

  const handleUpdateAvatar = async (e) => {
    e.preventDefault();
    
    // Check if URL is valid
    if (!isValidUrl) {
      setError('Por favor, corrige los errores de validación antes de continuar');
      return;
    }

    if (!avatarUrl.trim()) {
      setError('La URL del avatar es requerida');
      return;
    }

    try {
      setUpdating(true);
      setError('');
      setSuccess('');

      await userAPI.updateAvatar({ avatar_url: avatarUrl });
      
      setSuccess('Avatar actualizado correctamente');
      // Reload user profile to get updated data
      await loadUserProfile();
    } catch (error) {
      setError(handleAPIError(error));
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-400 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando perfil...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-slate-700">Mi Perfil</h1>
          <p className="text-gray-600 mt-2">Gestiona tu información personal y configuración</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-slate-700 mb-6">Información Personal</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre Completo
                  </label>
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                    {user?.first_name} {user?.last_name}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                    {user?.email}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rol
                  </label>
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md capitalize">
                    {user?.role === 'patient' ? 'Paciente' : 
                     user?.role === 'doctor' ? 'Médico' : 
                     user?.role === 'admin' ? 'Administrador' : user?.role}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha de Registro
                  </label>
                  <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded-md">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString('es-ES') : 'No disponible'}
                  </p>
                </div>
              </div>
            </div>

            {/* SSRF Protection Information */}
            <SSRFProtectionInfo />

            {/* SSRF Validation Demo */}
            <SSRFValidationDemo />
          </div>

          {/* Avatar Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-slate-700 mb-6">Avatar</h2>
              
              {/* Avatar Update Form */}
              <form onSubmit={handleUpdateAvatar} className="space-y-6">
                <AvatarUrlInput
                  value={avatarUrl}
                  onChange={handleAvatarUrlChange}
                  onValidationChange={handleValidationChange}
                  disabled={updating}
                  showPreview={true}
                />

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-3">
                    <div className="flex items-start">
                      <svg className="w-5 h-5 text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                )}

                {/* Success Message */}
                {success && (
                  <div className="bg-green-50 border border-green-200 rounded-md p-3">
                    <div className="flex items-start">
                      <svg className="w-5 h-5 text-green-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <p className="text-sm text-green-700">{success}</p>
                    </div>
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={updating || !avatarUrl.trim() || !isValidUrl}
                  className="w-full bg-teal-400 hover:bg-teal-500 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors"
                >
                  {updating ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Actualizando...
                    </span>
                  ) : (
                    'Actualizar Avatar'
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;