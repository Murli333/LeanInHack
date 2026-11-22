import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useScan } from '../hooks/useScans';
import { ProgressStepper } from '../components/ProgressStepper';
import { ErrorState } from '../components/ErrorState';
import { Skeleton } from '../components/Skeleton';
import { Button } from '../components/Button';
import { AlertCircle, RotateCcw, ArrowRight } from 'lucide-react';

export const ProgressPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: scan, isLoading, isError, error, refetch } = useScan(id || '', Boolean(id));

  const status = scan?.status;
  const isComplete = status === 'completed' || status === 'partial';

  // 1. Guaranteed active polling while the scan is running
  useEffect(() => {
    if (!id || isComplete || status === 'failed') return;

    // Actively poll every 350ms while running
    const pollTimer = setInterval(() => {
      refetch();
    }, 350);

    return () => clearInterval(pollTimer);
  }, [id, isComplete, status, refetch]);

  // 2. Smooth auto-navigation once completed
  useEffect(() => {
    if (!scan || !isComplete) return;

    // Redirect after brief visual confirmation (400ms)
    const timer = setTimeout(() => {
      navigate(`/report/${scan.id}`, { replace: true });
    }, 400);

    return () => clearTimeout(timer);
  }, [isComplete, scan?.id, navigate]);

  // Terminal state: Analysis failed
  if (status === 'failed') {
    return (
      <div className="py-8 max-w-md mx-auto space-y-5">
        <div className="p-6 rounded-card bg-surface border border-danger/30 text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-danger/10 text-danger flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h2 className="text-lg font-medium text-text">Scan Processing Interrupted</h2>
            <p className="text-xs text-text-secondary leading-relaxed">
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
              Start new verification
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

  const defaultRunningSteps = [
    { key: 'extract', label: 'Extract content', status: 'completed' as const },
    { key: 'patterns', label: 'Check patterns', status: 'running' as const },
    { key: 'reputation', label: 'Check URL reputation', status: 'waiting' as const },
    { key: 'evidence', label: 'Combine evidence', status: 'waiting' as const },
    { key: 'report', label: 'Prepare report', status: 'waiting' as const },
  ];

  const defaultCompletedSteps = [
    { key: 'extract', label: 'Extract content', status: 'completed' as const },
    { key: 'patterns', label: 'Check patterns', status: 'completed' as const },
    { key: 'reputation', label: 'Check URL reputation', status: 'completed' as const },
    { key: 'evidence', label: 'Combine evidence', status: 'completed' as const },
    { key: 'report', label: 'Prepare report', status: 'completed' as const },
  ];

  const steps = isComplete
    ? (scan?.steps && scan.steps.length > 0 ? scan.steps.map(s => ({ ...s, status: 'completed' as const })) : defaultCompletedSteps)
    : (scan?.steps && scan.steps.length > 0 ? scan.steps : defaultRunningSteps);

  return (
    <div className="py-4 sm:py-8 max-w-md mx-auto space-y-6">
      {/* Header */}
      <div className="space-y-1 text-left">
        <div className="inline-flex items-center gap-2 text-xs font-medium text-text-muted mb-1">
          <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
          <span className="font-mono text-2xs uppercase tracking-wider text-accent">Analysis Pipeline</span>
        </div>
        <h1 className="text-2xl font-medium tracking-tight text-text">
          {isComplete ? 'Verification complete' : 'Evaluating submission'}
        </h1>
        <p className="text-xs sm:text-sm text-text-secondary">
          {isComplete ? 'All checks completed. Preparing report...' : 'Verifying content across reputation and pattern models.'}
        </p>
      </div>

      {/* Stepper Card */}
      <div className="p-5 sm:p-6 rounded-card bg-surface border border-border space-y-5">
        {isLoading && !scan ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        ) : (
          <ProgressStepper steps={steps} />
        )}

        {/* Immediate navigation action when scan is completed */}
        {isComplete && scan && (
          <div className="pt-2 animate-fade-in">
            <Button
              variant="primary"
              size="md"
              fullWidth
              icon={<ArrowRight className="w-4 h-4" />}
              onClick={() => navigate(`/report/${scan.id}`, { replace: true })}
            >
              View Report
            </Button>
          </div>
        )}
      </div>

      {!isComplete && (
        <p className="text-center text-xs text-text-muted">
          Evaluating across calibrated models, URL structure, and fraud signals...
        </p>
      )}
    </div>
  );
};
