import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg' | 'huge';
  fullWidth?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  icon,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none disabled:active:scale-100 select-none cursor-pointer tracking-tight';

  const sizeStyles = {
    sm: 'text-xs px-3 py-1.5 min-h-[34px] gap-1.5',
    md: 'text-sm px-4 py-2 min-h-[40px] gap-2',
    lg: 'text-sm sm:text-base px-5 py-2.5 min-h-[44px] gap-2.5 font-medium',
    huge: 'text-base px-6 py-3.5 min-h-[50px] gap-3 font-medium',
  };

  const variantStyles = {
    primary:
      'bg-primary hover:bg-blue-600 text-white border border-primary/30 shadow-sm active:bg-blue-700',
    secondary:
      'bg-surface hover:bg-surface-2 text-text border border-border/80 shadow-none',
    ghost: 'bg-transparent text-text-muted hover:text-text hover:bg-surface-2 border border-transparent',
    destructive:
      'bg-danger text-white hover:bg-rose-600 border border-danger/30 shadow-sm',
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${
        fullWidth ? 'w-full' : ''
      } ${className}`}
      disabled={disabled}
      {...props}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{children}</span>
    </button>
  );
};
