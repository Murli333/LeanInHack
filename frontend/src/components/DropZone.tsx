import React, { useRef, useState } from 'react';
import { Image as ImageIcon, UploadCloud, CheckCircle, XCircle } from 'lucide-react';
import { FEATURES } from '../config/flags';
import { ComingSoonPanel } from './ComingSoonPanel';
import { Button } from './Button';

export interface DropZoneProps {
  onFileSelect?: (file: File | null) => void;
  className?: string;
}

export const DropZone: React.FC<DropZoneProps> = ({ onFileSelect, className = '' }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // HONESTY RULE 1: If feature flag is off, show calm Coming Soon panel
  if (!FEATURES.screenshot) {
    return (
      <ComingSoonPanel
        title="Screenshot analysis coming soon"
        description="Our optical character recognition (OCR) and multimodal fraud verification models are undergoing safety evaluations."
        featureName="Screenshot OCR"
        className={className}
      />
    );
  }

  const validateAndSetFile = (file: File) => {
    setError(null);
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Please select a valid image (JPEG, PNG, or WebP).');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10 MB limit.');
      return;
    }
    setSelectedFile(file);
    onFileSelect?.(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setError(null);
    onFileSelect?.(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className={`space-y-3 ${className}`}>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`rounded-card-lg border-2 border-dashed p-8 text-center space-y-4 transition-all ${
          isDragging
            ? 'border-accent bg-accent/10'
            : selectedFile
            ? 'border-safe/50 bg-safe-tint/20'
            : 'border-border bg-surface-2 hover:border-text-muted/40'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png, image/jpeg, image/webp"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              validateAndSetFile(e.target.files[0]);
            }
          }}
        />

        {selectedFile ? (
          <div className="space-y-3">
            <div className="w-14 h-14 rounded-full bg-safe/20 text-safe flex items-center justify-center mx-auto">
              <CheckCircle className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm font-semibold text-text">{selectedFile.name}</p>
              <p className="text-xs text-text-muted">
                {(selectedFile.size / 1024).toFixed(1)} KB &bull; Ready for check
              </p>
            </div>
            <Button variant="secondary" size="sm" onClick={handleClear}>
              Remove image
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-surface border border-border text-primary flex items-center justify-center mx-auto shadow-sm">
              <UploadCloud className="w-8 h-8 text-primary" />
            </div>

            <div className="space-y-1">
              <h3 className="text-base sm:text-lg font-bold text-text">
                Upload a screenshot
              </h3>
              <p className="text-xs sm:text-sm text-text-muted max-w-sm mx-auto">
                Choose a screenshot of any message, WhatsApp, or email.
              </p>
            </div>

            <div>
              <Button
                variant="primary"
                size="md"
                icon={<ImageIcon className="w-4 h-4" />}
                onClick={() => fileInputRef.current?.click()}
              >
                Select from Photos
              </Button>
            </div>

            <p className="text-xs text-text-muted">
              Supports JPEG, PNG, or WebP up to 10 MB. Private &amp; secure.
            </p>
          </div>
        )}
      </div>

      {error && (
        <p className="text-xs text-danger flex items-center gap-1.5 px-1">
          <XCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{error}</span>
        </p>
      )}
    </div>
  );
};
