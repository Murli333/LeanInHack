import React from 'react';
import { PhoneCall, ExternalLink, Shield } from 'lucide-react';
import { getActiveRegion } from '../config/regions';

export interface HelplineCardProps {
  className?: string;
}

export const HelplineCard: React.FC<HelplineCardProps> = ({ className = '' }) => {
  const region = getActiveRegion();

  return (
    <div
      className={`p-4 rounded-card bg-surface-2 border border-border space-y-3 ${className}`}
    >
      <div className="flex items-center gap-2">
        <Shield className="w-4 h-4 text-primary" />
        <span className="text-xs font-semibold text-text uppercase tracking-wider">
          Official Support ({region.name})
        </span>
      </div>

      <p className="text-xs text-text-muted leading-relaxed">
        {region.instructionText}
      </p>

      <div className="flex items-center gap-2 flex-wrap pt-1">
        {region.helpline && (
          <a
            href={`tel:${region.helpline}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-primary text-on-primary hover:bg-primary/90 transition-all shadow-sm"
          >
            <PhoneCall className="w-3.5 h-3.5" />
            <span>Call {region.helpline}</span>
          </a>
        )}

        {region.portalUrl && region.portalUrl !== '#' && (
          <a
            href={region.portalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-surface text-text border border-border hover:bg-surface-2 transition-all"
          >
            <span>{region.portalName}</span>
            <ExternalLink className="w-3 h-3 text-text-muted" />
          </a>
        )}
      </div>
    </div>
  );
};
