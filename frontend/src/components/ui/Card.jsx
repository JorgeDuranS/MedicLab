import React from 'react';

const Card = ({ 
  children, 
  variant = 'default',
  hover = false,
  padding = 'default',
  className = '',
  onClick,
  ...props 
}) => {
  const baseClasses = 'card';
  
  const variantClasses = {
    default: 'bg-card',
    elevated: 'bg-card shadow-card-hover',
    outlined: 'bg-card border border-professional-200',
    flat: 'bg-card shadow-none'
  };
  
  const paddingClasses = {
    none: 'p-0',
    small: 'p-4',
    default: 'p-6',
    large: 'p-8'
  };
  
  const hoverClasses = hover ? 'card-hover cursor-pointer' : '';
  const clickableClasses = onClick ? 'cursor-pointer' : '';
  
  const classes = `
    ${baseClasses}
    ${variantClasses[variant] || variantClasses.default}
    ${paddingClasses[padding]}
    ${hoverClasses}
    ${clickableClasses}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  const CardComponent = onClick ? 'button' : 'div';

  return (
    <CardComponent
      className={classes}
      onClick={onClick}
      {...(onClick && { 
        role: 'button',
        tabIndex: 0,
        onKeyDown: (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onClick(e);
          }
        }
      })}
      {...props}
    >
      {children}
    </CardComponent>
  );
};

// Card sub-components for better composition
Card.Header = ({ children, className = '', ...props }) => (
  <div className={`mb-4 ${className}`} {...props}>
    {children}
  </div>
);

Card.Title = ({ children, className = '', ...props }) => (
  <h3 className={`text-heading-3 text-professional-800 ${className}`} {...props}>
    {children}
  </h3>
);

Card.Content = ({ children, className = '', ...props }) => (
  <div className={`text-body-main text-professional-700 ${className}`} {...props}>
    {children}
  </div>
);

Card.Footer = ({ children, className = '', ...props }) => (
  <div className={`mt-4 pt-4 border-t border-professional-200 ${className}`} {...props}>
    {children}
  </div>
);

export default Card;