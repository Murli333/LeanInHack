import React, { useRef } from 'react';
import { Clipboard, Trash2 } from 'lucide-react';

export interface TextPanelProps {
  value: string;
  onChange: (val: string) => void;
  maxLength?: number;
  className?: string;
}

export const TextPanel: React.FC<TextPanelProps> = ({
  value,
  onChange,
  maxLength = 10000,
  className = '',
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        onChange(text.slice(0, maxLength));
        if (textareaRef.current) {
          textareaRef.current.focus();
        }
      }
    } catch {
      // If clipboard access is blocked, focus textarea so user can Ctrl+V
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  };

  const handleClear = () => {
    onChange('');
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Navy card container */}
      <div className="relative rounded-card-lg border border-border bg-surface-2 focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20 transition-all p-4 flex flex-col min-h-[220px]">
        <label htmlFor="text-scan-input" className="sr-only">
          Paste the suspicious message here
        </label>
        <textarea
          id="text-scan-input"
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
          placeholder="Paste the suspicious message here..."
          className="w-full flex-1 bg-transparent text-text placeholder:text-text-muted/60 text-sm sm:text-base resize-none focus:outline-none min-h-[140px] leading-relaxed"
          maxLength={maxLength}
        />

        {/* Bottom card actions */}
        <div className="flex items-center justify-between pt-3 border-t border-border/50">
          <button
            type="button"
            onClick={handlePaste}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-surface text-text border border-border hover:bg-surface/80 transition-all"
          >
            <Clipboard className="w-3.5 h-3.5 text-text-muted" />
            <span>Paste</span>
          </button>

          <div className="flex items-center gap-3">
            <span className="text-xs text-text-muted font-mono">
              {value.length.toLocaleString()} / {maxLength.toLocaleString()}
            </span>

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
      </div>

      {/* Helper line below card */}
      <p className="text-xs text-text-muted px-1">
        Up to 10,000 letters. Do not share passwords or PINs.
      </p>
    </div>
  );
};
