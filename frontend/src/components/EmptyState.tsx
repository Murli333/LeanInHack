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
        return <Search className="w-5 h-5 text-text-muted" />;
      case 'sparkles':
        return <Sparkles className="w-5 h-5 text-primary" />;
      case 'shield':
      default:
        return <ShieldAlert className="w-5 h-5 text-text-muted" />;
    }
  };

  return (
    <div
      className={`rounded-xl border border-border/80 bg-surface p-7 text-center space-y-3.5 ${className}`}
    >
      <div className="w-10 h-10 rounded-xl bg-surface-2 border border-border/80 flex items-center justify-center mx-auto">
        {getIcon()}
      </div>

      <div className="space-y-1 max-w-sm mx-auto">
        <h3 className="text-sm font-medium text-text">{title}</h3>
        <p className="text-xs text-text-muted leading-relaxed">
          {description}
        </p>
      </div>

      {actionLabel && onAction && (
        <div className="pt-1">
          <Button variant="secondary" size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
