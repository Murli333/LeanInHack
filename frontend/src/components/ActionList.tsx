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
        <div className="w-8 h-8 rounded-xl bg-danger/15 border border-danger/30 flex items-center justify-center shrink-0 shadow-sm text-danger">
          <XCircle className="w-4 h-4 stroke-[2.5]" />
        </div>
      );
    }
    if (lower.includes('otp') || lower.includes('password') || lower.includes('pin')) {
      return (
        <div className="w-8 h-8 rounded-xl bg-warn/15 border border-warn/30 flex items-center justify-center shrink-0 shadow-sm text-warn">
          <Lock className="w-4 h-4" />
        </div>
      );
    }
    if (lower.includes('call') || lower.includes('helpline') || lower.includes('1930')) {
      return (
        <div className="w-8 h-8 rounded-xl bg-accent/15 border border-accent/30 flex items-center justify-center shrink-0 shadow-sm text-accent">
          <PhoneCall className="w-4 h-4" />
        </div>
      );
    }
    return (
      <div className="w-8 h-8 rounded-xl bg-safe/15 border border-safe/30 flex items-center justify-center shrink-0 shadow-sm text-safe">
        <ShieldCheck className="w-4 h-4 stroke-[2.5]" />
      </div>
    );
  };

  return (
    <div
      className={`rounded-card-lg border border-safe/40 bg-gradient-to-b from-safe/10 via-surface to-surface p-5 space-y-4 shadow-card-soft ${className}`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-text flex items-center gap-2">
          <span>Stay safe</span>
          <span className="w-2 h-2 rounded-full bg-safe animate-pulse" />
        </h3>
        <span className="text-xs font-semibold text-safe uppercase tracking-wider">
          Recommended Steps
        </span>
      </div>

      <div className="space-y-3">
        {actions.map((act, index) => (
          <div key={index} className="flex items-start gap-3.5 text-sm font-medium text-text">
            {getActionIcon(act)}
            <span className="leading-snug pt-1">{act}</span>
          </div>
        ))}

        {/* Region helpline item */}
        <div className="flex items-start gap-3.5 text-sm text-text pt-3 border-t border-safe/25">
          <div className="w-8 h-8 rounded-xl bg-accent/15 border border-accent/30 flex items-center justify-center shrink-0 shadow-sm text-accent">
            <PhoneCall className="w-4 h-4" />
          </div>
          <div className="space-y-2 flex-1">
            <div>
              <span className="font-bold text-text block leading-tight">
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
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-accent/20 text-accent border border-accent/40 hover:bg-accent/30 transition-all active:scale-95 shadow-sm"
                >
                  <PhoneCall className="w-3 h-3" />
                  <span>Call {region.helpline}</span>
                </a>
              )}
              {region.portalUrl && region.portalUrl !== '#' && (
                <a
                  href={region.portalUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-surface border border-border hover:border-text-muted/40 text-text-muted hover:text-text transition-all active:scale-95 shadow-sm"
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
