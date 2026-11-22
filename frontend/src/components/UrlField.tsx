import React, { useRef, useState } from 'react';
import { Link2, Clipboard, Trash2, AlertCircle } from 'lucide-react';

export interface UrlFieldProps {
  value: string;
  onChange: (val: string) => void;
  className?: string;
}

export const UrlField: React.FC<UrlFieldProps> = ({ value, onChange, className = '' }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [touched, setTouched] = useState(false);

  const isValidUrl = (val: string) => {
    if (!val.trim()) return false;
    try {
      const u = new URL(val.trim());
      return u.protocol === 'http:' || u.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const hasError = touched && value.trim().length > 0 && !isValidUrl(value);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        onChange(text.trim());
        setTouched(true);
        if (inputRef.current) inputRef.current.focus();
      }
    } catch {
      if (inputRef.current) inputRef.current.focus();
    }
  };

  const handleClear = () => {
    onChange('');
    setTouched(false);
    if (inputRef.current) inputRef.current.focus();
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <div
        className={`rounded-xl border bg-surface p-4 transition-colors ${
          hasError
            ? 'border-danger focus-within:border-danger'
            : 'border-border/80 focus-within:border-primary/50'
        }`}
      >
        <div className="flex items-center gap-3">
          <Link2 className="w-4 h-4 text-text-muted shrink-0" />
          <label htmlFor="url-scan-input" className="sr-only">
            Paste the suspicious link here
          </label>
          <input
            id="url-scan-input"
            ref={inputRef}
            type="url"
            value={value}
            onChange={(e) => {
              onChange(e.target.value);
              setTouched(true);
            }}
            placeholder="https://example.com/login"
            className="w-full bg-transparent text-text placeholder:text-text-muted/40 text-sm focus:outline-none font-mono"
            autoCapitalize="none"
            autoCorrect="off"
            spellCheck="false"
          />
        </div>

        <div className="flex items-center justify-between pt-3 mt-3 border-t border-border/50">
          <button
            type="button"
            onClick={handlePaste}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-surface-2 text-text border border-border/70 hover:bg-surface-2/80 transition-colors"
          >
            <Clipboard className="w-3.5 h-3.5 text-text-muted" />
            <span>Paste Link</span>
          </button>

          {value.length > 0 && (
            <button
              type="button"
              onClick={handleClear}
              className="inline-flex items-center gap-1 text-xs text-text-muted hover:text-danger transition-colors font-medium"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {hasError ? (
        <p className="text-xs text-danger flex items-center gap-1 px-1">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>Please enter a complete URL starting with http:// or https://</span>
        </p>
      ) : (
        <p className="text-xs text-text-muted px-1">
          Paste the full link. We will not open it or connect to it from your browser.
        </p>
      )}
    </div>
  );
};
