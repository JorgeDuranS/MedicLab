import React from 'react';

const AppointmentCard = ({ appointment, userRole = 'patient', onStatusUpdate }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled':
        return 'bg-teal-100 text-teal-800 border-teal-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'scheduled':
        return 'Programada';
      case 'completed':
        return 'Completada';
      case 'cancelled':
        return 'Cancelada';
      default:
        return 'Desconocido';
    }
  };

  const isUpcoming = (dateString) => {
    const appointmentDate = new Date(dateString);
    const now = new Date();
    return appointmentDate > now;
  };

  const handleStatusChange = (newStatus) => {
    if (onStatusUpdate) {
      onStatusUpdate(appointment.id, newStatus);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-1">
      {/* Header with date and status */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold text-slate-700 text-lg">
            {formatDate(appointment.appointment_date)}
          </h3>
          <p className="text-teal-600 font-medium">
            {formatTime(appointment.appointment_date)}
          </p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(appointment.status)}`}>
          {getStatusText(appointment.status)}
        </span>
      </div>

      {/* Appointment details */}
      <div className="space-y-2 mb-4">
        {userRole === 'patient' && appointment.doctor && (
          <div className="flex items-center text-sm text-gray-600">
            <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}</span>
          </div>
        )}

        {userRole === 'doctor' && appointment.patient && (
          <div className="flex items-center text-sm text-gray-600">
            <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Paciente: {appointment.patient.first_name} {appointment.patient.last_name}</span>
          </div>
        )}

        {appointment.description && (
          <div className="flex items-start text-sm text-gray-600">
            <svg className="w-4 h-4 mr-2 mt-0.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="flex-1">{appointment.description}</span>
          </div>
        )}
      </div>

      {/* Action buttons for doctors */}
      {userRole === 'doctor' && appointment.status === 'scheduled' && isUpcoming(appointment.appointment_date) && (
        <div className="flex gap-2 pt-3 border-t border-gray-100">
          <button
            onClick={() => handleStatusChange('completed')}
            className="flex-1 bg-green-50 hover:bg-green-100 text-green-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Marcar Completada
          </button>
          <button
            onClick={() => handleStatusChange('cancelled')}
            className="flex-1 bg-red-50 hover:bg-red-100 text-red-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Cancelar
          </button>
        </div>
      )}

      {/* Upcoming appointment indicator */}
      {appointment.status === 'scheduled' && isUpcoming(appointment.appointment_date) && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center text-xs text-teal-600">
            <div className="w-2 h-2 bg-teal-400 rounded-full mr-2 animate-pulse"></div>
            <span>Próxima cita</span>
          </div>
        </div>
      )}

      {/* Past appointment indicator */}
      {appointment.status === 'scheduled' && !isUpcoming(appointment.appointment_date) && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center text-xs text-amber-600">
            <svg className="w-3 h-3 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>Requiere atención</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AppointmentCard;