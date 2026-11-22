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
      title: '🚨 Scam Alert — High Risk',
      icon: <ShieldAlert className="w-9 h-9" />,
      border: 'border-danger/50',
      cardBg: 'bg-gradient-to-b from-danger/10 via-surface to-surface',
      shadow: 'shadow-[0_0_40px_rgba(239,68,68,0.22)]',
      iconBg: 'bg-danger/15 border-2 border-danger/40 ring-4 ring-danger/20 shadow-lg shadow-danger/25',
      iconColor: 'text-danger',
    },
    medium: {
      title: '⚠️ Suspicious — Be Careful',
      icon: <AlertTriangle className="w-9 h-9" />,
      border: 'border-warn/50',
      cardBg: 'bg-gradient-to-b from-warn/10 via-surface to-surface',
      shadow: 'shadow-[0_0_30px_rgba(245,158,11,0.18)]',
      iconBg: 'bg-warn/15 border-2 border-warn/40 ring-4 ring-warn/20 shadow-lg shadow-warn/25',
      iconColor: 'text-warn',
    },
    low: {
      title: '✅ Verified — Looks Low Risk',
      icon: <Check className="w-9 h-9 stroke-[3]" />,
      border: 'border-safe/50',
      cardBg: 'bg-gradient-to-b from-safe/10 via-surface to-surface',
      shadow: 'shadow-[0_0_30px_rgba(16,185,129,0.18)]',
      iconBg: 'bg-safe/15 border-2 border-safe/40 ring-4 ring-safe/20 shadow-lg shadow-safe/25',
      iconColor: 'text-safe',
    },
    unknown: {
      title: "❓ Inconclusive — We Can't Tell",
      icon: <HelpCircle className="w-9 h-9" />,
      border: 'border-border',
      cardBg: 'bg-surface',
      shadow: 'shadow-card-soft',
      iconBg: 'bg-surface-2 border-2 border-border ring-4 ring-border/20',
      iconColor: 'text-text-muted',
    },
  };

  const current = configs[level] || configs.unknown;

  return (
    <div
      className={`rounded-card-lg border p-6 text-center space-y-4 transition-all ${current.cardBg} ${current.border} ${current.shadow} ${className}`}
      role="region"
      aria-label="Scam risk assessment result"
    >
      {/* Category tag */}
      {category && (
        <div className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-surface-2 text-text-muted border border-border">
          {category}
        </div>
      )}

      {/* Central shield / status icon badge */}
      <div className="flex justify-center">
        <div
          className={`w-16 h-16 rounded-full flex items-center justify-center transition-transform hover:scale-105 ${current.iconBg} ${current.iconColor}`}
        >
          {current.icon}
        </div>
      </div>

      {/* Headline */}
      <div className="space-y-1">
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-text">
          {current.title}
        </h2>
      </div>

      {/* 3-segment qualitative meter (Honesty rule: No fake percentage bar) */}
      <div className="max-w-xs mx-auto pt-1">
        <RiskMeter level={level} score={score} scoreValidated={scoreValidated} />
      </div>

      {/* One-line finding / summary */}
      <p className="text-sm sm:text-base text-text-muted max-w-md mx-auto pt-2 leading-relaxed">
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
