import React from 'react';

export interface ChipProps {
  label: string;
  selected?: boolean;
  soon?: boolean;
  icon?: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export const Chip: React.FC<ChipProps> = ({
  label,
  selected = false,
  soon = false,
  icon,
  onClick,
  className = '',
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-xs sm:text-sm font-medium transition-all shrink-0 select-none min-h-[40px] border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
        selected
          ? 'bg-primary text-on-primary border-primary shadow-sm'
          : 'bg-surface-2 text-text border-border hover:bg-surface hover:border-text-muted/30'
      } ${className}`}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{label}</span>
      {soon && (
        <span
          className={`ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold uppercase tracking-wider ${
            selected
              ? 'bg-white/20 text-white'
              : 'bg-border text-text-muted'
          }`}
        >
          Soon
        </span>
      )}
    </button>
  );
};
