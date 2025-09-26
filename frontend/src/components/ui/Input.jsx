import React, { forwardRef } from 'react';

const Input = forwardRef(({ 
  label,
  error,
  helperText,
  required = false,
  className = '',
  containerClassName = '',
  type = 'text',
  id,
  ...props 
}, ref) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  const errorId = error ? `${inputId}-error` : undefined;
  const helperId = helperText ? `${inputId}-helper` : undefined;

  const inputClasses = `
    form-input
    ${error ? 'border-alert focus:ring-alert focus:border-alert' : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <div className={`space-y-2 ${containerClassName}`}>
      {label && (
        <label 
          htmlFor={inputId} 
          className="form-label"
        >
          {label}
          {required && (
            <span className="text-alert ml-1" aria-label="requerido">*</span>
          )}
        </label>
      )}
      
      <input
        ref={ref}
        type={type}
        id={inputId}
        className={inputClasses}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={[errorId, helperId].filter(Boolean).join(' ') || undefined}
        required={required}
        {...props}
      />
      
      {error && (
        <p id={errorId} className="form-error" role="alert">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p id={helperId} className="text-body-small text-professional-500">
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

// Textarea variant
const Textarea = forwardRef(({ 
  label,
  error,
  helperText,
  required = false,
  className = '',
  containerClassName = '',
  rows = 3,
  id,
  ...props 
}, ref) => {
  const inputId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
  const errorId = error ? `${inputId}-error` : undefined;
  const helperId = helperText ? `${inputId}-helper` : undefined;

  const textareaClasses = `
    form-input resize-vertical
    ${error ? 'border-alert focus:ring-alert focus:border-alert' : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <div className={`space-y-2 ${containerClassName}`}>
      {label && (
        <label 
          htmlFor={inputId} 
          className="form-label"
        >
          {label}
          {required && (
            <span className="text-alert ml-1" aria-label="requerido">*</span>
          )}
        </label>
      )}
      
      <textarea
        ref={ref}
        id={inputId}
        rows={rows}
        className={textareaClasses}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={[errorId, helperId].filter(Boolean).join(' ') || undefined}
        required={required}
        {...props}
      />
      
      {error && (
        <p id={errorId} className="form-error" role="alert">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p id={helperId} className="text-body-small text-professional-500">
          {helperText}
        </p>
      )}
    </div>
  );
});

Textarea.displayName = 'Textarea';

// Select variant
const Select = forwardRef(({ 
  label,
  error,
  helperText,
  required = false,
  className = '',
  containerClassName = '',
  children,
  placeholder,
  id,
  ...props 
}, ref) => {
  const inputId = id || `select-${Math.random().toString(36).substr(2, 9)}`;
  const errorId = error ? `${inputId}-error` : undefined;
  const helperId = helperText ? `${inputId}-helper` : undefined;

  const selectClasses = `
    form-input appearance-none bg-white
    ${error ? 'border-alert focus:ring-alert focus:border-alert' : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <div className={`space-y-2 ${containerClassName}`}>
      {label && (
        <label 
          htmlFor={inputId} 
          className="form-label"
        >
          {label}
          {required && (
            <span className="text-alert ml-1" aria-label="requerido">*</span>
          )}
        </label>
      )}
      
      <div className="relative">
        <select
          ref={ref}
          id={inputId}
          className={selectClasses}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={[errorId, helperId].filter(Boolean).join(' ') || undefined}
          required={required}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {children}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-professional-400">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      
      {error && (
        <p id={errorId} className="form-error" role="alert">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p id={helperId} className="text-body-small text-professional-500">
          {helperText}
        </p>
      )}
    </div>
  );
});

Select.displayName = 'Select';

// Attach variants to main Input component
Input.Textarea = Textarea;
Input.Select = Select;

export default Input;