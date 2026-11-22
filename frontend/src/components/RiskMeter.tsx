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
    <div className={`space-y-2.5 ${className}`}>
      {/* 3-segment qualitative bar */}
      <div
        className="grid grid-cols-3 gap-2 h-4 w-full bg-surface-2/90 p-1 rounded-full border border-border shadow-inner"
        role="meter"
        aria-label="Qualitative risk level meter"
        aria-valuetext={level}
      >
        {/* Segment 1: Low */}
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            level === 'unknown'
              ? 'bg-unknown/20'
              : isLowActive
              ? level === 'low'
                ? 'bg-gradient-to-r from-emerald-500 to-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.4)]'
                : 'bg-emerald-500/50'
              : 'bg-border/60'
          }`}
        />

        {/* Segment 2: Medium */}
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            level === 'unknown'
              ? 'bg-unknown/20'
              : isMediumActive
              ? level === 'medium'
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.4)]'
                : 'bg-amber-500/50'
              : 'bg-border/60'
          }`}
        />

        {/* Segment 3: High */}
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            level === 'unknown'
              ? 'bg-unknown/20'
              : isHighActive
              ? 'bg-gradient-to-r from-red-600 to-rose-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]'
              : 'bg-border/60'
          }`}
        />
      </div>

      {/* Segment labels + Optional validated numeric score */}
      <div className="flex items-center justify-between text-xs text-text-muted px-1 font-semibold">
        <span className={level === 'low' ? 'text-safe font-bold' : ''}>Low Risk</span>
        <span className={level === 'medium' ? 'text-warn font-bold' : ''}>Medium Risk</span>
        <span className={level === 'high' ? 'text-danger font-bold' : ''}>High Risk</span>
      </div>

      {/* HONESTY RULE 2: Show numeric score ONLY if scoreValidated is true */}
      {scoreValidated && typeof score === 'number' && level !== 'unknown' && (
        <div className="text-center pt-1.5">
          <span className="text-xs font-bold px-3.5 py-1 rounded-full bg-surface border border-border text-text shadow-sm">
            Calibrated Score: {score} / 100
          </span>
        </div>
      )}
    </div>
  );
};
