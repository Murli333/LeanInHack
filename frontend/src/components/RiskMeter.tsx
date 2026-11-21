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
        className="grid grid-cols-3 gap-1.5 h-3.5 w-full bg-surface-2 p-1 rounded-full border border-border"
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
                ? 'bg-safe'
                : 'bg-safe/60'
              : 'bg-border'
          }`}
        />

        {/* Segment 2: Medium */}
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            level === 'unknown'
              ? 'bg-unknown/20'
              : isMediumActive
              ? level === 'medium'
                ? 'bg-warn'
                : 'bg-warn/60'
              : 'bg-border'
          }`}
        />

        {/* Segment 3: High */}
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            level === 'unknown'
              ? 'bg-unknown/20'
              : isHighActive
              ? 'bg-danger'
              : 'bg-border'
          }`}
        />
      </div>

      {/* Segment labels + Optional validated numeric score */}
      <div className="flex items-center justify-between text-xs text-text-muted px-1">
        <span className={level === 'low' ? 'text-safe font-semibold' : ''}>Low</span>
        <span className={level === 'medium' ? 'text-warn font-semibold' : ''}>Medium</span>
        <span className={level === 'high' ? 'text-danger font-semibold' : ''}>High</span>
      </div>

      {/* HONESTY RULE 2: Show numeric score ONLY if scoreValidated is true */}
      {scoreValidated && typeof score === 'number' && level !== 'unknown' && (
        <div className="text-center pt-1">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-surface-2 border border-border text-text">
            Risk score {score} / 100
          </span>
        </div>
      )}
    </div>
  );
};
