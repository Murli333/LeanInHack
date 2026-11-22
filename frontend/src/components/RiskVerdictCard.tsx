import React from 'react';
import { ShieldAlert, AlertTriangle, Check, HelpCircle } from 'lucide-react';
import { RiskLevel } from '../types';
import { RiskMeter } from './RiskMeter';

export interface RiskVerdictCardProps {
  level: RiskLevel;
  summary: string;
  score?: number;
  scoreValidated?: boolean;
  category?: string;
  className?: string;
}

export const RiskVerdictCard: React.FC<RiskVerdictCardProps> = ({
  level,
  summary,
  score,
  scoreValidated = false,
  category,
  className = '',
}) => {
  const isHigh = level === 'high';
  const isMedium = level === 'medium';
  const isLow = level === 'low';
  const isUnknown = level === 'unknown';

  const configs: Record<
    RiskLevel,
    {
      title: string;
      icon: React.ReactNode;
      border: string;
      iconBg: string;
      iconColor: string;
    }
  > = {
    high: {
      title: 'High Risk Detected',
      icon: <ShieldAlert className="w-5 h-5" />,
      border: 'border-danger/20',
      iconBg: 'bg-danger/10 border border-danger/20',
      iconColor: 'text-danger',
    },
    medium: {
      title: 'Suspicious Indicators Found',
      icon: <AlertTriangle className="w-5 h-5" />,
      border: 'border-warn/20',
      iconBg: 'bg-warn/10 border border-warn/20',
      iconColor: 'text-warn',
    },
    low: {
      title: 'No Threats Detected',
      icon: <Check className="w-5 h-5" />,
      border: 'border-safe/20',
      iconBg: 'bg-safe/10 border border-safe/20',
      iconColor: 'text-safe',
    },
    unknown: {
      title: 'Inconclusive Result',
      icon: <HelpCircle className="w-5 h-5" />,
      border: 'border-border',
      iconBg: 'bg-surface-raised border border-border',
      iconColor: 'text-text-secondary',
    },
  };

  const current = configs[level] || configs.unknown;

  return (
    <div
      className={`rounded-card border p-6 text-center space-y-4 bg-surface ${current.border} ${className}`}
      role="region"
      aria-label="Scam risk assessment result"
    >
      {/* Category tag */}
      {category && (
        <div className="inline-block px-2.5 py-0.5 rounded-[6px] text-xs font-mono uppercase tracking-wider bg-surface-raised text-text-secondary border border-border">
          {category}
        </div>
      )}

      {/* Central icon */}
      <div className="flex justify-center">
        <div
          className={`w-11 h-11 rounded-[10px] flex items-center justify-center ${current.iconBg} ${current.iconColor}`}
        >
          {current.icon}
        </div>
      </div>

      {/* Headline */}
      <div className="space-y-1">
        <h2 className="text-xl font-medium tracking-tight text-text">
          {current.title}
        </h2>
      </div>

      {/* 3-segment qualitative meter (Honesty rule: No fake percentage bar) */}
      <div className="max-w-xs mx-auto pt-1">
        <RiskMeter level={level} score={score} scoreValidated={scoreValidated} />
      </div>

      {/* One-line finding / summary */}
      <p className="text-sm text-text-secondary max-w-md mx-auto pt-1 leading-relaxed">
        {summary}
      </p>

      {/* Honesty Rule 3 clarification for unknown */}
      {isUnknown && (
        <div className="text-xs text-text-muted bg-surface-raised p-3 rounded-[8px] border border-border text-left leading-relaxed">
          <span className="text-text font-medium">Note:</span> &quot;We can&apos;t tell&quot; means there was not enough verifiable context in your submission. An unknown status is neither a confirmation of safety nor of malicious intent. Always practice caution.
        </div>
      )}
    </div>
  );
};
