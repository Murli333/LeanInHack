import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../theme/useTheme';
import { ThemeChoice } from '../types';

interface ThemeToggleProps {
  className?: string;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '' }) => {
  const { themeChoice, resolvedTheme, setTheme } = useTheme();

  const options: { id: ThemeChoice; label: string; icon: React.ReactNode }[] = [
    { id: 'system', label: 'System', icon: <Monitor className="w-3.5 h-3.5" /> },
    { id: 'light', label: 'Light', icon: <Sun className="w-3.5 h-3.5" /> },
    { id: 'dark', label: 'Dark', icon: <Moon className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className={`space-y-2 ${className}`}>
      <div
        className="inline-flex p-0.5 rounded-button bg-surface-raised border border-border"
        role="radiogroup"
        aria-label="Theme mode"
      >
        {options.map((opt) => {
          const isSelected = themeChoice === opt.id;
          return (
            <button
              key={opt.id}
              type="button"
              role="radio"
              aria-checked={isSelected}
              onClick={() => setTheme(opt.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-button text-xs font-medium transition-colors ${
                isSelected
                  ? 'bg-surface text-text border border-border'
                  : 'text-text-muted hover:text-text'
              }`}
            >
              {opt.icon}
              <span>{opt.label}</span>
            </button>
          );
        })}
      </div>
      <p className="text-2xs text-text-muted font-mono">
        Active theme: {resolvedTheme === 'dark' ? 'Dark' : 'Light'}{' '}
        {themeChoice === 'system' ? '(System synced)' : ''}
      </p>
    </div>
  );
};
