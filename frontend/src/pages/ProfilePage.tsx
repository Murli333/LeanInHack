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
  Palette,
  Globe,
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
    <div className="space-y-6 max-w-2xl mx-auto py-2">
      {/* Page Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-medium tracking-tight text-text">
          Settings
        </h1>
        <p className="text-xs sm:text-sm text-text-secondary">
          Appearance, regional cyber helpline preferences, and local storage.
        </p>
      </div>

      {/* 1. Appearance / Theming Section */}
      <div className="p-5 rounded-card bg-surface border border-border space-y-3">
        <div className="flex items-center gap-2">
          <Palette className="w-4 h-4 text-text-muted" />
          <h2 className="text-xs font-medium text-text uppercase tracking-wider">Appearance</h2>
        </div>
        <p className="text-xs text-text-secondary">
          Choose between dark surface tones or light clean theme.
        </p>
        <ThemeToggle />
      </div>

      {/* 2. Region / Cyber Helpline Section */}
      <div className="p-5 rounded-card bg-surface border border-border space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-text-muted" />
            <h2 className="text-xs font-medium text-text uppercase tracking-wider">Regional Cyber Helpline</h2>
          </div>
          {regionSavedToast && (
            <span className="text-xs text-safe flex items-center gap-1 font-mono">
              <CheckCircle className="w-3.5 h-3.5" /> Saved
            </span>
          )}
        </div>
        <p className="text-xs text-text-secondary leading-relaxed">
          Select your region to configure official incident reporting hotlines and portals on verification reports.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
          {Object.values(SUPPORTED_REGIONS).map((reg) => {
            const isSelected = selectedRegion === reg.code;
            return (
              <button
                key={reg.code}
                onClick={() => handleRegionChange(reg.code)}
                className={`flex items-start justify-between p-3 rounded-button border text-left transition-colors ${
                  isSelected
                    ? 'border-accent/60 bg-accent/10'
                    : 'border-border bg-surface-raised hover:bg-surface'
                }`}
              >
                <div>
                  <div className="text-xs font-medium text-text">{reg.name}</div>
                  <div className="text-2xs text-text-muted mt-0.5 font-mono">
                    {reg.helpline ? `Helpline: ${reg.helpline}` : reg.portalName}
                  </div>
                </div>
                {isSelected && (
                  <span className="w-2 h-2 rounded-full bg-accent mt-1 shrink-0" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Data & Privacy Section */}
      <div className="p-5 rounded-card bg-surface border border-border space-y-3">
        <div className="flex items-center gap-2">
          <Lock className="w-4 h-4 text-text-muted" />
          <h2 className="text-xs font-medium text-text uppercase tracking-wider">Privacy &amp; Data Storage</h2>
        </div>

        <div className="space-y-1.5 text-xs text-text-secondary leading-relaxed">
          <p>
            &bull; <span className="text-text font-medium">Local Storage:</span> Verification logs are kept strictly in your browser session/storage.
          </p>
          <p>
            &bull; <span className="text-text font-medium">Zero Telemetry:</span> ScamLens does not track users or collect personal credentials.
          </p>
          <p>
            &bull; <span className="text-text font-medium">Safe Processing:</span> Analyzed URLs are parsed structurally and never triggered or opened.
          </p>
        </div>

        <div className="pt-3 flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 border-t border-border">
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
      <div className="text-center text-2xs text-text-muted space-y-0.5">
        <p className="font-mono text-text">ScamLens v2.2.0 (LeanInHack Hackathon)</p>
        <p>Built with React 18, TypeScript, Tailwind CSS &amp; Calibrated Threat Engine</p>
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
