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
          <span className="inline-flex items-center px-2 py-0.5 rounded-[5px] text-[10px] font-mono uppercase tracking-wider bg-safe/10 text-safe border border-safe/20 shrink-0">
            CONFIRMED
          </span>
        );
      case 'warning':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-[5px] text-[10px] font-mono uppercase tracking-wider bg-warn/10 text-warn border border-warn/20 shrink-0">
            WARNING
          </span>
        );
      case 'not_run':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-[5px] text-[10px] font-mono uppercase tracking-wider bg-surface text-text-muted border border-border shrink-0">
            NOT RUN
          </span>
        );
    }
  };

  const getIcon = (kind: EvidenceKind) => {
    switch (kind) {
      case 'confirmed':
        return (
          <div className="w-7 h-7 rounded-[7px] bg-safe/10 border border-safe/20 flex items-center justify-center shrink-0 text-safe">
            <ShieldCheck className="w-3.5 h-3.5" />
          </div>
        );
      case 'warning':
        return (
          <div className="w-7 h-7 rounded-[7px] bg-warn/10 border border-warn/20 flex items-center justify-center shrink-0 text-warn">
            <AlertTriangle className="w-3.5 h-3.5" />
          </div>
        );
      case 'not_run':
        return (
          <div className="w-7 h-7 rounded-[7px] bg-surface border border-border flex items-center justify-center shrink-0 text-text-muted">
            <HelpCircle className="w-3.5 h-3.5" />
          </div>
        );
    }
  };

  return (
    <div
      className={`flex items-start gap-3 p-3.5 rounded-[10px] bg-surface-raised border border-border transition-colors ${className}`}
    >
      {getIcon(evidence.kind)}
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <h4 className="text-sm font-medium text-text leading-tight">
            {evidence.title}
          </h4>
          {getKindBadge(evidence.kind)}
        </div>
        <p className="text-xs text-text-secondary leading-relaxed font-normal">
          {evidence.detail}
        </p>
        {evidence.source && (
          <div className="pt-1">
            <span className="inline-block text-[10px] text-text-muted font-mono bg-surface px-2 py-0.5 rounded-[4px] border border-border">
              Source: {evidence.source}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
