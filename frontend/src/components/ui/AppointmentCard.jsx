import React from 'react';
import Card from './Card';
import Button from './Button';

const AppointmentCard = ({ 
  appointment, 
  userRole = 'patient', 
  onStatusUpdate,
  onClick,
  className = '',
  ...props 
}) => {
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

  const getStatusConfig = (status) => {
    switch (status) {
      case 'scheduled':
        return {
          className: 'status-confirmed',
          text: 'Programada',
          color: 'mint'
        };
      case 'completed':
        return {
          className: 'status-completed',
          text: 'Completada',
          color: 'professional'
        };
      case 'cancelled':
        return {
          className: 'status-cancelled',
          text: 'Cancelada',
          color: 'alert'
        };
      default:
        return {
          className: 'bg-professional-100 text-professional-800 px-3 py-1 rounded-full text-xs font-medium',
          text: 'Desconocido',
          color: 'professional'
        };
    }
  };

  const isUpcoming = (dateString) => {
    const appointmentDate = new Date(dateString);
    const now = new Date();
    return appointmentDate > now;
  };

  const isPast = (dateString) => {
    const appointmentDate = new Date(dateString);
    const now = new Date();
    return appointmentDate < now;
  };

  const handleStatusChange = (newStatus) => {
    if (onStatusUpdate) {
      onStatusUpdate(appointment.id, newStatus);
    }
  };

  const statusConfig = getStatusConfig(appointment.status);
  const upcoming = isUpcoming(appointment.appointment_date);
  const past = isPast(appointment.appointment_date);

  return (
    <Card 
      className={`appointment-card ${className}`}
      hover={!!onClick}
      onClick={onClick}
      padding="default"
      {...props}
    >
      {/* Header with date and status */}
      <Card.Header>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-heading-3 text-professional-800 mb-1">
              {formatDate(appointment.appointment_date)}
            </h3>
            <p className="text-body-main text-mint-600 font-medium">
              {formatTime(appointment.appointment_date)}
            </p>
          </div>
          <span className={statusConfig.className}>
            {statusConfig.text}
          </span>
        </div>
      </Card.Header>

      {/* Appointment details */}
      <Card.Content>
        <div className="space-y-3">
          {userRole === 'patient' && appointment.doctor && (
            <div className="flex items-center text-body-small text-professional-600">
              <svg 
                className="w-4 h-4 mr-3 text-professional-400" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" 
                />
              </svg>
              <span>Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}</span>
            </div>
          )}

          {(userRole === 'doctor' || userRole === 'admin') && appointment.patient && (
            <div className="flex items-center text-body-small text-professional-600">
              <svg 
                className="w-4 h-4 mr-3 text-professional-400" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" 
                />
              </svg>
              <span>Paciente: {appointment.patient.first_name} {appointment.patient.last_name}</span>
            </div>
          )}

          {appointment.description && (
            <div className="flex items-start text-body-small text-professional-600">
              <svg 
                className="w-4 h-4 mr-3 mt-0.5 text-professional-400 flex-shrink-0" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
                />
              </svg>
              <span className="flex-1">{appointment.description}</span>
            </div>
          )}
        </div>
      </Card.Content>

      {/* Action buttons for doctors */}
      {userRole === 'doctor' && appointment.status === 'scheduled' && upcoming && (
        <Card.Footer>
          <div className="flex gap-3 w-full">
            <Button
              variant="primary"
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleStatusChange('completed');
              }}
              className="flex-1"
            >
              Completar
            </Button>
            <Button
              variant="danger"
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleStatusChange('cancelled');
              }}
              className="flex-1"
            >
              Cancelar
            </Button>
          </div>
        </Card.Footer>
      )}

      {/* Status indicators */}
      {appointment.status === 'scheduled' && (
        <div className="mt-4 pt-4 border-t border-professional-200">
          {upcoming && (
            <div className="flex items-center text-body-small text-mint-600">
              <div className="w-2 h-2 bg-mint-500 rounded-full mr-2 animate-pulse" aria-hidden="true"></div>
              <span>Próxima cita</span>
            </div>
          )}

          {past && (
            <div className="flex items-center text-body-small text-alert">
              <svg 
                className="w-3 h-3 mr-2" 
                fill="currentColor" 
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path 
                  fillRule="evenodd" 
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" 
                  clipRule="evenodd" 
                />
              </svg>
              <span>Requiere atención</span>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default AppointmentCard;