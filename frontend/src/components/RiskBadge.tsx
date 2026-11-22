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
      compactLabel: 'HIGH RISK',
      icon: <ShieldAlert className="shrink-0" />,
      bg: 'bg-danger/10',
      text: 'text-danger font-medium',
      border: 'border-danger/25',
    },
    medium: {
      label: 'Be careful',
      compactLabel: 'MEDIUM RISK',
      icon: <AlertTriangle className="shrink-0" />,
      bg: 'bg-warn/10',
      text: 'text-warn font-medium',
      border: 'border-warn/25',
    },
    low: {
      label: 'Looks low risk',
      compactLabel: 'LOW RISK',
      icon: <Check className="shrink-0" />,
      bg: 'bg-safe/10',
      text: 'text-safe font-medium',
      border: 'border-safe/25',
    },
    unknown: {
      label: "We can't tell",
      compactLabel: 'UNKNOWN',
      icon: <HelpCircle className="shrink-0" />,
      bg: 'bg-unknown/10',
      text: 'text-unknown font-medium',
      border: 'border-unknown/25',
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
