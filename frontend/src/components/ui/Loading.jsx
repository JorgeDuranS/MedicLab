import React from 'react';

const Loading = ({ 
  size = 'medium', 
  text = 'Cargando...', 
  fullScreen = false,
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  };

  const textSizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  };

  const spinnerClasses = `animate-spin rounded-full border-b-2 border-mint-500 ${sizeClasses[size]}`;

  const content = (
    <div className={`flex flex-col items-center justify-center space-y-4 ${className}`} {...props}>
      <div className={spinnerClasses} role="status" aria-label="Cargando">
        <span className="sr-only">Cargando...</span>
      </div>
      {text && (
        <p className={`text-professional-600 ${textSizeClasses[size]}`}>
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};

// Inline loading spinner for buttons
Loading.Spinner = ({ size = 'small', className = '', ...props }) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-5 w-5',
    large: 'h-6 w-6'
  };

  return (
    <svg 
      className={`animate-spin ${sizeClasses[size]} ${className}`}
      fill="none" 
      viewBox="0 0 24 24"
      role="status"
      aria-label="Cargando"
      {...props}
    >
      <circle 
        className="opacity-25" 
        cx="12" 
        cy="12" 
        r="10" 
        stroke="currentColor" 
        strokeWidth="4"
      />
      <path 
        className="opacity-75" 
        fill="currentColor" 
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

export default Loading;