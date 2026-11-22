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
          <div className="w-11 h-11 rounded-2xl bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0 shadow-sm text-accent group-hover:scale-105 transition-transform">
            <Link2 className="w-5 h-5" />
          </div>
        );
      case 'screenshot':
        return (
          <div className="w-11 h-11 rounded-2xl bg-warn/10 border border-warn/20 flex items-center justify-center shrink-0 shadow-sm text-warn group-hover:scale-105 transition-transform">
            <Image className="w-5 h-5" />
          </div>
        );
      case 'qr':
        return (
          <div className="w-11 h-11 rounded-2xl bg-safe/10 border border-safe/20 flex items-center justify-center shrink-0 shadow-sm text-safe group-hover:scale-105 transition-transform">
            <QrCode className="w-5 h-5" />
          </div>
        );
      case 'audio':
        return (
          <div className="w-11 h-11 rounded-2xl bg-danger/10 border border-danger/20 flex items-center justify-center shrink-0 shadow-sm text-danger group-hover:scale-105 transition-transform">
            <Mic className="w-5 h-5" />
          </div>
        );
      case 'text':
      default:
        return (
          <div className="w-11 h-11 rounded-2xl bg-primary/15 border border-primary/25 flex items-center justify-center shrink-0 shadow-sm text-accent group-hover:scale-105 transition-transform">
            <MessageSquare className="w-5 h-5" />
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
      className={`group flex items-center justify-between gap-3 p-4 rounded-card-lg bg-surface border border-border transition-all duration-200 hover:border-primary/40 hover:shadow-card-elevated hover:-translate-y-0.5 active:scale-[0.99] cursor-pointer text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${className}`}
    >
      {/* Icon tile + text */}
      <div className="flex items-center gap-3.5 min-w-0">
        {getTypeIcon(scan.type)}
        <div className="min-w-0">
          <h4 className="text-sm sm:text-base font-semibold text-text group-hover:text-primary dark:group-hover:text-accent transition-colors truncate">
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
        <ChevronRight className="w-4 h-4 text-text-muted transition-transform group-hover:translate-x-0.5" />
      </div>
    </div>
  );
};
