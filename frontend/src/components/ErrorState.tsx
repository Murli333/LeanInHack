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
      className={`rounded-xl border border-danger/25 bg-surface p-6 text-center space-y-3.5 ${className}`}
      role="alert"
    >
      <div className="w-10 h-10 rounded-xl bg-danger/10 text-danger flex items-center justify-center mx-auto border border-danger/20">
        <AlertTriangle className="w-5 h-5" />
      </div>

      <div className="space-y-1 max-w-sm mx-auto">
        <h3 className="text-sm font-medium text-text">{title}</h3>
        <p className="text-xs text-text-muted leading-relaxed">
          {message}
        </p>
      </div>

      {onRetry && (
        <div className="pt-1">
          <Button
            variant="secondary"
            size="sm"
            icon={<RefreshCw className="w-3.5 h-3.5" />}
            onClick={onRetry}
          >
            Try again
          </Button>
        </div>
      )}
    </div>
  );
};
