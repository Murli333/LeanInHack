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
      return <XCircle className="w-5 h-5 text-danger shrink-0 mt-0.5" />;
    }
    if (lower.includes('otp') || lower.includes('password') || lower.includes('pin')) {
      return <Lock className="w-5 h-5 text-warn shrink-0 mt-0.5" />;
    }
    if (lower.includes('call') || lower.includes('helpline') || lower.includes('1930')) {
      return <PhoneCall className="w-5 h-5 text-accent shrink-0 mt-0.5" />;
    }
    return <ShieldCheck className="w-5 h-5 text-safe shrink-0 mt-0.5" />;
  };

  return (
    <div
      className={`rounded-card-lg border border-safe/30 bg-safe-tint p-5 space-y-4 ${className}`}
    >
      <div className="flex items-center gap-2">
        <h3 className="text-base font-bold text-text">Stay safe</h3>
      </div>

      <div className="space-y-3">
        {actions.map((act, index) => (
          <div key={index} className="flex items-start gap-3 text-sm text-text">
            {getActionIcon(act)}
            <span className="leading-snug">{act}</span>
          </div>
        ))}

        {/* Region helpline item */}
        <div className="flex items-start gap-3 text-sm text-text pt-1 border-t border-safe/20">
          <PhoneCall className="w-5 h-5 text-accent shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold block leading-tight">
              Report suspicious activity:
            </span>
            <span className="text-xs text-text-muted block">
              {region.instructionText}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
