import React from 'react';
import { ShieldAlert, AlertTriangle, Check, HelpCircle } from 'lucide-react';
import { RiskLevel } from '../types';

export interface RiskBadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  compact?: boolean;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  size = 'md',
  compact = false,
  className = '',
}) => {
  const configs: Record<
    RiskLevel,
    { label: string; compactLabel: string; icon: React.ReactNode; bg: string; text: string; border: string }
  > = {
    high: {
      label: 'Scam alert — High risk',
      compactLabel: 'SCAM',
      icon: <ShieldAlert className="shrink-0" />,
      bg: 'bg-danger-tint',
      text: 'text-danger font-bold',
      border: 'border-danger/30 shadow-[0_0_12px_rgba(239,68,68,0.2)]',
    },
    medium: {
      label: 'Be careful',
      compactLabel: 'BE CAREFUL',
      icon: <AlertTriangle className="shrink-0" />,
      bg: 'bg-warn-tint',
      text: 'text-warn font-bold',
      border: 'border-warn/30',
    },
    low: {
      label: 'Looks low risk',
      compactLabel: 'SAFE',
      icon: <Check className="shrink-0" />,
      bg: 'bg-safe-tint',
      text: 'text-safe font-bold',
      border: 'border-safe/30 shadow-[0_0_12px_rgba(16,185,129,0.15)]',
    },
    unknown: {
      label: "We can't tell",
      compactLabel: 'UNKNOWN',
      icon: <HelpCircle className="shrink-0" />,
      bg: 'bg-unknown-tint',
      text: 'text-unknown font-bold',
      border: 'border-unknown/30',
    },
  };

  const current = configs[level] || configs.unknown;
  const isCompact = compact || size === 'sm';

  const sizeClasses = {
    sm: 'text-[11px] px-2.5 py-0.5 gap-1.5 [&>svg]:w-3.5 [&>svg]:h-3.5 tracking-wider',
    md: 'text-xs sm:text-sm px-3.5 py-1.5 gap-2 [&>svg]:w-4 [&>svg]:h-4',
    lg: 'text-sm sm:text-base px-4 py-2 gap-2.5 [&>svg]:w-5 [&>svg]:h-5',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border ${current.bg} ${current.text} ${current.border} ${sizeClasses[size]} ${className}`}
      role="status"
    >
      {current.icon}
      <span>{isCompact ? current.compactLabel : current.label}</span>
    </span>
  );
};
