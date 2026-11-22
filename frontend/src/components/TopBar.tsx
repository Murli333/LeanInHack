import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, ChevronLeft, Sun, Moon, HelpCircle } from 'lucide-react';
import { useTheme } from '../theme/useTheme';

export interface TopBarProps {
  onOpenHelp?: () => void;
  className?: string;
}

export const TopBar: React.FC<TopBarProps> = ({ onOpenHelp, className = '' }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { themeChoice, resolvedTheme, cycleTheme } = useTheme();

  const isHome = location.pathname === '/home' || location.pathname === '/';
  const isWelcome = location.pathname === '/welcome';
  const canGoBack = !isHome && !isWelcome;

  const accessibleThemeLabel = `Theme: ${
    themeChoice === 'system' ? 'System (' + resolvedTheme + ')' : themeChoice
  }. Switch theme`;

  return (
    <header
      className={`sticky top-0 z-40 w-full bg-bg/90 backdrop-blur-md border-b border-border/80 transition-colors ${className}`}
    >
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-3">
        {/* Left: Back button or App Brand */}
        <div className="flex items-center gap-2">
          {canGoBack && (
            <button
              onClick={() => navigate(-1)}
              className="p-1.5 -ml-1.5 text-text-muted hover:text-text hover:bg-surface-2 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-text-muted"
              aria-label="Go back to previous screen"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}

          <div
            onClick={() => navigate('/home')}
            className="flex items-center gap-2 cursor-pointer select-none group"
            role="link"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter') navigate('/home');
            }}
          >
            <div className="w-7 h-7 rounded-lg bg-surface-2 border border-border flex items-center justify-center text-text group-hover:border-text-muted/60 transition-colors">
              <ShieldCheck className="w-4 h-4 text-blue-500" />
            </div>
            <span className="text-base font-semibold tracking-tight text-text">
              ScamLens
            </span>
          </div>
        </div>

        {/* Right actions: Quick Theme Toggle & Help */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={cycleTheme}
            className="p-1.5 rounded-lg text-text-muted hover:text-text hover:bg-surface-2 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-text-muted"
            title={accessibleThemeLabel}
            aria-label={accessibleThemeLabel}
          >
            {resolvedTheme === 'dark' ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
          </button>

          <button
            onClick={() => onOpenHelp?.()}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium text-text-muted hover:text-text bg-surface-2 hover:bg-surface border border-border transition-colors"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Help</span>
          </button>
        </div>
      </div>
    </header>
  );
};
