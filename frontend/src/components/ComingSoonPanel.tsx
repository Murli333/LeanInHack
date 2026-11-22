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
      className={`rounded-card border border-dashed border-border bg-surface-raised p-8 text-center space-y-4 ${className}`}
    >
      <div className="w-10 h-10 rounded-button bg-surface border border-border text-text-muted flex items-center justify-center mx-auto">
        <Clock className="w-5 h-5 text-text-muted" />
      </div>

      <div className="space-y-1">
        <h3 className="text-sm font-medium text-text">{title}</h3>
        <p className="text-xs text-text-secondary max-w-sm mx-auto leading-relaxed">
          {description}
        </p>
      </div>

      <div className="pt-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-button text-xs font-mono bg-surface border border-border text-text-muted">
          <Shield className="w-3 h-3 text-accent" />
          <span>{featureName} is currently in validation &bull; Coming soon</span>
        </div>
      </div>
    </div>
  );
};
