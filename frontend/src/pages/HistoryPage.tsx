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
          <h1 className="text-2xl font-medium tracking-tight text-text">
            History
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary">
            All locally verified messages and URLs on this device.
          </p>
        </div>

        {scans && scans.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            icon={<Trash2 className="w-3.5 h-3.5 text-danger" />}
            onClick={() => setShowClearAll(true)}
            className="text-danger hover:bg-danger/10"
          >
            Clear history
          </Button>
        )}
      </div>

      {/* Search Bar */}
      <div className="relative">
        <label htmlFor="history-search" className="sr-only">
          Search previous scans
        </label>
        <Search className="w-4 h-4 text-text-muted absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          id="history-search"
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search keywords, phone numbers, or links..."
          className="w-full pl-10 pr-4 py-2.5 rounded-button bg-surface-raised border border-border text-xs sm:text-sm text-text placeholder:text-text-muted focus:outline-none focus:border-accent/80 transition-colors"
        />
      </div>

      {/* Filter Chips Bar */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
        <span className="font-medium text-text-muted shrink-0 flex items-center gap-1 mr-1">
          <Filter className="w-3 h-3 text-text-muted" /> Type:
        </span>
        {(['all', 'text', 'url'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={`px-2.5 py-1 rounded-button capitalize text-xs font-medium transition-colors border ${
              typeFilter === t
                ? 'bg-accent text-white border-accent'
                : 'bg-surface text-text-secondary border-border hover:text-text hover:bg-surface-raised'
            }`}
          >
            {t}
          </button>
        ))}

        <div className="h-3.5 w-px bg-border mx-1.5 shrink-0" />

        <span className="font-medium text-text-muted shrink-0 mr-1">Risk:</span>
        {(['all', 'high', 'medium', 'low', 'unknown'] as const).map((r) => (
          <button
            key={r}
            onClick={() => setRiskFilter(r)}
            className={`px-2.5 py-1 rounded-button capitalize text-xs font-medium transition-colors border ${
              riskFilter === r
                ? 'bg-accent text-white border-accent'
                : 'bg-surface text-text-secondary border-border hover:text-text hover:bg-surface-raised'
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
                  className="absolute right-3 top-3 p-1.5 rounded-full bg-surface-raised text-text-muted hover:text-danger hover:bg-surface border border-border opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100"
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
