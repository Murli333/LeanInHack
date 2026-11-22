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
        <div className="w-7 h-7 rounded-lg bg-primary/10 border border-primary/25 flex items-center justify-center shrink-0 text-primary">
          <PhoneCall className="w-3.5 h-3.5" />
        </div>
      );
    }
    return (
      <div className="w-7 h-7 rounded-lg bg-safe/10 border border-safe/25 flex items-center justify-center shrink-0 text-safe">
        <ShieldCheck className="w-3.5 h-3.5" />
      </div>
    );
  };

  return (
    <div
      className={`rounded-xl border border-border/80 bg-surface p-4 sm:p-5 space-y-4 ${className}`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text flex items-center gap-2">
          <span>Recommended actions</span>
        </h3>
        <span className="text-[11px] font-mono text-text-muted uppercase tracking-wider">
          Safety protocol
        </span>
      </div>

      <div className="space-y-3">
        {actions.map((act, index) => (
          <div key={index} className="flex items-start gap-3 text-xs sm:text-sm text-text">
            {getActionIcon(act)}
            <span className="leading-snug pt-1">{act}</span>
          </div>
        ))}

        {/* Region helpline item */}
        <div className="flex items-start gap-3 text-xs sm:text-sm text-text pt-3 border-t border-border/60">
          <div className="w-7 h-7 rounded-lg bg-primary/10 border border-primary/25 flex items-center justify-center shrink-0 text-primary">
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
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-primary text-white border border-primary/40 hover:bg-blue-600 transition-colors"
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
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-2 border border-border/80 text-text hover:bg-surface-2/80 transition-colors"
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
