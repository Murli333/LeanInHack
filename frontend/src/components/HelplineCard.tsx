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
      className={`p-3.5 rounded-lg bg-surface-2/60 border border-border/80 space-y-2.5 ${className}`}
    >
      <div className="flex items-center gap-2">
        <Shield className="w-3.5 h-3.5 text-text-muted" />
        <span className="text-[11px] font-mono text-text-muted uppercase tracking-wider">
          Official Support ({region.name})
        </span>
      </div>

      <p className="text-xs text-text-muted leading-relaxed">
        {region.instructionText}
      </p>

      <div className="flex items-center gap-2 flex-wrap pt-0.5">
        {region.helpline && (
          <a
            href={`tel:${region.helpline}`}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-primary text-white hover:bg-blue-600 transition-colors"
          >
            <PhoneCall className="w-3 h-3" />
            <span>Call {region.helpline}</span>
          </a>
        )}

        {region.portalUrl && region.portalUrl !== '#' && (
          <a
            href={region.portalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-surface text-text border border-border/80 hover:bg-surface-2 transition-colors"
          >
            <span>{region.portalName}</span>
            <ExternalLink className="w-3 h-3 text-text-muted" />
          </a>
        )}
      </div>
    </div>
  );
};
