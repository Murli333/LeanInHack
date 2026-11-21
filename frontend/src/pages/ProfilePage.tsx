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
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-text">
          Profile &amp; Settings
        </h1>
        <p className="text-xs sm:text-sm text-text-muted">
          Manage appearance, regional cyber helpline settings, and privacy preferences.
        </p>
      </div>

      {/* 1. Appearance / Theming Section */}
      <div className="p-6 rounded-card-lg bg-surface border border-border shadow-card-soft space-y-4">
        <div className="flex items-center gap-2.5">
          <Palette className="w-5 h-5 text-primary" />
          <h2 className="text-base font-bold text-text">Appearance</h2>
        </div>
        <p className="text-xs sm:text-sm text-text-muted">
          Choose whether ScamLens follows your device theme or locks to Light or Dark mode.
        </p>
        <ThemeToggle />
      </div>

      {/* 2. Region / Cyber Helpline Section */}
      <div className="p-6 rounded-card-lg bg-surface border border-border shadow-card-soft space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Globe className="w-5 h-5 text-accent" />
            <h2 className="text-base font-bold text-text">Regional Cyber Helpline</h2>
          </div>
          {regionSavedToast && (
            <span className="text-xs font-semibold text-safe flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> Saved
            </span>
          )}
        </div>
        <p className="text-xs sm:text-sm text-text-muted leading-relaxed">
          Select your country to display official reporting hotlines and government fraud reporting portals on your scan results.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          {Object.values(SUPPORTED_REGIONS).map((reg) => {
            const isSelected = selectedRegion === reg.code;
            return (
              <button
                key={reg.code}
                onClick={() => handleRegionChange(reg.code)}
                className={`flex items-start justify-between p-3.5 rounded-card border text-left transition-all ${
                  isSelected
                    ? 'border-primary bg-primary/10 ring-1 ring-primary'
                    : 'border-border bg-surface-2 hover:bg-surface'
                }`}
              >
                <div>
                  <div className="text-sm font-semibold text-text">{reg.name}</div>
                  <div className="text-xs text-text-muted mt-0.5">
                    {reg.helpline ? `Helpline: ${reg.helpline}` : reg.portalName}
                  </div>
                </div>
                {isSelected && (
                  <span className="w-2.5 h-2.5 rounded-full bg-primary mt-1 shrink-0" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Data & Privacy Section */}
      <div className="p-6 rounded-card-lg bg-surface border border-border shadow-card-soft space-y-4">
        <div className="flex items-center gap-2.5">
          <Lock className="w-5 h-5 text-safe" />
          <h2 className="text-base font-bold text-text">Privacy &amp; Data Storage</h2>
        </div>

        <div className="space-y-3 text-xs sm:text-sm text-text-muted leading-relaxed">
          <p>
            &bull; <strong>Local Processing:</strong> Scan history is kept strictly in your local device browser storage.
          </p>
          <p>
            &bull; <strong>Zero Ad Telemetry:</strong> ScamLens does not track users across websites, display ads, or sell data.
          </p>
          <p>
            &bull; <strong>Safe Link Handling:</strong> URLs submitted for checking are evaluated via server-side structural analysis and threat feeds; they are never opened in your browser.
          </p>
        </div>

        <div className="pt-3 flex flex-col sm:flex-row items-stretch sm:items-center gap-3 border-t border-border">
          <Button
            variant="ghost"
            size="md"
            icon={<Trash2 className="w-4 h-4 text-danger" />}
            onClick={() => setShowClearConfirm(true)}
            className="text-danger hover:bg-danger-tint"
          >
            Clear all scan history
          </Button>

          <Button
            variant="ghost"
            size="md"
            icon={<RotateCcw className="w-4 h-4" />}
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
