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
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-button text-xs font-medium transition-colors shrink-0 select-none border ${
        selected
          ? 'bg-accent text-white border-accent'
          : 'bg-surface text-text-secondary border-border hover:text-text hover:bg-surface-raised'
      } ${className}`}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{label}</span>
      {soon && (
        <span
          className={`ml-1 px-1.5 py-0.5 rounded text-[10px] font-mono tracking-wider ${
            selected
              ? 'bg-white/20 text-white'
              : 'bg-surface-raised text-text-muted'
          }`}
        >
          SOON
        </span>
      )}
    </button>
  );
};
