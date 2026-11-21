import React from 'react';

export interface StatTileProps {
  value: number;
  label: string;
  className?: string;
}

export const StatTile: React.FC<StatTileProps> = ({ value, label, className = '' }) => {
  return (
    <div
      className={`rounded-card-lg border border-border bg-surface-2 p-5 text-center transition-all hover:border-text-muted/30 ${className}`}
    >
      <div className="text-3xl sm:text-4xl font-extrabold text-text tracking-tight font-mono">
        {value.toLocaleString()}
      </div>
      <div className="text-xs sm:text-sm text-text-muted font-medium mt-1">
        {label}
      </div>
    </div>
  );
};
