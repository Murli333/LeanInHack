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
      cardBg: string;
      shadow: string;
      iconBg: string;
      iconColor: string;
    }
  > = {
    high: {
      title: 'High Risk Detected',
      icon: <ShieldAlert className="w-6 h-6" />,
      border: 'border-danger/30',
      cardBg: 'bg-surface',
      shadow: 'shadow-none',
      iconBg: 'bg-danger/10 border border-danger/25',
      iconColor: 'text-danger',
    },
    medium: {
      title: 'Suspicious Indicators Found',
      icon: <AlertTriangle className="w-6 h-6" />,
      border: 'border-warn/30',
      cardBg: 'bg-surface',
      shadow: 'shadow-none',
      iconBg: 'bg-warn/10 border border-warn/25',
      iconColor: 'text-warn',
    },
    low: {
      title: 'No Threats Detected',
      icon: <Check className="w-6 h-6" />,
      border: 'border-safe/30',
      cardBg: 'bg-surface',
      shadow: 'shadow-none',
      iconBg: 'bg-safe/10 border border-safe/25',
      iconColor: 'text-safe',
    },
    unknown: {
      title: 'Inconclusive Result',
      icon: <HelpCircle className="w-6 h-6" />,
      border: 'border-border/80',
      cardBg: 'bg-surface',
      shadow: 'shadow-none',
      iconBg: 'bg-surface-2 border border-border/80',
      iconColor: 'text-text-muted',
    },
  };

  const current = configs[level] || configs.unknown;

  return (
    <div
      className={`rounded-xl border p-5 sm:p-6 text-center space-y-3.5 transition-colors ${current.cardBg} ${current.border} ${className}`}
      role="region"
      aria-label="Scam risk assessment result"
    >
      {/* Category tag */}
      {category && (
        <div className="inline-block px-2.5 py-0.5 rounded-md text-[11px] font-mono uppercase tracking-wider bg-surface-2 text-text-muted border border-border/80">
          {category}
        </div>
      )}

      {/* Central icon */}
      <div className="flex justify-center">
        <div
          className={`w-12 h-12 rounded-xl flex items-center justify-center ${current.iconBg} ${current.iconColor}`}
        >
          {current.icon}
        </div>
      </div>

      {/* Headline */}
      <div className="space-y-0.5">
        <h2 className="text-xl font-semibold tracking-tight text-text">
          {current.title}
        </h2>
      </div>

      {/* 3-segment qualitative meter (Honesty rule: No fake percentage bar) */}
      <div className="max-w-xs mx-auto pt-1">
        <RiskMeter level={level} score={score} scoreValidated={scoreValidated} />
      </div>

      {/* One-line finding / summary */}
      <p className="text-xs sm:text-sm text-text-muted max-w-md mx-auto pt-1 leading-relaxed">
        {summary}
      </p>

      {/* Honesty Rule 3 clarification for unknown */}
      {isUnknown && (
        <div className="text-xs text-text-muted bg-surface-2 p-3 rounded-card border border-border text-left">
          <strong>Note:</strong> &quot;We can&apos;t tell&quot; means there wasn&apos;t enough verifiable information in your submission. An unknown status is <strong>not</strong> a confirmation that the message is safe, nor that it is malicious. Always stay cautious.
        </div>
      )}
    </div>
  );
};
