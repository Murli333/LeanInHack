import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  MessageSquare,
  Link2,
  Image as ImageIcon,
  QrCode,
  Mic,
  Search,
  Lock,
  AlertCircle,
  Loader2,
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

type ScanLifecycle = 'IDLE' | 'VALIDATING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export const ScanPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialType = (searchParams.get('type') as ScanType) || 'text';

  const [activeType, setActiveType] = useState<ScanType>(initialType);
  const [textContent, setTextContent] = useState('');
  const [urlContent, setUrlContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Robust state machine
  const [lifecycle, setLifecycle] = useState<ScanLifecycle>('IDLE');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const isSubmittingRef = useRef(false);

  const createScanMutation = useCreateScan();

  // Validate current active input
  const validateInput = (): { valid: boolean; error?: string } => {
    switch (activeType) {
      case 'text':
        if (!textContent.trim()) {
          return { valid: false, error: 'Please enter or paste a message to scan.' };
        }
        return { valid: true };
      case 'url':
        if (!urlContent.trim()) {
          return { valid: false, error: 'Please enter a URL to check.' };
        }
        try {
          const u = new URL(urlContent.trim());
          if (u.protocol !== 'http:' && u.protocol !== 'https:') {
            return { valid: false, error: 'URL must begin with http:// or https://' };
          }
          return { valid: true };
        } catch {
          return { valid: false, error: 'Please enter a valid, complete web address.' };
        }
      case 'screenshot':
        if (!FEATURES.screenshot) {
          return { valid: false, error: 'Screenshot scanning is coming soon.' };
        }
        if (!selectedFile) {
          return { valid: false, error: 'Please select an image file to upload.' };
        }
        return { valid: true };
      case 'qr':
        return { valid: false, error: 'QR code inspection is coming soon.' };
      case 'audio':
        return { valid: false, error: 'Audio scanning is coming soon.' };
      default:
        return { valid: false, error: 'Unsupported scan type.' };
    }
  };

  const isFormValid = validateInput().valid;

  const handleSubmit = async () => {
    // Prevent duplicate submissions from rapid repeated clicks
    if (isSubmittingRef.current || lifecycle === 'PROCESSING' || createScanMutation.isPending) {
      return;
    }

    setErrorMessage(null);
    setLifecycle('VALIDATING');

    const validation = validateInput();
    if (!validation.valid) {
      setLifecycle('IDLE');
      setErrorMessage(validation.error || 'Please provide valid input.');
      return;
    }

    // Set lock
    isSubmittingRef.current = true;
    setLifecycle('PROCESSING');

    let payloadContent = '';
    if (activeType === 'text') payloadContent = textContent.trim();
    else if (activeType === 'url') payloadContent = urlContent.trim();
    else if (activeType === 'screenshot' && selectedFile) payloadContent = selectedFile.name;

    try {
      const res = await createScanMutation.mutateAsync({
        type: activeType,
        content: payloadContent,
      });

      setLifecycle('COMPLETED');
      // Navigate to progress stepper
      navigate(`/scan/${res.id}/progress`);
    } catch (err: any) {
      isSubmittingRef.current = false;
      setLifecycle('FAILED');
      setErrorMessage(err?.message || 'Failed to submit scan request. Please try again.');
    }
  };

  // Keyboard shortcut: Ctrl/Cmd + Enter to submit
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (isFormValid && lifecycle !== 'PROCESSING') {
          e.preventDefault();
          handleSubmit();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFormValid, lifecycle, activeType, textContent, urlContent, selectedFile]);

  // Clean inputs on unmount / navigation
  useEffect(() => {
    return () => {
      isSubmittingRef.current = false;
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
        <h1 className="text-2xl font-semibold tracking-tight text-text">
          New verification
        </h1>
        <p className="text-xs sm:text-sm text-text-muted">
          Select an input format below and submit for immediate verification.
        </p>
      </div>

      {/* Error banner if submission or validation failed */}
      {errorMessage && (
        <div
          role="alert"
          className="p-3.5 rounded-xl bg-danger/10 border border-danger/25 text-danger text-sm flex items-start gap-2.5 animate-fade-in"
        >
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-medium block text-xs uppercase tracking-wider">Submission Error</span>
            <span className="text-xs sm:text-sm">{errorMessage}</span>
          </div>
        </div>
      )}

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
              onClick={() => {
                setActiveType(c.type);
                setErrorMessage(null);
                setLifecycle('IDLE');
              }}
            />
          ))}
        </div>
      </div>

      {/* Responsive Two-Column Layout on Desktop (>=1024px) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (Input Panel + Submit) */}
        <div className="lg:col-span-7 space-y-6">
          {activeType === 'text' && (
            <TextPanel
              value={textContent}
              onChange={(v) => {
                setTextContent(v);
                if (errorMessage) setErrorMessage(null);
              }}
            />
          )}

          {activeType === 'url' && (
            <UrlField
              value={urlContent}
              onChange={(v) => {
                setUrlContent(v);
                if (errorMessage) setErrorMessage(null);
              }}
            />
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
              disabled={!isFormValid || lifecycle === 'PROCESSING' || createScanMutation.isPending}
              icon={
                lifecycle === 'PROCESSING' ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )
              }
              onClick={handleSubmit}
            >
              {lifecycle === 'PROCESSING' || createScanMutation.isPending
                ? 'Starting scan...'
                : 'Check now'}
            </Button>
            <p className="text-center text-[11px] text-text-muted mt-2 hidden lg:block">
              Tip: Press <kbd className="px-1.5 py-0.5 rounded bg-surface-2 border border-border/80 text-xs font-mono">Ctrl + Enter</kbd> to submit
            </p>
          </div>
        </div>

        {/* Right Column on Desktop: How It Works & Privacy Notes */}
        <div className="lg:col-span-5 space-y-4">
          <div className="p-4 rounded-xl bg-surface border border-border/80 space-y-3">
            <h3 className="text-xs font-medium text-text-muted uppercase tracking-wider">
              Verification process
            </h3>
            <ul className="space-y-2.5 text-xs text-text leading-relaxed">
              <li className="flex items-start gap-2.5">
                <span className="w-4 h-4 rounded-full bg-surface-2 text-text-muted text-[10px] font-mono flex items-center justify-center shrink-0 mt-0.5">
                  1
                </span>
                <span>Extracts text, structural links, and urgency indicators.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="w-4 h-4 rounded-full bg-surface-2 text-text-muted text-[10px] font-mono flex items-center justify-center shrink-0 mt-0.5">
                  2
                </span>
                <span>Compares with confirmed phishing databases and calibrated models.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="w-4 h-4 rounded-full bg-surface-2 text-text-muted text-[10px] font-mono flex items-center justify-center shrink-0 mt-0.5">
                  3
                </span>
                <span>Delivers a qualitative risk badge and actionable safety steps.</span>
              </li>
            </ul>
          </div>

          <div className="p-3.5 rounded-xl bg-surface border border-border/80 flex items-start gap-2.5 text-xs text-text-muted leading-relaxed">
            <Lock className="w-3.5 h-3.5 text-text-muted shrink-0 mt-0.5" />
            <div>
              <span className="text-text font-medium">Safe processing:</span> Input is evaluated in volatile memory and never navigated to directly.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
