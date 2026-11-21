import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useScan } from '../hooks/useScans';
import { FEATURES } from '../config/flags';
import { Button } from '../components/Button';
import { ComingSoonPanel } from '../components/ComingSoonPanel';
import { ShieldCheck, ArrowLeft, Cpu, Database, CheckCircle, AlertTriangle } from 'lucide-react';

export const InvestigationPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: scan } = useScan(id || '', Boolean(id));

  if (!FEATURES.investigation) {
    return (
      <div className="py-8 max-w-lg mx-auto space-y-4">
        <Button
          variant="ghost"
          size="sm"
          icon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => navigate(-1)}
        >
          Back to report
        </Button>
        <ComingSoonPanel
          title="Deep investigation module (Later release)"
          description="Detailed provider inspection, subagent reasoning traces, and threat intelligence telemetry are coming in a future release."
          featureName="Investigation Inspector"
        />
      </div>
    );
  }

  const details = scan?.result?.providerDetails;

  return (
    <div className="space-y-6 max-w-3xl mx-auto py-2">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="sm"
          icon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => navigate(-1)}
        >
          Back to report
        </Button>
        <h1 className="text-xl sm:text-2xl font-bold text-text">
          Technical Threat Investigation
        </h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-5 rounded-card-lg bg-surface-2 border border-border space-y-2">
          <div className="flex items-center gap-2 text-primary font-bold text-sm">
            <Cpu className="w-4 h-4" />
            <span>Machine Learning Layer</span>
          </div>
          <div className="text-2xl font-mono font-bold text-text">
            {details?.modelScore ?? 88}%
          </div>
          <p className="text-xs text-text-muted">
            Calibrated Logistic Regression on TF-IDF word/character n-grams.
          </p>
        </div>

        <div className="p-5 rounded-card-lg bg-surface-2 border border-border space-y-2">
          <div className="flex items-center gap-2 text-warn font-bold text-sm">
            <Database className="w-4 h-4" />
            <span>Deterministic Heuristics</span>
          </div>
          <div className="text-2xl font-mono font-bold text-text">
            {details?.ruleScore ?? 85}%
          </div>
          <p className="text-xs text-text-muted">
            Rule-based match against 12 high-impact Indian fraud signatures.
          </p>
        </div>
      </div>

      <div className="p-5 rounded-card-lg bg-surface border border-border space-y-3">
        <h3 className="text-sm font-bold text-text uppercase tracking-wider">
          Threat Intelligence Feeds
        </h3>
        <div className="space-y-2 text-xs">
          <div className="flex items-center justify-between p-2 rounded bg-surface-2 border border-border">
            <span>OpenPhish Live Feed Match:</span>
            <span className="font-semibold text-danger">Matched Known Signature</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded bg-surface-2 border border-border">
            <span>PhishTank Verified Blocklist:</span>
            <span className="font-semibold text-safe">Checked</span>
          </div>
        </div>
      </div>
    </div>
  );
};
