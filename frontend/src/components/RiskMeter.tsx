import React from 'react';
import { RiskLevel } from '../types';

export interface RiskMeterProps {
  level: RiskLevel;
  score?: number;
  scoreValidated?: boolean;
  className?: string;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({
  level,
  score,
  scoreValidated = false,
  className = '',
}) => {
  // Determine segment states based on qualitative risk level
  const isLowActive = level === 'low' || level === 'medium' || level === 'high';
  const isMediumActive = level === 'medium' || level === 'high';
  const isHighActive = level === 'high';

  return (
    <div className={`space-y-2 ${className}`}>
      {/* 3-segment qualitative bar */}
      <div
        className="grid grid-cols-3 gap-1.5 h-2 w-full"
        role="meter"
        aria-label="Qualitative risk level meter"
        aria-valuetext={level}
      >
        {/* Segment 1: Low */}
        <div
          className={`h-full rounded-full transition-colors duration-200 ${
            level === 'unknown'
              ? 'bg-border/40'
              : isLowActive
              ? level === 'low'
                ? 'bg-emerald-500'
                : 'bg-emerald-500/40'
              : 'bg-border/40'
          }`}
        />

        {/* Segment 2: Medium */}
        <div
          className={`h-full rounded-full transition-colors duration-200 ${
            level === 'unknown'
              ? 'bg-border/40'
              : isMediumActive
              ? level === 'medium'
                ? 'bg-amber-500'
                : 'bg-amber-500/40'
              : 'bg-border/40'
          }`}
        />

        {/* Segment 3: High */}
        <div
          className={`h-full rounded-full transition-colors duration-200 ${
            level === 'unknown'
              ? 'bg-border/40'
              : isHighActive
              ? 'bg-rose-500'
              : 'bg-border/40'
          }`}
        />
      </div>

      {/* Segment labels + Optional validated numeric score */}
      <div className="flex items-center justify-between text-[11px] text-text-muted font-medium">
        <span className={level === 'low' ? 'text-safe font-medium' : ''}>Low</span>
        <span className={level === 'medium' ? 'text-warn font-medium' : ''}>Medium</span>
        <span className={level === 'high' ? 'text-danger font-medium' : ''}>High</span>
      </div>

      {/* HONESTY RULE 2: Show numeric score ONLY if scoreValidated is true */}
      {scoreValidated && typeof score === 'number' && level !== 'unknown' && (
        <div className="text-center pt-1">
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-surface-2 border border-border/80 text-text-muted">
            Calibrated Index: {score} / 100
          </span>
        </div>
      )}
    </div>
  );
};
