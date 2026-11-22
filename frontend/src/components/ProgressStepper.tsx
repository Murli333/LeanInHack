import React from 'react';
import { Check, X, Loader2 } from 'lucide-react';
import { ScanStep, StepStatus } from '../types';

export interface ProgressStepperProps {
  steps: ScanStep[];
  className?: string;
}

export const ProgressStepper: React.FC<ProgressStepperProps> = ({
  steps,
  className = '',
}) => {
  const getStepIcon = (status: StepStatus) => {
    switch (status) {
      case 'completed':
        return (
          <div className="w-6 h-6 rounded-full bg-safe/10 text-safe border border-safe/25 flex items-center justify-center shrink-0">
            <Check className="w-3.5 h-3.5" />
          </div>
        );
      case 'running':
        return (
          <div className="w-6 h-6 rounded-full bg-accent/15 text-accent border border-accent/40 flex items-center justify-center shrink-0">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          </div>
        );
      case 'failed':
        return (
          <div className="w-6 h-6 rounded-full bg-danger/10 text-danger border border-danger/30 flex items-center justify-center shrink-0">
            <X className="w-3.5 h-3.5" />
          </div>
        );
      case 'waiting':
      default:
        return (
          <div className="w-6 h-6 rounded-full border border-border bg-surface-raised shrink-0" />
        );
    }
  };

  const getStatusLabel = (status: StepStatus) => {
    switch (status) {
      case 'completed':
        return <span className="text-xs text-safe font-mono">Done</span>;
      case 'running':
        return <span className="text-xs text-accent font-mono">In progress</span>;
      case 'failed':
        return <span className="text-xs text-danger font-mono">Failed</span>;
      case 'waiting':
      default:
        return <span className="text-xs text-text-muted font-mono">Waiting</span>;
    }
  };

  return (
    <div
      className={`space-y-4 ${className}`}
      role="list"
      aria-label="Analysis progress steps"
      aria-live="polite"
    >
      {steps.map((step, index) => {
        const isLast = index === steps.length - 1;
        const isCompleted = step.status === 'completed';

        return (
          <div key={step.key || index} className="relative flex items-center gap-3.5" role="listitem">
            {/* Connecting line to next step */}
            {!isLast && (
              <div
                className={`absolute left-[11px] top-6 w-[1px] h-5 transition-colors duration-150 ${
                  isCompleted ? 'bg-safe/30' : 'bg-border'
                }`}
              />
            )}

            {getStepIcon(step.status)}
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-text leading-tight">
                {step.label}
              </div>
              <div className="pt-0.5">{getStatusLabel(step.status)}</div>
              {step.detail && (
                <div className="text-xs text-text-muted mt-0.5">{step.detail}</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
