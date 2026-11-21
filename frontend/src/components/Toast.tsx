import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export interface ToastProps {
  id: string;
  type?: 'success' | 'error' | 'info';
  message: string;
  onClose: (id: string) => void;
  duration?: number;
}

export const Toast: React.FC<ToastProps> = ({
  id,
  type = 'info',
  message,
  onClose,
  duration = 4000,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => onClose(id), duration);
    return () => clearTimeout(timer);
  }, [id, duration, onClose]);

  const icons = {
    success: <CheckCircle2 className="w-4 h-4 text-safe shrink-0" />,
    error: <AlertCircle className="w-4 h-4 text-danger shrink-0" />,
    info: <Info className="w-4 h-4 text-accent shrink-0" />,
  };

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-2.5 px-4 py-2.5 rounded-full bg-surface border border-border shadow-lg text-xs sm:text-sm text-text transition-all"
    >
      {icons[type]}
      <span className="font-medium">{message}</span>
      <button
        onClick={() => onClose(id)}
        className="ml-1 text-text-muted hover:text-text p-0.5 rounded-full transition-colors"
        aria-label="Dismiss toast"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
