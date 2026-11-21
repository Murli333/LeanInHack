import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';
import { ThemeChoice, ResolvedTheme } from '../types';

interface ThemeContextType {
  themeChoice: ThemeChoice;
  resolvedTheme: ResolvedTheme;
  setTheme: (choice: ThemeChoice) => void;
  cycleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const STORAGE_KEY = 'scamlens-theme';

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [themeChoice, setThemeChoiceState] = useState<ThemeChoice>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY) as ThemeChoice;
      if (saved === 'system' || saved === 'light' || saved === 'dark') {
        return saved;
      }
    } catch {
      // Fallback on error
    }
    return 'system';
  });

  const [systemIsDark, setSystemIsDark] = useState<boolean>(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return true;
  });

  // Watch system prefers-color-scheme live
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      setSystemIsDark(e.matches);
    };

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  const resolvedTheme: ResolvedTheme = useMemo(() => {
    if (themeChoice === 'system') {
      return systemIsDark ? 'dark' : 'light';
    }
    return themeChoice;
  }, [themeChoice, systemIsDark]);

  // Synchronize with DOM attributes and <meta name="theme-color">
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', resolvedTheme);
    root.style.colorScheme = resolvedTheme;

    const meta = document.getElementById('theme-color-meta');
    if (meta) {
      meta.setAttribute('content', resolvedTheme === 'dark' ? '#05080F' : '#F5F7FB');
    }
  }, [resolvedTheme]);

  const setTheme = (choice: ThemeChoice) => {
    setThemeChoiceState(choice);
    try {
      localStorage.setItem(STORAGE_KEY, choice);
    } catch {
      // ignore
    }
  };

  const cycleTheme = () => {
    if (themeChoice === 'system') setTheme('light');
    else if (themeChoice === 'light') setTheme('dark');
    else setTheme('system');
  };

  return (
    <ThemeContext.Provider value={{ themeChoice, resolvedTheme, setTheme, cycleTheme }}>
      {children}
      {/* Invisible live region to announce theme changes politely to screen readers */}
      <div className="sr-only" role="status" aria-live="polite">
        {resolvedTheme === 'dark' ? 'Dark theme on' : 'Light theme on'}
      </div>
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
