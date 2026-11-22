import React, { useRef } from 'react';
import { Clipboard, Trash2, Lock } from 'lucide-react';

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
      {/* Filled input container with hairline border */}
      <div className="relative rounded-card border border-border bg-surface-raised focus-within:border-accent/80 transition-colors p-4 flex flex-col min-h-[220px]">
        <label htmlFor="text-scan-input" className="sr-only">
          Paste the message here
        </label>
        <textarea
          id="text-scan-input"
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
          placeholder="Paste suspicious SMS, WhatsApp message, email, or text to verify..."
          className="w-full flex-1 bg-transparent text-text placeholder:text-text-muted text-sm resize-none focus:outline-none min-h-[140px] leading-relaxed font-sans"
          maxLength={maxLength}
        />

        {/* Bottom card actions */}
        <div className="flex items-center justify-between pt-3 border-t border-border">
          <button
            type="button"
            onClick={handlePaste}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-button text-xs font-medium bg-surface text-text-secondary border border-border hover:text-text hover:bg-surface-raised transition-colors"
          >
            <Clipboard className="w-3.5 h-3.5" />
            <span>Paste</span>
          </button>

          <div className="flex items-center gap-3">
            <span className="text-xs text-text-muted font-mono tabular-nums">
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

      {/* Security note */}
      <div className="flex items-center gap-1.5 text-xs text-text-muted px-1">
        <Lock className="w-3.5 h-3.5 text-text-muted shrink-0" />
        <span>Private verification. Passwords and personal PINs are never requested or stored.</span>
      </div>
    </div>
  );
};
