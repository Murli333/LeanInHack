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
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-safe-tint text-safe border border-safe/30 shrink-0">
            CONFIRMED
          </span>
        );
      case 'warning':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-warn-tint text-warn border border-warn/30 shrink-0">
            WARNING SIGN
          </span>
        );
      case 'not_run':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-unknown-tint text-unknown border border-unknown/30 shrink-0">
            NOT RUN
          </span>
        );
    }
  };

  const getIcon = (kind: EvidenceKind) => {
    switch (kind) {
      case 'confirmed':
        return <ShieldCheck className="w-5 h-5 text-safe shrink-0 mt-0.5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-warn shrink-0 mt-0.5" />;
      case 'not_run':
        return <HelpCircle className="w-5 h-5 text-text-muted shrink-0 mt-0.5" />;
    }
  };

  return (
    <div
      className={`flex items-start gap-3 p-3.5 rounded-card bg-surface-2 border border-border transition-colors hover:border-text-muted/30 ${className}`}
    >
      {getIcon(evidence.kind)}
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <h4 className="text-sm font-semibold text-text leading-tight">
            {evidence.title}
          </h4>
          {getKindBadge(evidence.kind)}
        </div>
        <p className="text-xs text-text-muted leading-relaxed">
          {evidence.detail}
        </p>
        {evidence.source && (
          <p className="text-[11px] text-text-muted/80 pt-0.5 font-mono">
            Source: {evidence.source}
          </p>
        )}
      </div>
    </div>
  );
};
