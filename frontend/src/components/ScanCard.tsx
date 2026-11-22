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
          <div className="w-8 h-8 rounded-button bg-surface-raised border border-border flex items-center justify-center shrink-0 text-text-muted">
            <Link2 className="w-3.5 h-3.5" />
          </div>
        );
      case 'screenshot':
        return (
          <div className="w-8 h-8 rounded-button bg-surface-raised border border-border flex items-center justify-center shrink-0 text-text-muted">
            <Image className="w-3.5 h-3.5" />
          </div>
        );
      case 'qr':
        return (
          <div className="w-8 h-8 rounded-button bg-surface-raised border border-border flex items-center justify-center shrink-0 text-text-muted">
            <QrCode className="w-3.5 h-3.5" />
          </div>
        );
      case 'audio':
        return (
          <div className="w-8 h-8 rounded-button bg-surface-raised border border-border flex items-center justify-center shrink-0 text-text-muted">
            <Mic className="w-3.5 h-3.5" />
          </div>
        );
      case 'text':
      default:
        return (
          <div className="w-8 h-8 rounded-button bg-surface-raised border border-border flex items-center justify-center shrink-0 text-text-muted">
            <MessageSquare className="w-3.5 h-3.5" />
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
      className={`group flex items-center justify-between gap-3 p-3.5 rounded-card bg-surface border border-border hover:bg-surface-raised transition-colors cursor-pointer text-left ${className}`}
    >
      {/* Icon tile + text */}
      <div className="flex items-center gap-3 min-w-0">
        {getTypeIcon(scan.type)}
        <div className="min-w-0">
          <h4 className="text-xs font-medium text-text truncate">
            {scan.title}
          </h4>
          <p className="text-2xs text-text-muted font-mono mt-0.5">
            {formatDate(scan.createdAt)}
          </p>
        </div>
      </div>

      {/* Right side status pill + chevron */}
      <div className="flex items-center gap-2 shrink-0">
        <RiskBadge level={riskLevel} size="sm" />
        <ChevronRight className="w-3.5 h-3.5 text-text-muted transition-transform group-hover:translate-x-0.5" />
      </div>
    </div>
  );
};
