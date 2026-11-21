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
    <div className="flex items-center justify-between p-4 rounded-card-lg bg-surface-2 border border-border animate-pulse">
      <div className="flex items-center gap-3 w-3/4">
        <div className="w-11 h-11 rounded-2xl bg-border/60 shrink-0" />
        <div className="space-y-2 flex-1">
          <div className="h-4 bg-border/60 rounded w-5/6" />
          <div className="h-3 bg-border/40 rounded w-1/3" />
        </div>
      </div>
      <div className="h-6 w-20 bg-border/60 rounded-full" />
    </div>
  );
};
