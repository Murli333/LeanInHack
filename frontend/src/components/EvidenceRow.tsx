import React from 'react';
import { ShieldCheck, AlertTriangle, AlertCircle, HelpCircle } from 'lucide-react';
import { EvidenceItem, EvidenceKind } from '../types';

export interface EvidenceRowProps {
  evidence: EvidenceItem;
  className?: string;
}

export const EvidenceRow: React.FC<EvidenceRowProps> = ({ evidence, className = '' }) => {
  const getKindBadge = (kind: EvidenceKind) => {
    switch (kind) {
      case 'confirmed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-safe/15 text-safe border border-safe/30 shadow-[0_0_10px_rgba(16,185,129,0.15)] shrink-0">
            CONFIRMED
          </span>
        );
      case 'warning':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-warn/15 text-warn border border-warn/30 shadow-[0_0_10px_rgba(245,158,11,0.15)] shrink-0">
            WARNING
          </span>
        );
      case 'not_run':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-surface-2 text-text-muted border border-border shrink-0">
            NOT RUN
          </span>
        );
    }
  };

  const getIcon = (kind: EvidenceKind) => {
    switch (kind) {
      case 'confirmed':
        return (
          <div className="w-8 h-8 rounded-xl bg-safe/15 border border-safe/30 flex items-center justify-center shrink-0 text-safe shadow-sm">
            <ShieldCheck className="w-4 h-4 stroke-[2.5]" />
          </div>
        );
      case 'warning':
        return (
          <div className="w-8 h-8 rounded-xl bg-warn/15 border border-warn/30 flex items-center justify-center shrink-0 text-warn shadow-sm">
            <AlertTriangle className="w-4 h-4" />
          </div>
        );
      case 'not_run':
        return (
          <div className="w-8 h-8 rounded-xl bg-surface-2 border border-border flex items-center justify-center shrink-0 text-text-muted shadow-sm">
            <HelpCircle className="w-4 h-4" />
          </div>
        );
    }
  };

  return (
    <div
      className={`flex items-start gap-3.5 p-4 rounded-card-lg bg-surface border border-border transition-all duration-200 hover:border-primary/40 hover:shadow-card-soft ${className}`}
    >
      {getIcon(evidence.kind)}
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <h4 className="text-sm font-bold text-text leading-tight">
            {evidence.title}
          </h4>
          {getKindBadge(evidence.kind)}
        </div>
        <p className="text-xs text-text-muted leading-relaxed font-normal">
          {evidence.detail}
        </p>
        {evidence.source && (
          <div className="pt-1">
            <span className="inline-block text-[10px] text-text-muted font-medium bg-surface-2 px-2 py-0.5 rounded-md border border-border/80">
              Source: {evidence.source}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
