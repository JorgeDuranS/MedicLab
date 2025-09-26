import React, { useState } from 'react';

const Calendar = ({ 
  selectedDate, 
  onDateSelect, 
  appointmentDates = [],
  minDate = null,
  maxDate = null,
  className = '',
  ...props 
}) => {
  const [currentMonth, setCurrentMonth] = useState(selectedDate || new Date());

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

  const isDisabled = (date) => {
    if (!date) return true;
    
    // Check if date is in the past
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (date < today) return true;
    
    // Check min/max date constraints
    if (minDate && date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    
    return false;
  };

  const handleDateClick = (date) => {
    if (!date || isDisabled(date)) return;
    onDateSelect && onDateSelect(date);
  };

  const handleKeyDown = (e, date) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleDateClick(date);
    }
  };

  const days = getDaysInMonth(currentMonth);

  return (
    <div className={`calendar ${className}`} {...props}>
      {/* Calendar Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigateMonth(-1)}
          className="p-2 text-professional-600 hover:text-professional-800 hover:bg-professional-50 rounded-lg transition-colors focusable"
          aria-label="Mes anterior"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <h3 className="text-heading-3 text-professional-800">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h3>
        
        <button
          onClick={() => navigateMonth(1)}
          className="p-2 text-professional-600 hover:text-professional-800 hover:bg-professional-50 rounded-lg transition-colors focusable"
          aria-label="Mes siguiente"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Day Names Header */}
      <div className="grid grid-cols-7 gap-1 mb-3">
        {dayNames.map(day => (
          <div key={day} className="text-center text-body-small text-professional-600 py-2 font-medium">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1" role="grid" aria-label="Calendario">
        {days.map((date, index) => {
          if (!date) {
            return <div key={index} className="h-10" role="gridcell"></div>;
          }

          const isCurrentDay = isToday(date);
          const isSelectedDay = isSelected(date);
          const hasAppt = hasAppointment(date);
          const disabled = isDisabled(date);

          return (
            <button
              key={index}
              onClick={() => handleDateClick(date)}
              onKeyDown={(e) => handleKeyDown(e, date)}
              disabled={disabled}
              role="gridcell"
              tabIndex={isSelectedDay ? 0 : -1}
              className={`
                calendar-day relative h-10 text-sm font-medium rounded-full transition-all duration-200 focusable
                ${disabled 
                  ? 'text-professional-300 cursor-not-allowed opacity-50' 
                  : 'text-professional-800 hover:bg-mint-100 cursor-pointer'
                }
                ${isCurrentDay 
                  ? 'calendar-day-current' 
                  : ''
                }
                ${isSelectedDay 
                  ? 'calendar-day-selected' 
                  : ''
                }
                ${hasAppt && !isSelectedDay 
                  ? 'bg-mint-50 text-mint-800 border border-mint-200' 
                  : ''
                }
              `}
              aria-label={`${date.getDate()} de ${monthNames[date.getMonth()]}${hasAppt ? ', tiene cita' : ''}${isCurrentDay ? ', hoy' : ''}`}
              aria-selected={isSelectedDay}
              aria-current={isCurrentDay ? 'date' : undefined}
            >
              {date.getDate()}
              
              {/* Appointment indicator dot */}
              {hasAppt && (
                <div className={`
                  calendar-day-with-appointment absolute bottom-1 left-1/2 transform -translate-x-1/2
                  w-1.5 h-1.5 rounded-full
                  ${isSelectedDay ? 'bg-white' : 'bg-mint-500'}
                `}
                aria-hidden="true"
                ></div>
              )}
            </button>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 flex flex-wrap gap-4 text-body-small text-professional-600">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full border-2 border-mint-500" aria-hidden="true"></div>
          <span>Hoy</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-mint-500" aria-hidden="true"></div>
          <span>Seleccionado</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-mint-50 border border-mint-200 relative" aria-hidden="true">
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 rounded-full bg-mint-500"></div>
          </div>
          <span>Con cita</span>
        </div>
      </div>
    </div>
  );
};

export default Calendar;