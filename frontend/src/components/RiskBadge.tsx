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
      label: 'High Risk',
      compactLabel: 'HIGH RISK',
      icon: <ShieldAlert className="shrink-0" />,
      bg: 'bg-danger/10',
      text: 'text-danger font-medium',
      border: 'border-danger/20',
    },
    medium: {
      label: 'Medium Risk',
      compactLabel: 'MEDIUM RISK',
      icon: <AlertTriangle className="shrink-0" />,
      bg: 'bg-warn/10',
      text: 'text-warn font-medium',
      border: 'border-warn/20',
    },
    low: {
      label: 'Low Risk',
      compactLabel: 'LOW RISK',
      icon: <Check className="shrink-0" />,
      bg: 'bg-safe/10',
      text: 'text-safe font-medium',
      border: 'border-safe/20',
    },
    unknown: {
      label: 'Inconclusive',
      compactLabel: 'UNKNOWN',
      icon: <HelpCircle className="shrink-0" />,
      bg: 'bg-surface-raised',
      text: 'text-text-secondary font-medium',
      border: 'border-border',
    },
  };

  const current = configs[level] || configs.unknown;
  const isCompact = compact || size === 'sm';

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5 [&>svg]:w-3 [&>svg]:h-3 font-mono tracking-wider',
    md: 'text-xs px-2.5 py-1 gap-1.5 [&>svg]:w-3.5 [&>svg]:h-3.5 font-mono tracking-wider',
    lg: 'text-xs sm:text-sm px-3 py-1.5 gap-2 [&>svg]:w-4 [&>svg]:h-4 font-mono tracking-wider',
  };

  return (
    <span
      className={`inline-flex items-center rounded-[6px] border ${current.bg} ${current.text} ${current.border} ${sizeClasses[size]} ${className}`}
      role="status"
    >
      {current.icon}
      <span>{isCompact ? current.compactLabel : current.label}</span>
    </span>
  );
};
