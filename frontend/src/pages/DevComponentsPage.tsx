import React, { useState } from 'react';
import { ThemeToggle } from '../components/ThemeToggle';
import { Button } from '../components/Button';
import { Chip } from '../components/Chip';
import { RiskBadge } from '../components/RiskBadge';
import { RiskMeter } from '../components/RiskMeter';
import { RiskVerdictCard } from '../components/RiskVerdictCard';
import { EvidenceRow } from '../components/EvidenceRow';
import { ActionList } from '../components/ActionList';
import { ProgressStepper } from '../components/ProgressStepper';
import { PartialResultBanner } from '../components/PartialResultBanner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { StatTile } from '../components/StatTile';
import { ScanCard } from '../components/ScanCard';
import { HelplineCard } from '../components/HelplineCard';
import { TextPanel } from '../components/TextPanel';
import { UrlField } from '../components/UrlField';
import { DropZone } from '../components/DropZone';
import { CardSkeleton, Skeleton } from '../components/Skeleton';
import { Toast } from '../components/Toast';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { Search, Sparkles, MessageSquare, Link2, Bell } from 'lucide-react';
import { Scan } from '../types';

export const DevComponentsPage: React.FC = () => {
  const [demoText, setDemoText] = useState('Urgent: your electricity will be disconnected tonight at 9:30 PM.');
  const [demoUrl, setDemoUrl] = useState('https://sbi-netbanking-verify.xyz/login');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [showToast, setShowToast] = useState(true);

  const sampleScan: Scan = {
    id: 'demo-scan-1',
    type: 'text',
    title: 'Urgent Electricity cutoff threat',
    content: demoText,
    createdAt: new Date().toISOString(),
    status: 'completed',
    steps: [],
    result: {
      riskLevel: 'high',
      summary: 'Threatens power disconnection to induce panic and extract immediate bill payment.',
      score: 88,
      scoreValidated: true,
      category: 'Utility Scam',
      evidence: [],
      actions: [],
    },
  };

  const sampleEvidence = [
    {
      id: 'e1',
      title: 'Known phishing database match',
      kind: 'confirmed' as const,
      detail: 'Verified match on OpenPhish active feed.',
      source: 'OpenPhish',
    },
    {
      id: 'e2',
      title: 'High-pressure urgency indicators',
      kind: 'warning' as const,
      detail: 'Threatens service suspension within hours.',
      source: 'Heuristics',
    },
    {
      id: 'e3',
      title: 'Domain reputation lookup skipped',
      kind: 'not_run' as const,
      detail: 'No URL detected in submitted message.',
      source: 'Content Analyzer',
    },
  ];

  return (
    <div className="space-y-12 max-w-4xl mx-auto py-6">
      {/* Top Banner with Theme Switcher */}
      <div className="p-6 rounded-card-lg bg-surface border border-border shadow-card-soft space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-text">
              ScamLens Component Design Gallery
            </h1>
            <p className="text-xs text-text-muted mt-1">
              Test every UI component across Light and Dark themes, states, and responsive viewports.
            </p>
          </div>
          <ThemeToggle />
        </div>
      </div>

      {/* 1. Buttons */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          1. Buttons (Pill &amp; Responsive Touch Targets)
        </h2>
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="primary" size="md">
            Primary Button
          </Button>
          <Button variant="primary" size="lg" icon={<Search className="w-5 h-5" />}>
            Check now (Large)
          </Button>
          <Button variant="secondary" size="md">
            Secondary Button
          </Button>
          <Button variant="ghost" size="md">
            Ghost Button
          </Button>
          <Button variant="destructive" size="md">
            Destructive
          </Button>
          <Button variant="primary" size="md" disabled>
            Disabled Button
          </Button>
        </div>
      </section>

      {/* 2. Chips */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          2. Filter &amp; Format Chips
        </h2>
        <div className="flex flex-wrap items-center gap-2">
          <Chip label="Text" icon={<MessageSquare className="w-4 h-4" />} selected />
          <Chip label="Link" icon={<Link2 className="w-4 h-4" />} />
          <Chip label="Screenshot" soon />
          <Chip label="QR Code" soon />
          <Chip label="Audio" soon />
        </div>
      </section>

      {/* 3. Risk Badges & Meters */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          3. Plain-Language Risk Badges &amp; 3-Segment Qualitative Meter
        </h2>
        <div className="flex flex-wrap items-center gap-3">
          <RiskBadge level="high" />
          <RiskBadge level="medium" />
          <RiskBadge level="low" />
          <RiskBadge level="unknown" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <div className="p-4 rounded-card bg-surface-2 border border-border space-y-2">
            <span className="text-xs font-semibold text-text">Validated Score Display:</span>
            <RiskMeter level="high" score={92} scoreValidated={true} />
          </div>
          <div className="p-4 rounded-card bg-surface-2 border border-border space-y-2">
            <span className="text-xs font-semibold text-text">Qualitative Only (No fake %):</span>
            <RiskMeter level="medium" scoreValidated={false} />
          </div>
        </div>
      </section>

      {/* 4. Verdict Cards */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          4. High-Threat Verdict Card (Red Glow in Dark, Soft Tint in Light)
        </h2>
        <RiskVerdictCard
          level="high"
          summary="Fake bank message asking for your OTP or login credentials."
          score={92}
          scoreValidated={true}
          category="Banking Fraud"
        />
      </section>

      {/* 5. Evidence Rows */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          5. Evidence Rows (CONFIRMED / WARNING SIGN / NOT RUN)
        </h2>
        <div className="space-y-2.5">
          {sampleEvidence.map((ev) => (
            <EvidenceRow key={ev.id} evidence={ev} />
          ))}
        </div>
      </section>

      {/* 6. Action List */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          6. Stay Safe Action List &amp; Regional Helpline
        </h2>
        <ActionList
          actions={[
            'Do not click the link or reply to this sender',
            'Do not share your OTP, PIN, or net banking password',
            'Verify through official customer support channels',
          ]}
        />
      </section>

      {/* 7. Progress Stepper */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          7. Progress Stepper (5 Steps: Completed, In Progress, Waiting, Failed)
        </h2>
        <div className="p-6 rounded-card bg-surface border border-border">
          <ProgressStepper
            steps={[
              { key: '1', label: 'Extract content', status: 'completed' },
              { key: '2', label: 'Check patterns', status: 'completed' },
              { key: '3', label: 'Check URL reputation', status: 'running' },
              { key: '4', label: 'Combine evidence', status: 'waiting' },
              { key: '5', label: 'Prepare report', status: 'waiting' },
            ]}
          />
        </div>
      </section>

      {/* 8. Input Panels */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          8. Input Panels (Text, URL, Screenshot DropZone)
        </h2>
        <TextPanel value={demoText} onChange={setDemoText} />
        <UrlField value={demoUrl} onChange={setDemoUrl} />
        <DropZone />
      </section>

      {/* 9. Feedback States */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          9. Feedback &amp; Warning States
        </h2>
        <PartialResultBanner message="Threat intelligence database was unreachable. Results reflect rule checks only." />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <EmptyState
            title="Empty state demo"
            description="Clear explanation when no data is available."
          />
          <ErrorState
            title="Error state demo"
            message="Clear recovery path for network interruptions."
          />
        </div>
      </section>

      {/* 10. Scan Card & Stat Tiles */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          10. Scan Card &amp; Stat Tiles
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <StatTile value={12} label="checks done" />
          <StatTile value={3} label="high-risk found" />
        </div>
        <ScanCard scan={sampleScan} onClick={() => alert('Clicked sample scan')} />
      </section>

      {/* 11. Skeletons */}
      <section className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          11. Skeleton Loading States
        </h2>
        <CardSkeleton />
      </section>

      {/* 12. Dialog Trigger */}
      <section className="space-y-4 pb-8">
        <h2 className="text-sm font-bold uppercase tracking-wider text-text-muted border-b border-border pb-2">
          12. Dialogs &amp; Toasts
        </h2>
        <div className="flex items-center gap-3">
          <Button variant="secondary" size="md" onClick={() => setConfirmOpen(true)}>
            Open Confirm Dialog Demo
          </Button>
          {showToast && (
            <Toast
              id="demo-toast"
              type="success"
              message="Theme applied and stored in localStorage."
              onClose={() => setShowToast(false)}
            />
          )}
        </div>
        <ConfirmDialog
          isOpen={confirmOpen}
          title="Confirm Action"
          description="Are you sure you want to proceed with this demonstration action?"
          onConfirm={() => setConfirmOpen(false)}
          onCancel={() => setConfirmOpen(false)}
        />
      </section>
    </div>
  );
};
