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
        className="grid grid-cols-3 gap-2 h-[3px] w-full"
        role="meter"
        aria-label="Qualitative risk level meter"
        aria-valuetext={level}
      >
        {/* Segment 1: Low */}
        <div
          className={`h-full rounded-full transition-colors duration-150 ${
            level === 'unknown'
              ? 'bg-border'
              : isLowActive
              ? level === 'low'
                ? 'bg-safe'
                : 'bg-safe/40'
              : 'bg-border'
          }`}
        />

        {/* Segment 2: Medium */}
        <div
          className={`h-full rounded-full transition-colors duration-150 ${
            level === 'unknown'
              ? 'bg-border'
              : isMediumActive
              ? level === 'medium'
                ? 'bg-warn'
                : 'bg-warn/40'
              : 'bg-border'
          }`}
        />

        {/* Segment 3: High */}
        <div
          className={`h-full rounded-full transition-colors duration-150 ${
            level === 'unknown'
              ? 'bg-border'
              : isHighActive
              ? 'bg-danger'
              : 'bg-border'
          }`}
        />
      </div>

      {/* Segment labels + Optional validated numeric score */}
      <div className="flex items-center justify-between text-xs text-text-muted font-mono uppercase tracking-wider">
        <span className={level === 'low' ? 'text-safe font-medium' : ''}>Low</span>
        <span className={level === 'medium' ? 'text-warn font-medium' : ''}>Medium</span>
        <span className={level === 'high' ? 'text-danger font-medium' : ''}>High</span>
      </div>

      {/* HONESTY RULE 2: Show numeric score ONLY if scoreValidated is true */}
      {scoreValidated && typeof score === 'number' && level !== 'unknown' && (
        <div className="text-center pt-0.5">
          <span className="text-xs font-mono px-2.5 py-0.5 rounded-[6px] bg-surface-raised border border-border text-text-secondary">
            Calibrated Index: {score} / 100
          </span>
        </div>
      )}
    </div>
  );
};
