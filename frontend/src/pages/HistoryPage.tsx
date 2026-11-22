import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Trash2, Filter, RotateCcw } from 'lucide-react';
import { useScans, useDeleteScan, useDeleteAllScans, useResetSampleScans } from '../hooks/useScans';
import { ScanCard } from '../components/ScanCard';
import { Button } from '../components/Button';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { EmptyState } from '../components/EmptyState';
import { CardSkeleton } from '../components/Skeleton';
import { RiskLevel, ScanType } from '../types';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<ScanType | 'all'>('all');
  const [riskFilter, setRiskFilter] = useState<RiskLevel | 'all'>('all');

  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [showClearAll, setShowClearAll] = useState(false);

  const { data: scans, isLoading } = useScans({
    query: search,
    type: typeFilter,
    risk: riskFilter,
  });

  const deleteScanMutation = useDeleteScan();
  const deleteAllScansMutation = useDeleteAllScans();
  const resetSamplesMutation = useResetSampleScans();

  const handleConfirmSingleDelete = () => {
    if (deleteId) {
      deleteScanMutation.mutate(deleteId);
      setDeleteId(null);
    }
  };

  const handleConfirmClearAll = () => {
    deleteAllScansMutation.mutate();
    setShowClearAll(false);
  };

  const scanToDelete = scans?.find((s) => s.id === deleteId);

  return (
    <div className="space-y-6 max-w-4xl mx-auto py-2">
      {/* Page Header */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-text">
            Scan History
          </h1>
          <p className="text-xs sm:text-sm text-text-muted">
            All your verified messages and links stored locally on this device.
          </p>
        </div>

        {scans && scans.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            icon={<Trash2 className="w-4 h-4 text-danger" />}
            onClick={() => setShowClearAll(true)}
            className="text-danger hover:bg-danger-tint"
          >
            Clear all history
          </Button>
        )}
      </div>

      {/* Search Bar */}
      <div className="relative">
        <label htmlFor="history-search" className="sr-only">
          Search previous scans
        </label>
        <Search className="w-5 h-5 text-text-muted absolute left-4 top-1/2 -translate-y-1/2" />
        <input
          id="history-search"
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by keywords, phone numbers, or links..."
          className="w-full pl-12 pr-4 py-3.5 rounded-card-lg bg-surface border border-border text-sm text-text placeholder:text-text-muted/50 focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 shadow-card-soft transition-all duration-200"
        />
      </div>

      {/* Filter Chips Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="font-bold text-text-muted shrink-0 flex items-center gap-1 mr-1">
          <Filter className="w-3.5 h-3.5 text-accent" /> Type:
        </span>
        {(['all', 'text', 'url'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={`px-3.5 py-1.5 rounded-full capitalize font-semibold transition-all active:scale-95 ${
              typeFilter === t
                ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-sm shadow-blue-500/20 border border-blue-400/30'
                : 'bg-surface text-text-muted border border-border hover:text-text hover:border-primary/30'
            }`}
          >
            {t}
          </button>
        ))}

        <div className="h-4 w-px bg-border mx-2 shrink-0" />

        <span className="font-bold text-text-muted shrink-0 mr-1">Risk:</span>
        {(['all', 'high', 'medium', 'low', 'unknown'] as const).map((r) => (
          <button
            key={r}
            onClick={() => setRiskFilter(r)}
            className={`px-3.5 py-1.5 rounded-full capitalize font-semibold transition-all active:scale-95 ${
              riskFilter === r
                ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-sm shadow-blue-500/20 border border-blue-400/30'
                : 'bg-surface text-text-muted border border-border hover:text-text hover:border-primary/30'
            }`}
          >
            {r}
          </button>
        ))}
      </div>

      {/* Scan Results List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="space-y-3">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : !scans || scans.length === 0 ? (
          <div className="space-y-4">
            <EmptyState
              title={search ? 'No matching scans found' : 'Your history is empty'}
              description={
                search
                  ? `No scans found matching "${search}". Try adjusting your keywords or filters.`
                  : 'You have cleared or have not performed any scans yet.'
              }
              actionLabel={search ? 'Clear search filter' : 'Check a message now'}
              onAction={search ? () => setSearch('') : () => navigate('/scan')}
              icon="search"
            />

            {!search && (
              <div className="text-center pt-2">
                <Button
                  variant="ghost"
                  size="sm"
                  icon={<RotateCcw className="w-3.5 h-3.5" />}
                  onClick={() => resetSamplesMutation.mutate()}
                >
                  Reload sample mock scans
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {scans.map((scan) => (
              <div key={scan.id} className="relative group">
                <ScanCard
                  scan={scan}
                  onClick={() =>
                    navigate(
                      scan.status === 'running' || scan.status === 'queued'
                        ? `/scan/${scan.id}/progress`
                        : `/report/${scan.id}`
                    )
                  }
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteId(scan.id);
                  }}
                  className="absolute right-3 top-3 p-1.5 rounded-full bg-surface-2 text-text-muted hover:text-danger hover:bg-surface border border-border opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100"
                  aria-label={`Delete scan: ${scan.title}`}
                  title="Delete scan"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Confirm Dialog for Single Delete */}
      <ConfirmDialog
        isOpen={Boolean(deleteId)}
        title="Delete Scan Record"
        description={`Are you sure you want to remove "${scanToDelete?.title || 'this scan'}" from your local history? This action cannot be undone.`}
        confirmLabel="Delete"
        isDestructive
        onConfirm={handleConfirmSingleDelete}
        onCancel={() => setDeleteId(null)}
      />

      {/* Confirm Dialog for Clear All History */}
      <ConfirmDialog
        isOpen={showClearAll}
        title="Clear Entire Scan History"
        description={`This will permanently remove all ${scans?.length ?? 0} saved scan records and reset your home statistics to zero. Do you wish to continue?`}
        confirmLabel="Clear All"
        isDestructive
        onConfirm={handleConfirmClearAll}
        onCancel={() => setShowClearAll(false)}
      />
    </div>
  );
};
