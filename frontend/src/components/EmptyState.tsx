import React from 'react';
import { Search, ShieldAlert, Sparkles } from 'lucide-react';
import { Button } from './Button';

export interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: 'search' | 'shield' | 'sparkles';
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  onAction,
  icon = 'shield',
  className = '',
}) => {
  const getIcon = () => {
    switch (icon) {
      case 'search':
        return <Search className="w-8 h-8 text-text-muted" />;
      case 'sparkles':
        return <Sparkles className="w-8 h-8 text-accent" />;
      case 'shield':
      default:
        return <ShieldAlert className="w-8 h-8 text-primary" />;
    }
  };

  return (
    <div
      className={`rounded-card-lg border border-dashed border-border bg-surface-2 p-8 text-center space-y-4 ${className}`}
    >
      <div className="w-16 h-16 rounded-2xl bg-surface border border-border flex items-center justify-center mx-auto shadow-sm">
        {getIcon()}
      </div>

      <div className="space-y-1.5 max-w-sm mx-auto">
        <h3 className="text-base sm:text-lg font-bold text-text">{title}</h3>
        <p className="text-xs sm:text-sm text-text-muted leading-relaxed">
          {description}
        </p>
      </div>

      {actionLabel && onAction && (
        <div className="pt-2">
          <Button variant="secondary" size="md" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
