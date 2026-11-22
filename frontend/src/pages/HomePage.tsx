import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MessageSquare, Link2 } from 'lucide-react';
import { useStats, useScans } from '../hooks/useScans';
import { StatTile } from '../components/StatTile';
import { ScanCard } from '../components/ScanCard';
import { Button } from '../components/Button';
import { EmptyState } from '../components/EmptyState';
import { CardSkeleton } from '../components/Skeleton';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { data: stats, isLoading: statsLoading } = useStats();
  const { data: scans, isLoading: scansLoading } = useScans();

  const recentScans = scans ? scans.slice(0, 5) : [];

  return (
    <div className="space-y-8 max-w-2xl lg:max-w-4xl mx-auto py-2">
      {/* Minimal Header */}
      <div className="space-y-1.5">
        <div className="inline-flex items-center gap-2 text-xs font-medium text-text-muted">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          <span>Engine active</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-text">
          Verify suspicious content
        </h1>
        <p className="text-sm text-text-muted">
          Inspect SMS alerts, payment notices, or unfamiliar URLs for fraud indicators.
        </p>
      </div>

      {/* Primary Action Button */}
      <div>
        <button
          onClick={() => navigate('/scan')}
          className="w-full py-3.5 px-5 rounded-xl bg-primary hover:bg-blue-600 text-white font-medium text-sm sm:text-base flex items-center justify-between transition-colors border border-primary/30 active:scale-[0.99]"
        >
          <div className="flex items-center gap-2.5">
            <Search className="w-4 h-4 text-white/90" />
            <span>Start a new verification</span>
          </div>
          <span className="text-xs text-white/80 bg-white/15 px-2.5 py-1 rounded-md font-normal">Check now →</span>
        </button>
      </div>

      {/* Two Big Stats Side-by-Side (Honesty Rule 5: From Real Stored Data Only!) */}
      <div className="grid grid-cols-2 gap-3">
        <StatTile
          value={statsLoading ? 0 : stats?.total ?? 0}
          label="checks done"
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
          className="group flex items-center justify-between p-3.5 rounded-xl bg-surface border border-border/80 hover:border-border hover:bg-surface-2/40 transition-colors text-left"
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border/80 text-text-muted flex items-center justify-center shrink-0">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-medium text-text">
                Check message or SMS
              </div>
              <div className="text-xs text-text-muted truncate mt-0.5">
                Paste copied text or bank alert
              </div>
            </div>
          </div>
          <span className="text-xs text-text-muted group-hover:text-text transition-colors shrink-0">→</span>
        </button>

        <button
          onClick={() => navigate('/scan?type=url')}
          className="group flex items-center justify-between p-3.5 rounded-xl bg-surface border border-border/80 hover:border-border hover:bg-surface-2/40 transition-colors text-left"
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-lg bg-surface-2 border border-border/80 text-text-muted flex items-center justify-center shrink-0">
              <Link2 className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-medium text-text">
                Check web link
              </div>
              <div className="text-xs text-text-muted truncate mt-0.5">
                Inspect URL domain safely
              </div>
            </div>
          </div>
          <span className="text-xs text-text-muted group-hover:text-text transition-colors shrink-0">→</span>
        </button>
      </div>

      {/* YOUR RECENT CHECKS List */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold text-text-muted uppercase tracking-wider">
            YOUR RECENT CHECKS
          </h2>
          {recentScans.length > 0 && (
            <button
              onClick={() => navigate('/history')}
              className="text-xs font-semibold text-primary hover:underline"
            >
              View all
            </button>
          )}
        </div>

        {scansLoading ? (
          <div className="space-y-3">
            <CardSkeleton />
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
