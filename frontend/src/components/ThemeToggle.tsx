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
    { id: 'system', label: 'System', icon: <Monitor className="w-4 h-4" /> },
    { id: 'light', label: 'Light', icon: <Sun className="w-4 h-4" /> },
    { id: 'dark', label: 'Dark', icon: <Moon className="w-4 h-4" /> },
  ];

  return (
    <div className={`space-y-2 ${className}`}>
      <div
        className="inline-flex p-1 rounded-full bg-surface-2 border border-border"
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
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                isSelected
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-text-muted hover:text-text hover:bg-surface/50'
              }`}
            >
              {opt.icon}
              <span>{opt.label}</span>
            </button>
          );
        })}
      </div>
      <p className="text-xs text-text-muted">
        Currently displaying {resolvedTheme === 'dark' ? 'Dark' : 'Light'} mode{' '}
        {themeChoice === 'system' ? '(matching system preference)' : ''}.
      </p>
    </div>
  );
};
