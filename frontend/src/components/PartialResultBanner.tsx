import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export interface PartialResultBannerProps {
  message?: string;
  onRetry?: () => void;
  isRetrying?: boolean;
  className?: string;
}

export const PartialResultBanner: React.FC<PartialResultBannerProps> = ({
  message = 'Some external safety checks could not complete due to network connectivity.',
  onRetry,
  isRetrying = false,
  className = '',
}) => {
  return (
    <div
      className={`rounded-card-lg border border-warn/40 bg-warn-tint p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${className}`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-warn shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-bold text-text">Incomplete verification</h4>
          <p className="text-xs text-text-muted mt-0.5 leading-relaxed">
            {message}
          </p>
        </div>
      </div>

      {onRetry && (
        <Button
          variant="secondary"
          size="sm"
          icon={<RefreshCw className={`w-3.5 h-3.5 ${isRetrying ? 'animate-spin' : ''}`} />}
          onClick={onRetry}
          disabled={isRetrying}
          className="shrink-0 self-end sm:self-center"
        >
          {isRetrying ? 'Checking...' : 'Retry check'}
        </Button>
      )}
    </div>
  );
};
