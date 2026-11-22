import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useScan } from '../hooks/useScans';
import { ProgressStepper } from '../components/ProgressStepper';
import { ErrorState } from '../components/ErrorState';
import { Skeleton } from '../components/Skeleton';
import { Button } from '../components/Button';
import { AlertCircle, RotateCcw, ArrowRight, CheckCircle2 } from 'lucide-react';

export const ProgressPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: scan, isLoading, isError, error, refetch } = useScan(id || '', Boolean(id));

  const status = scan?.status;
  const isComplete = status === 'completed' || status === 'partial';

  // 1. Guaranteed active polling while the scan is running
  useEffect(() => {
    if (!id || isComplete || status === 'failed') return;

    // Actively poll every 400ms while running
    const pollTimer = setInterval(() => {
      refetch();
    }, 400);

    return () => clearInterval(pollTimer);
  }, [id, isComplete, status, refetch]);

  // 2. Smooth auto-navigation once completed
  useEffect(() => {
    if (!scan || !isComplete) return;

    // Redirect after brief visual confirmation (500ms)
    const timer = setTimeout(() => {
      navigate(`/report/${scan.id}`, { replace: true });
    }, 500);

    return () => clearTimeout(timer);
  }, [isComplete, scan?.id, navigate]);

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
    <div className="py-4 sm:py-8 max-w-md mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-1.5 text-left">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary dark:text-accent border border-primary/20 shadow-sm mb-1">
          <span className="w-2 h-2 rounded-full bg-accent animate-ping" />
          <span>Multimodal Threat Verification</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-text">
          {isComplete ? 'Analysis complete' : 'Analyzing your submission'}
        </h1>
        <p className="text-sm text-text-muted">
          {isComplete ? 'Verification finished. Preparing your security report...' : 'This may take a few moments.'}
        </p>
      </div>

      {/* Stepper Card */}
      <div className="p-6 sm:p-7 rounded-card-lg bg-surface border border-border shadow-card-elevated space-y-6">
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

        {/* Immediate navigation action when scan is completed */}
        {isComplete && scan && (
          <div className="pt-2 animate-in fade-in duration-300">
            <Button
              variant="primary"
              size="lg"
              fullWidth
              icon={<ArrowRight className="w-5 h-5" />}
              onClick={() => navigate(`/report/${scan.id}`, { replace: true })}
            >
              View Full Report
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
