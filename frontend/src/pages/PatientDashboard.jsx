import React, { useState, useEffect } from 'react';
import { getUserRole } from '../utils/auth';
import { appointmentsAPI, userAPI, handleAPIError } from '../services/api';
import Calendar from '../components/Calendar';
import AppointmentList from '../components/appointments/AppointmentList';
import NewAppointmentModal from '../components/appointments/NewAppointmentModal';

const PatientDashboard = () => {
  const [user, setUser] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNewAppointmentModal, setShowNewAppointmentModal] = useState(false);

  useEffect(() => {
    // Get user info from token
    const userRole = getUserRole();
    if (userRole !== 'patient') {
      // Redirect if not patient
      window.location.href = '/login';
      return;
    }
    
    loadUserData();
    loadAppointments();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await userAPI.getProfile();
      setUser(userData);
    } catch (error) {
      console.error('Error loading user data:', error);
      // Fallback to mock data if API fails
      setUser({
        firstName: 'Juan',
        lastName: 'Pérez',
        email: 'juan.perez@email.com'
      });
    }
  };

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const appointmentsData = await appointmentsAPI.getAppointments();
      setAppointments(appointmentsData);
      setError(null);
    } catch (error) {
      console.error('Error loading appointments:', error);
      setError(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  // Extract dates that have appointments for calendar highlighting
  const getAppointmentDates = () => {
    return appointments.map(appointment => appointment.appointment_date);
  };

  // Handle creating new appointment
  const handleCreateAppointment = async (appointmentData) => {
    try {
      const newAppointment = await appointmentsAPI.createAppointment(appointmentData);
      
      // Add the new appointment to the list
      setAppointments(prev => [...prev, newAppointment]);
      
      // Show success message (you could add a toast notification here)
      console.log('Appointment created successfully:', newAppointment);
      
      return newAppointment;
    } catch (error) {
      console.error('Error creating appointment:', error);
      throw error; // Re-throw to let the modal handle the error
    }
  };

  // Handle opening new appointment modal with selected date
  const handleNewAppointmentClick = () => {
    setShowNewAppointmentModal(true);
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-400 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Main Content - 2 Column Layout */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Left Column - Calendar (40% width on desktop) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-slate-700 mb-4">
                Calendario
              </h2>
              {loading ? (
                <div className="h-80 bg-gray-50 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-400 mx-auto"></div>
                    <p className="mt-2 text-gray-500">Cargando citas...</p>
                  </div>
                </div>
              ) : (
                <Calendar
                  selectedDate={selectedDate}
                  onDateSelect={setSelectedDate}
                  appointmentDates={getAppointmentDates()}
                />
              )}
            </div>
          </div>

          {/* Right Column - Appointments List (60% width on desktop) */}
          <div className="lg:col-span-3">
            <div className="space-y-6">
              {/* New Appointment Button */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-lg font-semibold text-slate-700">
                    Mis Próximas Citas
                  </h2>
                  <button 
                    onClick={handleNewAppointmentClick}
                    className="bg-teal-400 hover:bg-teal-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    + Agendar Nueva Cita
                  </button>
                </div>
              </div>

              {/* Appointments List */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <AppointmentList
                  appointments={appointments}
                  userRole="patient"
                  loading={loading}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Layout - Responsive Design */}
        <div className="lg:hidden mt-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="flex space-x-1 mb-4">
              <button className="flex-1 py-2 px-4 text-sm font-medium text-teal-600 bg-teal-50 rounded-lg">
                Calendario
              </button>
              <button className="flex-1 py-2 px-4 text-sm font-medium text-gray-500 hover:text-gray-700 rounded-lg">
                Mis Citas
              </button>
            </div>
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Vista móvil (próximamente)</p>
            </div>
          </div>
        </div>
      </main>

      {/* New Appointment Modal */}
      <NewAppointmentModal
        isOpen={showNewAppointmentModal}
        onClose={() => setShowNewAppointmentModal(false)}
        onAppointmentCreated={handleCreateAppointment}
        selectedDate={selectedDate}
      />
    </div>
  );
};

export default PatientDashboard;