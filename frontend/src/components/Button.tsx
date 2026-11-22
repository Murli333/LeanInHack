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
    'inline-flex items-center justify-center font-medium rounded-[9px] transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 active:scale-[0.99] disabled:opacity-40 disabled:pointer-events-none select-none cursor-pointer tracking-tight';

  const sizeStyles = {
    sm: 'text-xs px-3 py-1.5 min-h-[32px] gap-1.5',
    md: 'text-sm px-4 py-2 min-h-[38px] gap-2',
    lg: 'text-sm sm:text-base px-5 py-2.5 min-h-[42px] gap-2.5',
    huge: 'text-base px-6 py-3 min-h-[48px] gap-3',
  };

  const variantStyles = {
    primary:
      'bg-accent hover:bg-accent-hover text-white border border-accent/20 active:opacity-95 shadow-none',
    secondary:
      'bg-surface-raised hover:bg-surface text-text border border-border shadow-none',
    ghost:
      'bg-transparent text-text-secondary hover:text-text hover:bg-surface-raised border border-transparent',
    destructive:
      'bg-danger/10 hover:bg-danger/15 text-danger border border-danger/25 shadow-none',
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
