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
      className={`relative overflow-hidden rounded-card-lg border border-border bg-surface p-5 text-center transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-card-elevated group ${className}`}
    >
      {/* Top subtle glow highlight line */}
      <div
        className={`absolute top-0 left-0 right-0 h-[2px] transition-opacity ${
          isDanger
            ? 'bg-gradient-to-r from-transparent via-danger/60 to-transparent'
            : 'bg-gradient-to-r from-transparent via-primary/60 to-transparent'
        }`}
      />

      <div className="flex items-center justify-center gap-1.5 mb-1.5">
        <div
          className={`w-6 h-6 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110 ${
            isDanger ? 'bg-danger/15 text-danger' : 'bg-primary/15 text-accent'
          }`}
        >
          {isDanger ? (
            <ShieldAlert className="w-3.5 h-3.5" />
          ) : (
            <ShieldCheck className="w-3.5 h-3.5" />
          )}
        </div>
        <span className="text-xs sm:text-sm font-semibold text-text-muted capitalize">
          {label}
        </span>
      </div>

      <div className="text-3xl sm:text-4xl font-black text-text tracking-tight">
        {value.toLocaleString()}
      </div>
    </div>
  );
};
