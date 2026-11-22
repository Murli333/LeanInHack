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
          <div className="w-9 h-9 rounded-full bg-safe text-white flex items-center justify-center shrink-0 shadow-md shadow-safe/25 ring-2 ring-safe/30 transition-all duration-300">
            <Check className="w-5 h-5 stroke-[3]" />
          </div>
        );
      case 'running':
        return (
          <div className="w-9 h-9 rounded-full border-2 border-accent/40 bg-accent/10 flex items-center justify-center shrink-0 ring-4 ring-accent/20 animate-pulse transition-all duration-300">
            <Loader2 className="w-5 h-5 text-accent animate-spin" />
          </div>
        );
      case 'failed':
        return (
          <div className="w-9 h-9 rounded-full bg-danger text-white flex items-center justify-center shrink-0 shadow-md shadow-danger/25 ring-2 ring-danger/30 transition-all duration-300">
            <X className="w-5 h-5 stroke-[3]" />
          </div>
        );
      case 'waiting':
      default:
        return (
          <div className="w-9 h-9 rounded-full border-2 border-border/80 bg-surface-2 shrink-0 transition-all duration-300" />
        );
    }
  };

  const getStatusLabel = (status: StepStatus) => {
    switch (status) {
      case 'completed':
        return <span className="text-xs font-bold text-safe tracking-wide">Completed</span>;
      case 'running':
        return <span className="text-xs font-bold text-accent tracking-wide animate-pulse">In progress</span>;
      case 'failed':
        return <span className="text-xs font-bold text-danger tracking-wide">Failed</span>;
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
      {steps.map((step, index) => {
        const isLast = index === steps.length - 1;
        const isCompleted = step.status === 'completed';

        return (
          <div key={step.key || index} className="relative flex items-center gap-4" role="listitem">
            {/* Connecting line to next step */}
            {!isLast && (
              <div
                className={`absolute left-[17px] top-9 w-[2px] h-7 -mb-2 transition-colors duration-300 ${
                  isCompleted ? 'bg-safe/60' : 'bg-border/60'
                }`}
              />
            )}

            {getStepIcon(step.status)}
            <div className="flex-1 min-w-0">
              <div className="text-base font-bold text-text leading-tight">
                {step.label}
              </div>
              <div className="pt-0.5">{getStatusLabel(step.status)}</div>
              {step.detail && (
                <div className="text-xs text-text-muted mt-0.5 font-medium">{step.detail}</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
