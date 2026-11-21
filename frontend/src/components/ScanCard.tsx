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
        return <Link2 className="w-5 h-5 text-accent" />;
      case 'screenshot':
        return <Image className="w-5 h-5 text-warn" />;
      case 'qr':
        return <QrCode className="w-5 h-5 text-safe" />;
      case 'audio':
        return <Mic className="w-5 h-5 text-danger" />;
      case 'text':
      default:
        return <MessageSquare className="w-5 h-5 text-primary" />;
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
      className={`flex items-center justify-between gap-3 p-4 rounded-card-lg bg-surface-2 border border-border transition-all hover:bg-surface hover:border-text-muted/30 hover:shadow-card-soft cursor-pointer text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${className}`}
    >
      {/* Icon tile + text */}
      <div className="flex items-center gap-3.5 min-w-0">
        <div className="w-11 h-11 rounded-2xl bg-surface border border-border flex items-center justify-center shrink-0 shadow-sm">
          {getTypeIcon(scan.type)}
        </div>
        <div className="min-w-0">
          <h4 className="text-sm sm:text-base font-semibold text-text truncate">
            {scan.title}
          </h4>
          <p className="text-xs text-text-muted font-medium mt-0.5">
            {formatDate(scan.createdAt)}
          </p>
        </div>
      </div>

      {/* Right side status pill + chevron */}
      <div className="flex items-center gap-2 shrink-0">
        <RiskBadge level={riskLevel} size="sm" />
        <ChevronRight className="w-4 h-4 text-text-muted hidden sm:block" />
      </div>
    </div>
  );
};
