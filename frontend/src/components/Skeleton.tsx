import React from 'react';

export const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      className={`animate-pulse bg-surface-2/80 rounded-card border border-border/40 ${className}`}
      aria-hidden="true"
    />
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="flex items-center justify-between p-3.5 rounded-xl bg-surface border border-border/80 animate-pulse">
      <div className="flex items-center gap-3 w-3/4">
        <div className="w-9 h-9 rounded-lg bg-surface-2 shrink-0 border border-border/60" />
        <div className="space-y-1.5 flex-1">
          <div className="h-3.5 bg-surface-2 rounded w-5/6" />
          <div className="h-2.5 bg-surface-2 rounded w-1/3" />
        </div>
      </div>
      <div className="h-5 w-16 bg-surface-2 rounded-full" />
    </div>
  );
};
