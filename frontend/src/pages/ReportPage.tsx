import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useScan, useRetryStep } from '../hooks/useScans';
import { RiskVerdictCard } from '../components/RiskVerdictCard';
import { EvidenceRow } from '../components/EvidenceRow';
import { ActionList } from '../components/ActionList';
import { Button } from '../components/Button';
import { PartialResultBanner } from '../components/PartialResultBanner';
import { ErrorState } from '../components/ErrorState';
import { Skeleton } from '../components/Skeleton';
import { FEATURES } from '../config/flags';
import {
  RotateCcw,
  SlidersHorizontal,
  Share2,
  Shield,
  Eye,
  EyeOff,
  Copy,
  Check,
} from 'lucide-react';

export const ReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [defang, setDefang] = useState(true);
  const [copied, setCopied] = useState(false);

  const { data: scan, isLoading, isError, refetch } = useScan(id || '', Boolean(id));
  const retryStepMutation = useRetryStep();

  // If scan is still running, route to progress stepper
  if (scan && (scan.status === 'running' || scan.status === 'queued')) {
    navigate(`/scan/${scan.id}/progress`, { replace: true });
    return null;
  }

  if (isLoading) {
    return (
      <div className="py-6 space-y-6 max-w-4xl mx-auto">
        <Skeleton className="h-64 w-full rounded-card-lg" />
        <Skeleton className="h-48 w-full rounded-card-lg" />
      </div>
    );
  }

  if (scan && scan.status === 'failed') {
    return (
      <div className="py-8 max-w-lg mx-auto">
        <ErrorState
          title="Analysis Failed"
          message={scan.error || "The scan encountered an unexpected processing error."}
          onRetry={() => navigate('/scan')}
        />
      </div>
    );
  }

  if (isError || !scan || !scan.result) {
    return (
      <div className="py-8 max-w-lg mx-auto">
        <ErrorState
          title="Report not found"
          message="We could not find the report for this scan ID."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const { result } = scan;

  // Defang submitted content if it is a link or contains links
  const getDisplayContent = (raw: string) => {
    if (!defang) return raw;
    return raw
      .replace(/https:\/\//gi, 'hxxps://')
      .replace(/http:\/\//gi, 'hxxp://')
      .replace(/\./g, '[.]');
  };

  const handleCopyReport = async () => {
    try {
      const textToShare = `ScamLens Report:\nVerdict: ${result.riskLevel.toUpperCase()}\nSummary: ${
        result.summary
      }\nVerified via ScamLens Digital Safety.`;
      await navigator.clipboard.writeText(textToShare);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // ignore
    }
  };

  const handleRetryFailedStep = () => {
    const failedStep = scan.steps.find((s) => s.status === 'failed');
    if (failedStep) {
      retryStepMutation.mutate({ id: scan.id, stepKey: failedStep.key });
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto py-2">
      {/* Partial result banner if any step was incomplete */}
      {result.isPartial && (
        <PartialResultBanner
          message="External reputation feed lookup was incomplete. Results reflect local pattern checks only."
          onRetry={handleRetryFailedStep}
          isRetrying={retryStepMutation.isPending}
        />
      )}

      {/* Desktop Two-Column Grid (>=1024px) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Verdict Card & Why it was flagged */}
        <div className="lg:col-span-7 space-y-6">
          {/* Reference Verdict Card */}
          <RiskVerdictCard
            level={result.riskLevel}
            summary={result.summary}
            score={result.score}
            scoreValidated={result.scoreValidated}
            category={result.category}
          />

          {/* Reference Card: "Why it was flagged" */}
          <div className="p-5 rounded-card-lg bg-surface border border-border space-y-4 shadow-card-soft">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-text">
                Why it was flagged
              </h3>
              <span className="text-xs text-text-muted">
                {result.evidence.length} evidence indicators
              </span>
            </div>

            <div className="space-y-3">
              {result.evidence.map((ev) => (
                <EvidenceRow key={ev.id} evidence={ev} />
              ))}
            </div>
          </div>

          {/* Submitted content preview (Defanged & Plaintext for security) */}
          <div className="p-4 rounded-card-lg bg-surface-2 border border-border space-y-2">
            <div className="flex items-center justify-between text-xs text-text-muted">
              <span className="font-semibold uppercase tracking-wider">
                Submitted Content
              </span>
              <button
                type="button"
                onClick={() => setDefang(!defang)}
                className="inline-flex items-center gap-1 text-primary hover:underline font-medium"
              >
                {defang ? (
                  <>
                    <Eye className="w-3.5 h-3.5" />
                    <span>Show original</span>
                  </>
                ) : (
                  <>
                    <EyeOff className="w-3.5 h-3.5" />
                    <span>Defang links</span>
                  </>
                )}
              </button>
            </div>
            <div className="p-3 rounded-card bg-surface border border-border text-xs sm:text-sm font-mono text-text break-words select-all">
              {getDisplayContent(scan.content)}
            </div>
            <p className="text-[11px] text-text-muted">
              Rendered as plain text. ScamLens never executes code or navigates to external links.
            </p>
          </div>
        </div>

        {/* Right Column: "Stay safe" Actions & Buttons */}
        <div className="lg:col-span-5 space-y-5">
          {/* Reference Card: "Stay safe" */}
          <ActionList actions={result.actions} />

          {/* Bottom Actions */}
          <div className="space-y-3 pt-1">
            <Button
              variant="primary"
              size="lg"
              fullWidth
              icon={<RotateCcw className="w-5 h-5" />}
              onClick={() => navigate('/scan')}
              className="shadow-md shadow-primary/20"
            >
              Check another
            </Button>

            {/* Later Release screen behind FEATURES.investigation flag */}
            {FEATURES.investigation ? (
              <Button
                variant="secondary"
                size="md"
                fullWidth
                icon={<SlidersHorizontal className="w-4 h-4" />}
                onClick={() => navigate(`/report/${scan.id}/investigation`)}
              >
                View Deep Investigation
              </Button>
            ) : (
              <div className="flex items-center justify-center gap-2 pt-1">
                <Button
                  variant="ghost"
                  size="sm"
                  icon={copied ? <Check className="w-4 h-4 text-safe" /> : <Copy className="w-4 h-4" />}
                  onClick={handleCopyReport}
                >
                  {copied ? 'Copied summary' : 'Copy summary'}
                </Button>
              </div>
            )}
          </div>

          <div className="text-center pt-2">
            <p className="text-[11px] text-text-muted">
              Accuracy figures are reported internally and not independently verified. Always exercise judgment.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
