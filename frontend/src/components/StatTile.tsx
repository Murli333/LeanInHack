import React from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

export interface StatTileProps {
  value: number;
  label: string;
  className?: string;
}

export const StatTile: React.FC<StatTileProps> = ({ value, label, className = '' }) => {
  const isDanger = label.toLowerCase().includes('high-risk') || label.toLowerCase().includes('scam');

  return (
    <div
      className={`rounded-xl border border-border/80 bg-surface p-4 sm:p-5 transition-colors hover:border-border text-left ${className}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-text-muted capitalize">
          {label}
        </span>
        <div
          className={`w-6 h-6 rounded-md flex items-center justify-center ${
            isDanger ? 'bg-danger/10 text-danger' : 'bg-primary/10 text-primary'
          }`}
        >
          {isDanger ? (
            <ShieldAlert className="w-3.5 h-3.5" />
          ) : (
            <ShieldCheck className="w-3.5 h-3.5" />
          )}
        </div>
      </div>

      <div className="text-2xl sm:text-3xl font-semibold text-text tracking-tight">
        {value.toLocaleString()}
      </div>
    </div>
  );
};
