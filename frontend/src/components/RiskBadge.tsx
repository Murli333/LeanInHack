import React from 'react';
import { ShieldAlert, AlertTriangle, Check, HelpCircle } from 'lucide-react';
import { RiskLevel } from '../types';

export interface RiskBadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  size = 'md',
  className = '',
}) => {
  const configs: Record<
    RiskLevel,
    { label: string; icon: React.ReactNode; bg: string; text: string; border: string }
  > = {
    high: {
      label: 'Scam alert — High risk',
      icon: <ShieldAlert className="shrink-0" />,
      bg: 'bg-danger-tint',
      text: 'text-danger font-semibold',
      border: 'border-danger/30',
    },
    medium: {
      label: 'Be careful',
      icon: <AlertTriangle className="shrink-0" />,
      bg: 'bg-warn-tint',
      text: 'text-warn font-semibold',
      border: 'border-warn/30',
    },
    low: {
      label: 'Looks low risk',
      icon: <Check className="shrink-0" />,
      bg: 'bg-safe-tint',
      text: 'text-safe font-semibold',
      border: 'border-safe/30',
    },
    unknown: {
      label: "We can't tell",
      icon: <HelpCircle className="shrink-0" />,
      bg: 'bg-unknown-tint',
      text: 'text-unknown font-semibold',
      border: 'border-unknown/30',
    },
  };

  const current = configs[level] || configs.unknown;

  const sizeClasses = {
    sm: 'text-xs px-2.5 py-1 gap-1.5 [&>svg]:w-3.5 [&>svg]:h-3.5',
    md: 'text-xs sm:text-sm px-3.5 py-1.5 gap-2 [&>svg]:w-4 [&>svg]:h-4',
    lg: 'text-sm sm:text-base px-4 py-2 gap-2.5 [&>svg]:w-5 [&>svg]:h-5',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-sm ${current.bg} ${current.text} ${current.border} ${sizeClasses[size]} ${className}`}
      role="status"
    >
      {current.icon}
      <span>{current.label}</span>
    </span>
  );
};
