import React, { useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useScan } from '../hooks/useScans';
import { ProgressStepper } from '../components/ProgressStepper';
import { ErrorState } from '../components/ErrorState';
import { Skeleton } from '../components/Skeleton';
import { Button } from '../components/Button';
import { AlertCircle, RotateCcw } from 'lucide-react';

export const ProgressPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const navigatedRef = useRef(false);

  const { data: scan, isLoading, isError, error, refetch } = useScan(id || '', Boolean(id));

  const status = scan?.status;

  // Terminal state transition: Once completed or partial, navigate directly to report
  useEffect(() => {
    if (!scan || navigatedRef.current) return;

    if (status === 'completed' || status === 'partial') {
      navigatedRef.current = true;
      const timer = setTimeout(() => {
        navigate(`/report/${scan.id}`, { replace: true });
      }, 400);
      return () => clearTimeout(timer);
    }
  }, [status, scan?.id, navigate]);

  // Terminal state: Analysis failed
  if (status === 'failed') {
    return (
      <div className="py-8 max-w-md mx-auto space-y-5">
        <div className="p-6 rounded-card-lg bg-surface border border-danger/40 text-center space-y-4 shadow-card-soft">
          <div className="w-14 h-14 rounded-full bg-danger-tint text-danger flex items-center justify-center mx-auto">
            <AlertCircle className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-text">Scan Processing Failed</h2>
            <p className="text-sm text-text-muted leading-relaxed">
              {scan?.error || 'An unexpected error occurred during threat verification. Please check the content and try again.'}
            </p>
          </div>
          <div className="pt-2 flex flex-col gap-2">
            <Button
              variant="primary"
              size="md"
              fullWidth
              icon={<RotateCcw className="w-4 h-4" />}
              onClick={() => navigate('/scan')}
            >
              Start a new scan
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="py-8 max-w-lg mx-auto">
        <ErrorState
          title="Analysis interrupted"
          message={error instanceof Error ? error.message : 'We could not complete verification for this scan ID.'}
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

  const steps = scan?.steps && scan.steps.length > 0 ? scan.steps : defaultSteps;

  return (
    <div className="py-4 sm:py-8 max-w-md mx-auto space-y-8">
      {/* Header */}
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
