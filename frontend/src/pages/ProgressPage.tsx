import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useScan } from '../hooks/useScans';
import { ProgressStepper } from '../components/ProgressStepper';
import { ErrorState } from '../components/ErrorState';
import { Skeleton } from '../components/Skeleton';

export const ProgressPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: scan, isLoading, isError, refetch } = useScan(id || '', Boolean(id));

  // When scan completes or reports a partial result, redirect to report screen
  useEffect(() => {
    if (scan && (scan.status === 'completed' || scan.status === 'partial')) {
      const timer = setTimeout(() => {
        navigate(`/report/${scan.id}`, { replace: true });
      }, 600);
      return () => clearTimeout(timer);
    }
  }, [scan, navigate]);

  if (isError) {
    return (
      <div className="py-8 max-w-lg mx-auto">
        <ErrorState
          title="Analysis interrupted"
          message="We could not complete verification for this scan ID."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const defaultSteps = [
    { key: 'extract', label: 'Extract content', status: 'completed' as const },
    { key: 'patterns', label: 'Check patterns', status: 'running' as const },
    { key: 'reputation', label: 'Check URL reputation', status: 'waiting' as const },
    { key: 'evidence', label: 'Combine evidence', status: 'waiting' as const },
    { key: 'report', label: 'Prepare report', status: 'waiting' as const },
  ];

  const steps = scan?.steps || defaultSteps;

  return (
    <div className="py-4 sm:py-8 max-w-md mx-auto space-y-8">
      {/* Reference Header */}
      <div className="space-y-1.5 text-left">
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-text">
          Analyzing your submission
        </h1>
        <p className="text-sm text-text-muted">
          This may take a few moments.
        </p>
      </div>

      {/* Stepper Card */}
      <div className="p-6 rounded-card-lg bg-surface border border-border shadow-card-soft">
        {isLoading && !scan ? (
          <div className="space-y-6">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : (
          <ProgressStepper steps={steps} />
        )}
      </div>

      <p className="text-center text-xs text-text-muted">
        Evaluating across calibrated models, URL structure, and fraud signals...
      </p>
    </div>
  );
};
