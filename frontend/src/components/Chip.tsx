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
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all duration-200 shrink-0 select-none min-h-[42px] border active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
        selected
          ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white border-blue-400/30 shadow-md shadow-blue-500/25'
          : 'bg-surface text-text-muted border-border hover:text-text hover:border-primary/30 hover:bg-surface-2'
      } ${className}`}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{label}</span>
      {soon && (
        <span
          className={`ml-1 px-1.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${
            selected
              ? 'bg-white/25 text-white'
              : 'bg-surface-2 text-text-muted border border-border'
          }`}
        >
          Soon
        </span>
      )}
    </button>
  );
};
