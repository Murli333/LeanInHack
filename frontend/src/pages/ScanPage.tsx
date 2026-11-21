import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  MessageSquare,
  Link2,
  Image as ImageIcon,
  QrCode,
  Mic,
  Search,
  Lock,
  Info,
} from 'lucide-react';
import { ScanType } from '../types';
import { FEATURES } from '../config/flags';
import { Chip } from '../components/Chip';
import { TextPanel } from '../components/TextPanel';
import { UrlField } from '../components/UrlField';
import { DropZone } from '../components/DropZone';
import { ComingSoonPanel } from '../components/ComingSoonPanel';
import { Button } from '../components/Button';
import { useCreateScan } from '../hooks/useScans';

export const ScanPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialType = (searchParams.get('type') as ScanType) || 'text';

  const [activeType, setActiveType] = useState<ScanType>(initialType);
  const [textContent, setTextContent] = useState('');
  const [urlContent, setUrlContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const createScanMutation = useCreateScan();

  // Validate current active input
  const isValid = (() => {
    switch (activeType) {
      case 'text':
        return textContent.trim().length > 0;
      case 'url':
        if (!urlContent.trim()) return false;
        try {
          const u = new URL(urlContent.trim());
          return u.protocol === 'http:' || u.protocol === 'https:';
        } catch {
          return false;
        }
      case 'screenshot':
        return Boolean(FEATURES.screenshot && selectedFile);
      case 'qr':
        return Boolean(FEATURES.qr);
      case 'audio':
        return Boolean(FEATURES.audio);
      default:
        return false;
    }
  })();

  const handleSubmit = async () => {
    if (!isValid || createScanMutation.isPending) return;

    let payloadContent = '';
    if (activeType === 'text') payloadContent = textContent.trim();
    else if (activeType === 'url') payloadContent = urlContent.trim();
    else if (activeType === 'screenshot' && selectedFile) payloadContent = selectedFile.name;

    try {
      const res = await createScanMutation.mutateAsync({
        type: activeType,
        content: payloadContent,
      });
      // Navigate to progress stepper
      navigate(`/scan/${res.id}/progress`);
    } catch {
      // Error handling
    }
  };

  // Keyboard shortcut: Ctrl/Cmd + Enter to submit
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (isValid) {
          e.preventDefault();
          handleSubmit();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isValid, activeType, textContent, urlContent, selectedFile]);

  // Clean inputs on unmount / navigation
  useEffect(() => {
    return () => {
      setTextContent('');
      setUrlContent('');
      setSelectedFile(null);
    };
  }, []);

  const chips: { type: ScanType; label: string; icon: React.ReactNode; soon: boolean }[] = [
    { type: 'text', label: 'Text', icon: <MessageSquare className="w-4 h-4" />, soon: false },
    { type: 'url', label: 'Link', icon: <Link2 className="w-4 h-4" />, soon: false },
    {
      type: 'screenshot',
      label: 'Screenshot',
      icon: <ImageIcon className="w-4 h-4" />,
      soon: !FEATURES.screenshot,
    },
    {
      type: 'qr',
      label: 'QR Code',
      icon: <QrCode className="w-4 h-4" />,
      soon: !FEATURES.qr,
    },
    {
      type: 'audio',
      label: 'Audio',
      icon: <Mic className="w-4 h-4" />,
      soon: !FEATURES.audio,
    },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto py-2">
      {/* Title */}
      <div className="space-y-1">
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-text">
          What would you like to check?
        </h1>
        <p className="text-xs sm:text-sm text-text-muted">
          Select an input format below and submit for instant verification.
        </p>
      </div>

      {/* Horizontally Scrollable Chips with Fade Edge */}
      <div className="relative">
        <div
          className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none"
          role="tablist"
          aria-label="Input types"
        >
          {chips.map((c) => (
            <Chip
              key={c.type}
              label={c.label}
              icon={c.icon}
              selected={activeType === c.type}
              soon={c.soon}
              onClick={() => setActiveType(c.type)}
            />
          ))}
        </div>
      </div>

      {/* Responsive Two-Column Layout on Desktop (>=1024px) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (Input Panel + Submit) */}
        <div className="lg:col-span-7 space-y-6">
          {activeType === 'text' && (
            <TextPanel value={textContent} onChange={setTextContent} />
          )}

          {activeType === 'url' && (
            <UrlField value={urlContent} onChange={setUrlContent} />
          )}

          {activeType === 'screenshot' && (
            <DropZone onFileSelect={setSelectedFile} />
          )}

          {activeType === 'qr' && (
            <ComingSoonPanel
              title="QR code inspection coming soon"
              description="Scanning payment and redirection QR codes is in active testing."
              featureName="QR Scanner"
            />
          )}

          {activeType === 'audio' && (
            <ComingSoonPanel
              title="Voice call & audio note check coming soon"
              description="Voice scam audio transcription and digital arrest speech pattern recognition will arrive in a future update."
              featureName="Audio Intelligence"
            />
          )}

          {/* Sticky Check Button on Mobile, Standard on Desktop */}
          <div className="pt-2">
            <Button
              variant="primary"
              size="lg"
              fullWidth
              disabled={!isValid || createScanMutation.isPending}
              icon={<Search className="w-5 h-5" />}
              onClick={handleSubmit}
              className="shadow-md shadow-primary/20"
            >
              {createScanMutation.isPending ? 'Submitting...' : 'Check now'}
            </Button>
            <p className="text-center text-[11px] text-text-muted mt-2 hidden lg:block">
              Tip: Press <kbd className="px-1.5 py-0.5 rounded bg-surface-2 border border-border text-xs">Ctrl + Enter</kbd> to submit
            </p>
          </div>
        </div>

        {/* Right Column on Desktop: How It Works & Privacy Notes */}
        <div className="lg:col-span-5 space-y-5">
          <div className="p-5 rounded-card-lg bg-surface-2 border border-border space-y-3">
            <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">
              HOW IT WORKS
            </h3>
            <ul className="space-y-3 text-xs sm:text-sm text-text leading-relaxed">
              <li className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-primary text-on-primary text-xs font-bold flex items-center justify-center shrink-0">
                  1
                </span>
                <span>Extracts text, structural links, and urgency indicators.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-primary text-on-primary text-xs font-bold flex items-center justify-center shrink-0">
                  2
                </span>
                <span>Compares with confirmed phishing databases and calibrated models.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-primary text-on-primary text-xs font-bold flex items-center justify-center shrink-0">
                  3
                </span>
                <span>Delivers a qualitative risk badge and actionable safety steps.</span>
              </li>
            </ul>
          </div>

          <div className="p-4 rounded-card-lg bg-surface border border-border flex items-start gap-3 text-xs text-text-muted leading-relaxed">
            <Lock className="w-4 h-4 text-primary shrink-0 mt-0.5" />
            <div>
              <strong className="text-text">Safe processing:</strong> Submitted text or URLs are inspected in volatile memory and never navigated to directly.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
