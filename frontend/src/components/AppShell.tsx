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
          <div className="w-full max-w-lg rounded-card-lg bg-surface border border-border p-6 shadow-2xl space-y-5 animate-scale-up max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-primary text-on-primary flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 id="help-title" className="text-lg font-bold text-text">
                  ScamLens Help &amp; Safety
                </h3>
              </div>
              <button
                onClick={() => setHelpOpen(false)}
                className="p-1.5 text-text-muted hover:text-text rounded-full transition-colors"
                aria-label="Close help"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-sm text-text-muted">
              <div>
                <h4 className="font-semibold text-text mb-1">How does ScamLens work?</h4>
                <p className="leading-relaxed">
                  ScamLens inspects messages, links, and screenshots using pattern-matching rules, threat databases (such as OpenPhish), and calibrated classification models.
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-text mb-1">What do the risk levels mean?</h4>
                <ul className="space-y-1.5 pt-1 text-xs">
                  <li>
                    <strong className="text-danger">Scam alert — High risk:</strong> Strong signs of fraudulent manipulation, urgent demands, or known malicious links.
                  </li>
                  <li>
                    <strong className="text-warn">Be careful:</strong> Suspicious wording or unverified links that warrant caution.
                  </li>
                  <li>
                    <strong className="text-safe">Looks low risk:</strong> No typical threat patterns detected. Does not constitute an absolute guarantee.
                  </li>
                  <li>
                    <strong className="text-unknown">We can&apos;t tell:</strong> Inconclusive data. Treat with standard everyday caution.
                  </li>
                </ul>
              </div>

              <HelplineCard />
            </div>

            <div className="pt-2 text-right">
              <Button variant="primary" size="md" onClick={() => setHelpOpen(false)}>
                Got it
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
