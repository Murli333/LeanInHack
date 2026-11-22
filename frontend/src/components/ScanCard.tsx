import React from 'react';
import { MessageSquare, Link2, Image, QrCode, Mic, ChevronRight } from 'lucide-react';
import { Scan, ScanType } from '../types';
import { RiskBadge } from './RiskBadge';

export interface ScanCardProps {
  scan: Scan;
  onClick?: () => void;
  className?: string;
}

export const ScanCard: React.FC<ScanCardProps> = ({ scan, onClick, className = '' }) => {
  const getTypeIcon = (type: ScanType) => {
    switch (type) {
      case 'url':
        return (
          <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border/80 flex items-center justify-center shrink-0 text-text-muted">
            <Link2 className="w-4 h-4" />
          </div>
        );
      case 'screenshot':
        return (
          <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border/80 flex items-center justify-center shrink-0 text-text-muted">
            <Image className="w-4 h-4" />
          </div>
        );
      case 'qr':
        return (
          <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border/80 flex items-center justify-center shrink-0 text-text-muted">
            <QrCode className="w-4 h-4" />
          </div>
        );
      case 'audio':
        return (
          <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border/80 flex items-center justify-center shrink-0 text-text-muted">
            <Mic className="w-4 h-4" />
          </div>
        );
      case 'text':
      default:
        return (
          <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border/80 flex items-center justify-center shrink-0 text-text-muted">
            <MessageSquare className="w-4 h-4" />
          </div>
        );
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const riskLevel = scan.result?.riskLevel || 'unknown';

  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
      className={`group flex items-center justify-between gap-3 p-3.5 rounded-xl bg-surface border border-border/80 transition-colors hover:border-border hover:bg-surface-2/40 active:scale-[0.99] cursor-pointer text-left focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-border ${className}`}
    >
      {/* Icon tile + text */}
      <div className="flex items-center gap-3 min-w-0">
        {getTypeIcon(scan.type)}
        <div className="min-w-0">
          <h4 className="text-sm font-medium text-text transition-colors truncate">
            {scan.title}
          </h4>
          <p className="text-xs text-text-muted mt-0.5">
            {formatDate(scan.createdAt)}
          </p>
        </div>
      </div>

      {/* Right side status pill + chevron */}
      <div className="flex items-center gap-2 shrink-0">
        <RiskBadge level={riskLevel} size="sm" />
        <ChevronRight className="w-4 h-4 text-text-muted transition-transform group-hover:translate-x-0.5" />
      </div>
    </div>
  );
};
