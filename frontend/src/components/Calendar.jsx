import React, { useState } from 'react';

const Calendar = ({ selectedDate, onDateSelect, appointmentDates = [] }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }

    return days;
  };

  const navigateMonth = (direction) => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() + direction);
      return newMonth;
    });
  };

  const isToday = (date) => {
    if (!date) return false;
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isSelected = (date) => {
    if (!date || !selectedDate) return false;
    return date.toDateString() === selectedDate.toDateString();
  };

  const hasAppointment = (date) => {
    if (!date) return false;
    return appointmentDates.some(appointmentDate => {
      const apptDate = new Date(appointmentDate);
      return date.toDateString() === apptDate.toDateString();
    });
  };

  const isPastDate = (date) => {
    if (!date) return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };

  const handleDateClick = (date) => {
    if (!date || isPastDate(date)) return;
    onDateSelect && onDateSelect(date);
  };

  const days = getDaysInMonth(currentMonth);

  return (
    <div className="w-full">
      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => navigateMonth(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Mes anterior"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <h3 className="text-lg font-semibold text-slate-700">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h3>
        
        <button
          onClick={() => navigateMonth(1)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Mes siguiente"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Day Names Header */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {dayNames.map(day => (
          <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((date, index) => {
          if (!date) {
            return <div key={index} className="h-10"></div>;
          }

          const isCurrentDay = isToday(date);
          const isSelectedDay = isSelected(date);
          const hasAppt = hasAppointment(date);
          const isPast = isPastDate(date);

          return (
            <button
              key={index}
              onClick={() => handleDateClick(date)}
              disabled={isPast}
              className={`
                relative h-10 text-sm font-medium rounded-lg transition-all duration-200
                ${isPast 
                  ? 'text-gray-300 cursor-not-allowed' 
                  : 'text-slate-700 hover:bg-gray-100 cursor-pointer'
                }
                ${isCurrentDay 
                  ? 'ring-2 ring-teal-400 ring-offset-1' 
                  : ''
                }
                ${isSelectedDay 
                  ? 'bg-teal-400 text-white hover:bg-teal-500' 
                  : ''
                }
                ${hasAppt && !isSelectedDay 
                  ? 'bg-teal-50 text-teal-700' 
                  : ''
                }
              `}
              aria-label={`${date.getDate()} de ${monthNames[date.getMonth()]}`}
            >
              {date.getDate()}
              
              {/* Appointment indicator dot */}
              {hasAppt && (
                <div className={`
                  absolute bottom-1 left-1/2 transform -translate-x-1/2
                  w-1 h-1 rounded-full
                  ${isSelectedDay ? 'bg-white' : 'bg-teal-400'}
                `}></div>
              )}
            </button>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded border-2 border-teal-400"></div>
          <span>Hoy</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-teal-400"></div>
          <span>Seleccionado</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-teal-50 border border-teal-200 relative">
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 rounded-full bg-teal-400"></div>
          </div>
          <span>Con cita</span>
        </div>
      </div>
    </div>
  );
};

export default Calendar;