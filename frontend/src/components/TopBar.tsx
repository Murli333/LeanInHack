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
      className={`sticky top-0 z-40 w-full bg-bg/80 backdrop-blur-xl border-b border-border transition-colors ${className}`}
    >
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-3">
        {/* Left: Back button or App Brand */}
        <div className="flex items-center gap-2">
          {canGoBack && (
            <button
              onClick={() => navigate(-1)}
              className="p-2 -ml-2 text-text-muted hover:text-text hover:bg-surface-2 rounded-full transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
              aria-label="Go back to previous screen"
            >
              <ChevronLeft className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>
          )}

          <div
            onClick={() => navigate('/home')}
            className="flex items-center gap-2.5 cursor-pointer select-none group"
            role="link"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter') navigate('/home');
            }}
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 text-white flex items-center justify-center shadow-md shadow-blue-500/20 ring-1 ring-white/20 group-hover:scale-105 transition-all">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-lg font-extrabold tracking-tight text-text">
                ScamLens
              </span>
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
            </div>
          </div>
        </div>

        {/* Right actions: Quick Theme Toggle & Help Pill */}
        <div className="flex items-center gap-2">
          <button
            onClick={cycleTheme}
            className="p-2 rounded-full text-text-muted hover:text-text hover:bg-surface-2 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            title={accessibleThemeLabel}
            aria-label={accessibleThemeLabel}
          >
            {resolvedTheme === 'dark' ? (
              <Sun className="w-5 h-5 text-amber-400" />
            ) : (
              <Moon className="w-5 h-5 text-slate-700" />
            )}
          </button>

          <button
            onClick={() => onOpenHelp?.()}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-surface text-text border border-border hover:border-primary/40 hover:bg-surface-2 transition-all shadow-sm active:scale-95"
          >
            <HelpCircle className="w-3.5 h-3.5 text-accent" />
            <span>Help</span>
          </button>
        </div>
      </div>
    </header>
  );
};
