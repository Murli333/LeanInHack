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
        return <Search className="w-4 h-4 text-text-muted" />;
      case 'sparkles':
        return <Sparkles className="w-4 h-4 text-accent" />;
      case 'shield':
      default:
        return <ShieldAlert className="w-4 h-4 text-text-muted" />;
    }
  };

  return (
    <div
      className={`rounded-card border border-border bg-surface p-7 text-center space-y-3.5 ${className}`}
    >
      <div className="w-9 h-9 rounded-button bg-surface-raised border border-border flex items-center justify-center mx-auto">
        {getIcon()}
      </div>

      <div className="space-y-1 max-w-sm mx-auto">
        <h3 className="text-xs font-medium text-text">{title}</h3>
        <p className="text-2xs text-text-muted leading-relaxed">
          {description}
        </p>
      </div>

      {actionLabel && onAction && (
        <div className="pt-1">
          <Button
            variant="primary"
            size="sm"
            onClick={onAction}
          >
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
