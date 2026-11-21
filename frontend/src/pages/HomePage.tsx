import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MessageSquare, Link2, Sparkles, PlusCircle } from 'lucide-react';
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
      {/* Reference Greeting */}
      <div className="space-y-1">
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-text flex items-center gap-2">
          <span>Hello!</span>
          <span className="text-2xl sm:text-3xl" role="img" aria-label="Waving hand">👋</span>
        </h1>
        <p className="text-sm text-text-muted">
          Check suspicious messages, delivery notices, or payment links.
        </p>
      </div>

      {/* Reference Huge Pill Button: "Tap here to check" */}
      <div>
        <Button
          variant="primary"
          size="huge"
          fullWidth
          icon={<Search className="w-5 h-5 sm:w-6 sm:h-6" />}
          onClick={() => navigate('/scan')}
          className="shadow-lg shadow-primary/20 text-base sm:text-lg"
        >
          Tap here to check
        </Button>
      </div>

      {/* Two Big Stats Side-by-Side (Honesty Rule 5: From Real Stored Data Only!) */}
      <div className="grid grid-cols-2 gap-4">
        <StatTile
          value={statsLoading ? 0 : stats?.total ?? 0}
          label="checks done"
        />
        <StatTile
          value={statsLoading ? 0 : stats?.highRisk ?? 0}
          label="high-risk found"
        />
      </div>

      {/* Quick-scan shortcuts */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        <button
          onClick={() => navigate('/scan?type=text')}
          className="flex items-center gap-3 p-3.5 rounded-card bg-surface-2 border border-border hover:bg-surface hover:border-text-muted/30 transition-all text-left"
        >
          <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold text-text">Check a Text / SMS</div>
            <div className="text-xs text-text-muted truncate">Paste copied WhatsApp or bank text</div>
          </div>
        </button>

        <button
          onClick={() => navigate('/scan?type=url')}
          className="flex items-center gap-3 p-3.5 rounded-card bg-surface-2 border border-border hover:bg-surface hover:border-text-muted/30 transition-all text-left"
        >
          <div className="w-9 h-9 rounded-xl bg-accent/10 text-accent flex items-center justify-center shrink-0">
            <Link2 className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold text-text">Check a Web Link</div>
            <div className="text-xs text-text-muted truncate">Inspect link domain without opening</div>
          </div>
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
