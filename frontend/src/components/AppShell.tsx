import React, { useState } from 'react';
import { TopBar } from './TopBar';
import { BottomTabBar } from './BottomTabBar';
import { SideNav } from './SideNav';
import { HelplineCard } from './HelplineCard';
import { X, ShieldCheck, HelpCircle } from 'lucide-react';
import { Button } from './Button';

export interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [helpOpen, setHelpOpen] = useState(false);

  return (
    <div className="min-h-screen min-h-dvh bg-bg text-text flex flex-col lg:flex-row antialiased">
      {/* Desktop Left Sidebar (>=1024px) */}
      <SideNav onOpenHelp={() => setHelpOpen(true)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <TopBar onOpenHelp={() => setHelpOpen(true)} />

        {/* Page Content Container */}
        <main
          className="flex-1 w-full max-w-xl sm:max-w-2xl lg:max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-6 pb-24 lg:pb-12"
          role="main"
        >
          {children}
        </main>

        {/* Mobile & Tablet Fixed Bottom Navigation Bar (<1024px) */}
        <BottomTabBar />
      </div>

      {/* Accessible Help Sheet / Modal */}
      {helpOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in"
          role="dialog"
          aria-modal="true"
          aria-labelledby="help-title"
        >
          <div className="w-full max-w-lg rounded-xl bg-surface border border-border/80 p-5 shadow-2xl space-y-4 animate-scale-up max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-border/60">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-primary text-white flex items-center justify-center">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <h3 id="help-title" className="text-sm font-semibold text-text">
                  Help &amp; Safety Guide
                </h3>
              </div>
              <button
                onClick={() => setHelpOpen(false)}
                className="p-1 text-text-muted hover:text-text rounded-md transition-colors"
                aria-label="Close help"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3.5 text-xs text-text-muted">
              <div>
                <h4 className="font-medium text-text mb-1">How ScamLens works</h4>
                <p className="leading-relaxed">
                  ScamLens inspects messages and links using pattern-matching rules, threat intelligence databases (such as OpenPhish), and calibrated risk models.
                </p>
              </div>

              <div>
                <h4 className="font-medium text-text mb-1">Risk level guide</h4>
                <ul className="space-y-1.5 pt-1 text-xs">
                  <li>
                    <strong className="text-danger font-medium">High risk:</strong> Strong signs of fraudulent manipulation, urgent demands, or known phishing links.
                  </li>
                  <li>
                    <strong className="text-warn font-medium">Medium risk:</strong> Suspicious wording or unverified domains that warrant caution.
                  </li>
                  <li>
                    <strong className="text-safe font-medium">Low risk:</strong> No typical threat patterns detected. Does not constitute an absolute guarantee.
                  </li>
                  <li>
                    <strong className="text-text-muted font-medium">Inconclusive:</strong> Insufficient verifiable information. Maintain standard caution.
                  </li>
                </ul>
              </div>

              <HelplineCard />
            </div>

            <div className="pt-2 text-right">
              <Button variant="primary" size="sm" onClick={() => setHelpOpen(false)}>
                Dismiss
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
