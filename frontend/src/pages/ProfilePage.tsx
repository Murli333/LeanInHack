import React, { useState } from 'react';
import { ThemeToggle } from '../components/ThemeToggle';
import { Button } from '../components/Button';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { useDeleteAllScans, useResetSampleScans } from '../hooks/useScans';
import {
  SUPPORTED_REGIONS,
  getActiveRegion,
  setActiveRegion,
} from '../config/regions';
import {
  User,
  Palette,
  Globe,
  Shield,
  Trash2,
  Lock,
  RotateCcw,
  CheckCircle,
} from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState(getActiveRegion().code);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [regionSavedToast, setRegionSavedToast] = useState(false);

  const deleteAllMutation = useDeleteAllScans();
  const resetSamplesMutation = useResetSampleScans();

  const handleRegionChange = (code: string) => {
    setSelectedRegion(code);
    setActiveRegion(code);
    setRegionSavedToast(true);
    setTimeout(() => setRegionSavedToast(false), 2000);
  };

  const handleConfirmClear = () => {
    deleteAllMutation.mutate();
    setShowClearConfirm(false);
  };

  return (
    <div className="space-y-8 max-w-2xl mx-auto py-2">
      {/* Page Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight text-text">
          Settings
        </h1>
        <p className="text-xs sm:text-sm text-text-muted">
          Appearance, regional cyber helpline preferences, and local storage.
        </p>
      </div>

      {/* 1. Appearance / Theming Section */}
      <div className="p-5 rounded-xl bg-surface border border-border/80 space-y-3.5">
        <div className="flex items-center gap-2">
          <Palette className="w-4 h-4 text-text-muted" />
          <h2 className="text-sm font-semibold text-text">Appearance</h2>
        </div>
        <p className="text-xs text-text-muted">
          Choose whether ScamLens follows system preferences or locks to Light or Dark mode.
        </p>
        <ThemeToggle />
      </div>

      {/* 2. Region / Cyber Helpline Section */}
      <div className="p-5 rounded-xl bg-surface border border-border/80 space-y-3.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-text-muted" />
            <h2 className="text-sm font-semibold text-text">Regional Cyber Helpline</h2>
          </div>
          {regionSavedToast && (
            <span className="text-xs text-safe flex items-center gap-1 font-mono">
              <CheckCircle className="w-3.5 h-3.5" /> Saved
            </span>
          )}
        </div>
        <p className="text-xs text-text-muted leading-relaxed">
          Select your region to display official reporting hotlines and government fraud reporting portals on your scan results.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
          {Object.values(SUPPORTED_REGIONS).map((reg) => {
            const isSelected = selectedRegion === reg.code;
            return (
              <button
                key={reg.code}
                onClick={() => handleRegionChange(reg.code)}
                className={`flex items-start justify-between p-3 rounded-lg border text-left transition-colors ${
                  isSelected
                    ? 'border-primary/50 bg-primary/10'
                    : 'border-border/80 bg-surface-2/40 hover:bg-surface-2'
                }`}
              >
                <div>
                  <div className="text-xs sm:text-sm font-medium text-text">{reg.name}</div>
                  <div className="text-xs text-text-muted mt-0.5 font-mono">
                    {reg.helpline ? `Helpline: ${reg.helpline}` : reg.portalName}
                  </div>
                </div>
                {isSelected && (
                  <span className="w-2 h-2 rounded-full bg-primary mt-1 shrink-0" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Data & Privacy Section */}
      <div className="p-5 rounded-xl bg-surface border border-border/80 space-y-3.5">
        <div className="flex items-center gap-2">
          <Lock className="w-4 h-4 text-text-muted" />
          <h2 className="text-sm font-semibold text-text">Privacy &amp; Data Storage</h2>
        </div>

        <div className="space-y-2 text-xs text-text-muted leading-relaxed">
          <p>
            &bull; <strong className="text-text">Local Storage:</strong> Scan history is saved strictly in your browser&apos;s local storage.
          </p>
          <p>
            &bull; <strong className="text-text">Zero Telemetry:</strong> ScamLens does not track users, serve ads, or sell data.
          </p>
          <p>
            &bull; <strong className="text-text">Safe Processing:</strong> Analyzed links are parsed in memory and never executed or loaded in your browser.
          </p>
        </div>

        <div className="pt-3 flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 border-t border-border/60">
          <Button
            variant="ghost"
            size="sm"
            icon={<Trash2 className="w-3.5 h-3.5 text-danger" />}
            onClick={() => setShowClearConfirm(true)}
            className="text-danger hover:bg-danger/10"
          >
            Clear local history
          </Button>

          <Button
            variant="ghost"
            size="sm"
            icon={<RotateCcw className="w-3.5 h-3.5" />}
            onClick={() => resetSamplesMutation.mutate()}
          >
            Reset sample scans
          </Button>
        </div>
      </div>

      {/* App & Version Info */}
      <div className="text-center text-xs text-text-muted space-y-1">
        <p className="font-semibold text-text">ScamLens v2.2.0 (LeanInHack Hackathon)</p>
        <p>Built with React 18, TypeScript, Tailwind CSS &amp; Calibrated AI</p>
      </div>

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={showClearConfirm}
        title="Clear Local History"
        description="This will permanently delete all scan records and statistics saved in your browser. You can reload sample mock scans anytime."
        confirmLabel="Clear Data"
        isDestructive
        onConfirm={handleConfirmClear}
        onCancel={() => setShowClearConfirm(false)}
      />
    </div>
  );
};
