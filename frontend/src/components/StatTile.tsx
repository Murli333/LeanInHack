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
      className={`rounded-card border border-border bg-surface p-4 sm:p-5 transition-colors hover:bg-surface-raised text-left ${className}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-mono text-text-muted capitalize">
          {label}
        </span>
        <div
          className={`w-6 h-6 rounded-[6px] flex items-center justify-center ${
            isDanger ? 'bg-danger/10 text-danger border border-danger/20' : 'bg-surface-raised text-accent border border-border'
          }`}
        >
          {isDanger ? (
            <ShieldAlert className="w-3.5 h-3.5" />
          ) : (
            <ShieldCheck className="w-3.5 h-3.5" />
          )}
        </div>
      </div>

      <div className="text-2xl sm:text-3xl font-medium font-mono text-text tracking-tight">
        {value.toLocaleString()}
      </div>
    </div>
  );
};
