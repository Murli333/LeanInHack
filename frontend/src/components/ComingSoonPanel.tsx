import React from 'react';
import { Clock, Shield } from 'lucide-react';

export interface ComingSoonPanelProps {
  title: string;
  description: string;
  featureName: string;
  className?: string;
}

export const ComingSoonPanel: React.FC<ComingSoonPanelProps> = ({
  title,
  description,
  featureName,
  className = '',
}) => {
  return (
    <div
      className={`rounded-card-lg border border-dashed border-border bg-surface-2 p-8 text-center space-y-4 ${className}`}
    >
      <div className="w-12 h-12 rounded-full bg-surface border border-border text-text-muted flex items-center justify-center mx-auto">
        <Clock className="w-6 h-6 text-accent" />
      </div>

      <div className="space-y-1">
        <h3 className="text-base sm:text-lg font-bold text-text">{title}</h3>
        <p className="text-sm text-text-muted max-w-sm mx-auto leading-relaxed">
          {description}
        </p>
      </div>

      <div className="pt-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-surface border border-border text-text-muted">
          <Shield className="w-3.5 h-3.5 text-primary" />
          <span>{featureName} is currently in validation &bull; Coming soon</span>
        </div>
      </div>
    </div>
  );
};
