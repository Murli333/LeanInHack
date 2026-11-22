import React from 'react';
import { XCircle, Lock, ShieldCheck, PhoneCall } from 'lucide-react';
import { getActiveRegion } from '../config/regions';

export interface ActionListProps {
  actions: string[];
  className?: string;
}

export const ActionList: React.FC<ActionListProps> = ({ actions, className = '' }) => {
  const region = getActiveRegion();

  const getActionIcon = (text: string) => {
    const lower = text.toLowerCase();
    if (lower.includes('click') || lower.includes('reply') || lower.includes('transfer')) {
      return (
        <div className="w-7 h-7 rounded-lg bg-danger/10 border border-danger/25 flex items-center justify-center shrink-0 text-danger">
          <XCircle className="w-3.5 h-3.5" />
        </div>
      );
    }
    if (lower.includes('otp') || lower.includes('password') || lower.includes('pin')) {
      return (
        <div className="w-7 h-7 rounded-lg bg-warn/10 border border-warn/25 flex items-center justify-center shrink-0 text-warn">
          <Lock className="w-3.5 h-3.5" />
        </div>
      );
    }
    if (lower.includes('call') || lower.includes('helpline') || lower.includes('1930')) {
      return (
        <div className="w-7 h-7 rounded-[7px] bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0 text-accent">
          <PhoneCall className="w-3.5 h-3.5" />
        </div>
      );
    }
    return (
      <div className="w-7 h-7 rounded-[7px] bg-safe/10 border border-safe/20 flex items-center justify-center shrink-0 text-safe">
        <ShieldCheck className="w-3.5 h-3.5" />
      </div>
    );
  };

  return (
    <div
      className={`rounded-card border border-border bg-surface p-5 space-y-4 ${className}`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-text flex items-center gap-2">
          <span>Recommended actions</span>
        </h3>
        <span className="text-xs font-mono text-text-muted uppercase tracking-wider">
          Safety protocol
        </span>
      </div>

      <div className="space-y-3">
        {actions.map((act, index) => (
          <div key={index} className="flex items-start gap-3 text-xs sm:text-sm text-text-secondary">
            {getActionIcon(act)}
            <span className="leading-relaxed pt-0.5">{act}</span>
          </div>
        ))}

        {/* Region helpline item */}
        <div className="flex items-start gap-3 text-xs sm:text-sm text-text pt-3 border-t border-border">
          <div className="w-7 h-7 rounded-[7px] bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0 text-accent">
            <PhoneCall className="w-3.5 h-3.5" />
          </div>
          <div className="space-y-2 flex-1">
            <div>
              <span className="font-medium text-text block leading-tight">
                Report fraud to official helpline
              </span>
              <span className="text-xs text-text-muted block mt-0.5">
                {region.instructionText}
              </span>
            </div>

            <div className="flex flex-wrap gap-2 pt-0.5">
              {region.helpline && (
                <a
                  href={`tel:${region.helpline}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[8px] text-xs font-medium bg-accent text-white hover:bg-accent-hover transition-colors"
                >
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>Call {region.helpline}</span>
                </a>
              )}
              {region.portalUrl && region.portalUrl !== '#' && (
                <a
                  href={region.portalUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[8px] text-xs font-medium bg-surface-raised border border-border text-text hover:bg-surface transition-colors"
                >
                  <span>{region.portalName}</span>
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
