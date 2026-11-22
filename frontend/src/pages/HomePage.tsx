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
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary dark:text-accent border border-primary/20 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-accent" />
          <span>AI Protection Ready</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-text flex items-center gap-2">
          <span>Hello!</span>
          <span className="text-2xl sm:text-3xl animate-bounce-subtle" role="img" aria-label="Waving hand">👋</span>
        </h1>
        <p className="text-sm sm:text-base text-text-muted">
          Check suspicious messages, delivery notices, or payment links.
        </p>
      </div>

      {/* Reference Huge Pill Button: "Tap here to check" */}
      <div>
        <button
          onClick={() => navigate('/scan')}
          className="w-full py-4 sm:py-5 px-6 rounded-pill bg-gradient-to-r from-blue-600 via-blue-500 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-base sm:text-lg flex items-center justify-center gap-3 shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/35 hover:scale-[1.01] active:scale-[0.98] transition-all duration-200 group border border-white/20"
        >
          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center group-hover:scale-110 transition-transform">
            <Search className="w-4 h-4 sm:w-5 sm:h-5 text-white stroke-[2.5]" />
          </div>
          <span className="tracking-wide">Tap here to check</span>
        </button>
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
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-1">
        <button
          onClick={() => navigate('/scan?type=text')}
          className="group flex items-center justify-between p-4 rounded-card-lg bg-surface border border-border hover:border-primary/40 hover:shadow-card-elevated hover:-translate-y-0.5 transition-all duration-200 text-left"
        >
          <div className="flex items-center gap-3.5 min-w-0">
            <div className="w-10 h-10 rounded-2xl bg-primary/10 border border-primary/20 text-accent flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-bold text-text group-hover:text-primary dark:group-hover:text-accent transition-colors">
                Check a Text / SMS
              </div>
              <div className="text-xs text-text-muted truncate mt-0.5">
                Paste copied WhatsApp or bank text
              </div>
            </div>
          </div>
          <PlusCircle className="w-4 h-4 text-text-muted group-hover:text-primary dark:group-hover:text-accent transition-colors shrink-0" />
        </button>

        <button
          onClick={() => navigate('/scan?type=url')}
          className="group flex items-center justify-between p-4 rounded-card-lg bg-surface border border-border hover:border-primary/40 hover:shadow-card-elevated hover:-translate-y-0.5 transition-all duration-200 text-left"
        >
          <div className="flex items-center gap-3.5 min-w-0">
            <div className="w-10 h-10 rounded-2xl bg-accent/10 border border-accent/20 text-accent flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <Link2 className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-bold text-text group-hover:text-primary dark:group-hover:text-accent transition-colors">
                Check a Web Link
              </div>
              <div className="text-xs text-text-muted truncate mt-0.5">
                Inspect link domain without opening
              </div>
            </div>
          </div>
          <PlusCircle className="w-4 h-4 text-text-muted group-hover:text-primary dark:group-hover:text-accent transition-colors shrink-0" />
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
