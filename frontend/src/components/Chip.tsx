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
      className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-colors shrink-0 select-none min-h-[36px] border active:scale-[0.99] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-border ${
        selected
          ? 'bg-primary text-white border-primary/40 shadow-none'
          : 'bg-surface text-text-muted border-border/80 hover:text-text hover:bg-surface-2/60'
      } ${className}`}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{label}</span>
      {soon && (
        <span
          className={`ml-1 px-1.5 py-0.2 rounded text-[10px] uppercase font-mono tracking-wider ${
            selected
              ? 'bg-white/20 text-white'
              : 'bg-surface-2 text-text-muted'
          }`}
        >
          Soon
        </span>
      )}
    </button>
  );
};
