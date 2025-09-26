import React, { useState, useEffect } from 'react';
import { userAPI, handleAPIError } from '../../services/api';
import { getUserRole } from '../../utils/auth';

const NewAppointmentModal = ({ isOpen, onClose, onAppointmentCreated, selectedDate }) => {
  const userRole = getUserRole();
  
  const [formData, setFormData] = useState({
    doctor_id: '',
    patient_id: '',
    appointment_date: '',
    description: ''
  });
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loadingOptions, setLoadingOptions] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadOptions();
      // Set initial date if provided
      if (selectedDate) {
        const dateStr = selectedDate.toISOString().slice(0, 16);
        setFormData(prev => ({ ...prev, appointment_date: dateStr }));
      }
    }
  }, [isOpen, selectedDate]);

  const loadOptions = async () => {
    try {
      setLoadingOptions(true);
      
      if (userRole === 'patient') {
        // Pacientes seleccionan médicos
        const doctorsData = await userAPI.getDoctors();
        setDoctors(doctorsData);
      } else if (userRole === 'doctor') {
        // Médicos seleccionan pacientes
        const patientsData = await userAPI.getPatients();
        setPatients(patientsData);
      }
    } catch (error) {
      console.error('Error loading options:', error);
      const errorMsg = userRole === 'patient' 
        ? 'Error al cargar la lista de médicos'
        : 'Error al cargar la lista de pacientes';
      setError(errorMsg);
    } finally {
      setLoadingOptions(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  const validateForm = () => {
    // Validar selección según el rol
    if (userRole === 'patient' && !formData.doctor_id) {
      setError('Por favor selecciona un médico');
      return false;
    }
    
    if (userRole === 'doctor' && !formData.patient_id) {
      setError('Por favor selecciona un paciente');
      return false;
    }
    
    if (!formData.appointment_date) {
      setError('Por favor selecciona fecha y hora');
      return false;
    }
    
    // Validate future date
    const appointmentDate = new Date(formData.appointment_date);
    const now = new Date();
    if (appointmentDate <= now) {
      setError('La fecha de la cita debe ser en el futuro');
      return false;
    }

    if (!formData.description.trim()) {
      setError('Por favor describe el motivo de la consulta');
      return false;
    }

    if (formData.description.length > 500) {
      setError('La descripción no puede exceder 500 caracteres');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      setLoading(true);
      setError(null);
      
      const appointmentData = {
        appointment_date: formData.appointment_date,
        description: formData.description.trim()
      };
      
      // Agregar doctor_id o patient_id según el rol
      if (userRole === 'patient') {
        appointmentData.doctor_id = parseInt(formData.doctor_id);
      } else if (userRole === 'doctor') {
        appointmentData.patient_id = parseInt(formData.patient_id);
      }

      await onAppointmentCreated(appointmentData);
      
      // Reset form and close modal
      setFormData({
        doctor_id: '',
        patient_id: '',
        appointment_date: '',
        description: ''
      });
      onClose();
    } catch (error) {
      console.error('Error creating appointment:', error);
      setError(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({
        doctor_id: '',
        patient_id: '',
        appointment_date: '',
        description: ''
      });
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-slate-700">
            {userRole === 'patient' ? 'Agendar Nueva Cita' : 'Crear Cita para Paciente'}
          </h2>
          <button
            onClick={handleClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Doctor/Patient Selection based on user role */}
          <div>
            <label htmlFor={userRole === 'patient' ? 'doctor_id' : 'patient_id'} className="block text-sm font-medium text-gray-700 mb-2">
              {userRole === 'patient' ? 'Médico *' : 'Paciente *'}
            </label>
            {loadingOptions ? (
              <div className="border border-gray-300 rounded-lg px-3 py-2 bg-gray-50">
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-teal-400 mr-2"></div>
                  <span className="text-gray-500">
                    {userRole === 'patient' ? 'Cargando médicos...' : 'Cargando pacientes...'}
                  </span>
                </div>
              </div>
            ) : (
              <select
                id={userRole === 'patient' ? 'doctor_id' : 'patient_id'}
                name={userRole === 'patient' ? 'doctor_id' : 'patient_id'}
                value={userRole === 'patient' ? formData.doctor_id : formData.patient_id}
                onChange={handleInputChange}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              >
                <option value="">
                  {userRole === 'patient' ? 'Selecciona un médico' : 'Selecciona un paciente'}
                </option>
                {userRole === 'patient' 
                  ? doctors.map(doctor => (
                      <option key={doctor.id} value={doctor.id}>
                        Dr. {doctor.first_name} {doctor.last_name}
                      </option>
                    ))
                  : patients.map(patient => (
                      <option key={patient.id} value={patient.id}>
                        {patient.first_name} {patient.last_name}
                      </option>
                    ))
                }
              </select>
            )}
          </div>

          {/* Date and Time */}
          <div>
            <label htmlFor="appointment_date" className="block text-sm font-medium text-gray-700 mb-2">
              Fecha y Hora *
            </label>
            <input
              type="datetime-local"
              id="appointment_date"
              name="appointment_date"
              value={formData.appointment_date}
              onChange={handleInputChange}
              min={new Date().toISOString().slice(0, 16)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              {userRole === 'patient' ? 'Motivo de la consulta *' : 'Descripción de la cita *'}
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder={
                userRole === 'patient' 
                  ? "Describe brevemente el motivo de tu consulta..."
                  : "Describe el motivo de la cita para el paciente..."
              }
              rows={4}
              maxLength={500}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
            />
            <div className="text-right text-xs text-gray-500 mt-1">
              {formData.description.length}/500 caracteres
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading || loadingOptions}
              className="flex-1 bg-teal-400 hover:bg-teal-500 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Agendando...
                </div>
              ) : (
                userRole === 'patient' ? 'Agendar Cita' : 'Crear Cita'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewAppointmentModal;