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
          <div className="w-8 h-8 rounded-full bg-safe text-on-primary flex items-center justify-center shrink-0 shadow-sm">
            <Check className="w-5 h-5 stroke-[3]" />
          </div>
        );
      case 'running':
        return (
          <div className="w-8 h-8 rounded-full border-2 border-accent/30 border-t-accent flex items-center justify-center shrink-0">
            <Loader2 className="w-5 h-5 text-accent animate-spin" />
          </div>
        );
      case 'failed':
        return (
          <div className="w-8 h-8 rounded-full bg-danger text-white flex items-center justify-center shrink-0 shadow-sm">
            <X className="w-5 h-5 stroke-[3]" />
          </div>
        );
      case 'waiting':
      default:
        return (
          <div className="w-8 h-8 rounded-full border-2 border-border bg-surface-2 shrink-0" />
        );
    }
  };

  const getStatusLabel = (status: StepStatus) => {
    switch (status) {
      case 'completed':
        return <span className="text-xs font-medium text-safe">Completed</span>;
      case 'running':
        return <span className="text-xs font-medium text-accent">In progress</span>;
      case 'failed':
        return <span className="text-xs font-medium text-danger">Failed</span>;
      case 'waiting':
      default:
        return <span className="text-xs font-medium text-text-muted">Waiting</span>;
    }
  };

  return (
    <div
      className={`space-y-6 ${className}`}
      role="list"
      aria-label="Analysis progress steps"
      aria-live="polite"
    >
      {steps.map((step, index) => (
        <div key={step.key || index} className="flex items-center gap-4" role="listitem">
          {getStepIcon(step.status)}
          <div className="flex-1 min-w-0">
            <div className="text-base font-semibold text-text leading-tight">
              {step.label}
            </div>
            <div className="pt-0.5">{getStatusLabel(step.status)}</div>
            {step.detail && (
              <div className="text-xs text-text-muted mt-0.5">{step.detail}</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
