import React, { useState, useMemo } from 'react';
import AppointmentCard from './AppointmentCard';

const AppointmentList = ({ appointments, userRole = 'patient', onStatusUpdate, loading = false }) => {
  const [filter, setFilter] = useState('upcoming'); // 'upcoming', 'past', 'all'
  const [sortBy, setSortBy] = useState('date'); // 'date', 'status'

  // Filter and sort appointments
  const filteredAndSortedAppointments = useMemo(() => {
    let filtered = [...appointments];
    const now = new Date();

    // Apply filter
    switch (filter) {
      case 'upcoming':
        filtered = filtered.filter(apt => {
          const aptDate = new Date(apt.appointment_date);
          return aptDate > now && apt.status !== 'cancelled';
        });
        break;
      case 'past':
        filtered = filtered.filter(apt => {
          const aptDate = new Date(apt.appointment_date);
          return aptDate <= now || apt.status === 'completed';
        });
        break;
      case 'all':
      default:
        // No additional filtering
        break;
    }

    // Apply sorting
    filtered.sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(a.appointment_date) - new Date(b.appointment_date);
      } else if (sortBy === 'status') {
        const statusOrder = { 'scheduled': 0, 'completed': 1, 'cancelled': 2 };
        return statusOrder[a.status] - statusOrder[b.status];
      }
      return 0;
    });

    return filtered;
  }, [appointments, filter, sortBy]);

  const getFilterCount = (filterType) => {
    const now = new Date();
    switch (filterType) {
      case 'upcoming':
        return appointments.filter(apt => {
          const aptDate = new Date(apt.appointment_date);
          return aptDate > now && apt.status !== 'cancelled';
        }).length;
      case 'past':
        return appointments.filter(apt => {
          const aptDate = new Date(apt.appointment_date);
          return aptDate <= now || apt.status === 'completed';
        }).length;
      case 'all':
        return appointments.length;
      default:
        return 0;
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="bg-white border border-gray-200 rounded-lg p-4 animate-pulse">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="h-5 bg-gray-200 rounded w-48 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-20"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded-full w-20"></div>
            </div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-32"></div>
              <div className="h-4 bg-gray-200 rounded w-full"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter and Sort Controls */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        {/* Filter Tabs */}
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setFilter('upcoming')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
              filter === 'upcoming'
                ? 'bg-white text-teal-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Próximas ({getFilterCount('upcoming')})
          </button>
          <button
            onClick={() => setFilter('past')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
              filter === 'past'
                ? 'bg-white text-teal-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Pasadas ({getFilterCount('past')})
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
              filter === 'all'
                ? 'bg-white text-teal-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Todas ({getFilterCount('all')})
          </button>
        </div>

        {/* Sort Dropdown */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
        >
          <option value="date">Ordenar por fecha</option>
          <option value="status">Ordenar por estado</option>
        </select>
      </div>

      {/* Appointments List */}
      {filteredAndSortedAppointments.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 0V7a2 2 0 012-2h4a2 2 0 012 2v0M8 7v10a2 2 0 002 2h4a2 2 0 002-2V7M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V9a2 2 0 00-2-2h-2" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {filter === 'upcoming' && 'No tienes citas próximas'}
            {filter === 'past' && 'No tienes citas pasadas'}
            {filter === 'all' && 'No tienes citas registradas'}
          </h3>
          <p className="text-gray-500 mb-4">
            {filter === 'upcoming' && 'Agenda tu primera cita médica'}
            {filter === 'past' && 'Tus citas completadas aparecerán aquí'}
            {filter === 'all' && 'Comienza agendando tu primera cita médica'}
          </p>
          {filter !== 'past' && (
            <button className="bg-teal-400 hover:bg-teal-500 text-white px-6 py-2 rounded-lg font-medium transition-colors">
              + Agendar Nueva Cita
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAndSortedAppointments.map(appointment => (
            <AppointmentCard
              key={appointment.id}
              appointment={appointment}
              userRole={userRole}
              onStatusUpdate={onStatusUpdate}
            />
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {appointments.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-teal-600">
                {getFilterCount('upcoming')}
              </div>
              <div className="text-sm text-gray-600">Próximas</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {appointments.filter(apt => apt.status === 'completed').length}
              </div>
              <div className="text-sm text-gray-600">Completadas</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-600">
                {appointments.length}
              </div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AppointmentList;