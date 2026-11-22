import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MessageSquare, Link2, ArrowRight } from 'lucide-react';
import { useStats, useScans } from '../hooks/useScans';
import { StatTile } from '../components/StatTile';
import { ScanCard } from '../components/ScanCard';
import { EmptyState } from '../components/EmptyState';
import { CardSkeleton } from '../components/Skeleton';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { data: stats, isLoading: statsLoading } = useStats();
  const { data: scans, isLoading: scansLoading } = useScans();

  const recentScans = scans ? scans.slice(0, 4) : [];

  return (
    <div className="space-y-6 max-w-2xl lg:max-w-4xl mx-auto py-2">
      {/* Minimal Header */}
      <div className="space-y-1.5">
        <div className="inline-flex items-center gap-2 text-xs font-medium text-text-muted">
          <span className="w-1.5 h-1.5 rounded-full bg-safe" />
          <span className="font-mono text-2xs uppercase tracking-wider">Engine Ready</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-text">
          Threat verification
        </h1>
        <p className="text-xs sm:text-sm text-text-secondary">
          Inspect SMS alerts, payment notices, or suspicious links for phishing signatures.
        </p>
      </div>

      {/* Primary Action Button */}
      <div>
        <button
          onClick={() => navigate('/scan')}
          className="w-full py-3.5 px-4 rounded-card bg-accent hover:bg-accent-hover text-white font-medium text-sm flex items-center justify-between transition-colors shadow-none"
        >
          <div className="flex items-center gap-2.5">
            <Search className="w-4 h-4 text-white" />
            <span>Verify suspicious message or link</span>
          </div>
          <span className="inline-flex items-center gap-1 text-xs text-white/90 bg-white/10 px-2.5 py-1 rounded-button">
            New scan <ArrowRight className="w-3.5 h-3.5" />
          </span>
        </button>
      </div>

      {/* Stats from real local/API storage */}
      <div className="grid grid-cols-2 gap-3">
        <StatTile
          value={statsLoading ? 0 : stats?.total ?? 0}
          label="verifications completed"
        />
        <StatTile
          value={statsLoading ? 0 : stats?.highRisk ?? 0}
          label="high-risk detected"
        />
      </div>

      {/* Quick-scan shortcuts */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <button
          onClick={() => navigate('/scan?type=text')}
          className="group flex items-center justify-between p-3.5 rounded-card bg-surface border border-border hover:bg-surface-raised transition-colors text-left"
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-8 h-8 rounded-button bg-surface-raised border border-border text-text-muted flex items-center justify-center shrink-0">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="text-xs font-medium text-text">
                Check message or SMS
              </div>
              <div className="text-2xs text-text-muted truncate mt-0.5">
                Paste copied text or bank alert
              </div>
            </div>
          </div>
          <span className="text-xs text-text-muted group-hover:text-text transition-colors shrink-0">→</span>
        </button>

        <button
          onClick={() => navigate('/scan?type=url')}
          className="group flex items-center justify-between p-3.5 rounded-card bg-surface border border-border hover:bg-surface-raised transition-colors text-left"
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-8 h-8 rounded-button bg-surface-raised border border-border text-text-muted flex items-center justify-center shrink-0">
              <Link2 className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="text-xs font-medium text-text">
                Check web link
              </div>
              <div className="text-2xs text-text-muted truncate mt-0.5">
                Inspect URL domain safely
              </div>
            </div>
          </div>
          <span className="text-xs text-text-muted group-hover:text-text transition-colors shrink-0">→</span>
        </button>
      </div>

      {/* Recent Scans */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <h2 className="text-2xs font-mono text-text-muted uppercase tracking-wider">
            Recent verifications
          </h2>
          {recentScans.length > 0 && (
            <button
              onClick={() => navigate('/history')}
              className="text-xs text-accent hover:underline font-mono"
            >
              View all ({scans?.length || 0})
            </button>
          )}
        </div>

        {scansLoading ? (
          <div className="space-y-3">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : recentScans.length === 0 ? (
          <EmptyState
            title="No checks performed yet"
            description="When you scan messages or links, your recent verifications will appear here."
            actionLabel="Start your first check"
            onAction={() => navigate('/scan')}
            icon="shield"
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {recentScans.map((scan) => (
              <ScanCard
                key={scan.id}
                scan={scan}
                onClick={() =>
                  navigate(
                    scan.status === 'running' || scan.status === 'queued'
                      ? `/scan/${scan.id}/progress`
                      : `/report/${scan.id}`
                  )
                }
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
