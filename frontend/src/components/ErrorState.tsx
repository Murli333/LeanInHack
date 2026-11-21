import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message = 'We encountered an error loading this information. Please check your connection and try again.',
  onRetry,
  className = '',
}) => {
  return (
    <div
      className={`rounded-card-lg border border-danger/30 bg-surface-2 p-8 text-center space-y-4 ${className}`}
      role="alert"
    >
      <div className="w-16 h-16 rounded-full bg-danger-tint text-danger flex items-center justify-center mx-auto border border-danger/20">
        <AlertTriangle className="w-8 h-8" />
      </div>

      <div className="space-y-1.5 max-w-sm mx-auto">
        <h3 className="text-base sm:text-lg font-bold text-text">{title}</h3>
        <p className="text-xs sm:text-sm text-text-muted leading-relaxed">
          {message}
        </p>
      </div>

      {onRetry && (
        <div className="pt-2">
          <Button
            variant="secondary"
            size="md"
            icon={<RefreshCw className="w-4 h-4" />}
            onClick={onRetry}
          >
            Try again
          </Button>
        </div>
      )}
    </div>
  );
};
