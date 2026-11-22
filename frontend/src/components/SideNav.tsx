import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Home,
  PlusSquare,
  History,
  User,
  Sliders,
  HelpCircle,
} from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { getActiveRegion } from '../config/regions';

export interface SideNavProps {
  onOpenHelp?: () => void;
}

export const SideNav: React.FC<SideNavProps> = ({ onOpenHelp }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const region = getActiveRegion();

  const navItems = [
    { path: '/home', label: 'Home', icon: Home },
    { path: '/scan', label: 'Check content', icon: PlusSquare },
    { path: '/history', label: 'Scan history', icon: History },
    { path: '/profile', label: 'Profile & Privacy', icon: User },
    { path: '/dev/components', label: 'Component Gallery', icon: Sliders },
  ];

  return (
    <aside
      className="hidden lg:flex flex-col w-56 h-screen sticky top-0 bg-surface border-r border-border/80 p-4 justify-between select-none shrink-0"
      aria-label="Desktop Sidebar Navigation"
    >
      {/* Brand Header */}
      <div className="space-y-5">
        <div
          onClick={() => navigate('/home')}
          className="flex items-center gap-2.5 cursor-pointer px-2"
          role="link"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter') navigate('/home');
          }}
        >
          <div className="w-7 h-7 rounded-lg bg-primary text-white flex items-center justify-center shrink-0">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight text-text leading-tight">
              ScamLens
            </h1>
            <p className="text-[10px] text-text-muted font-mono tracking-tight uppercase">Threat Defense</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1" aria-label="Main menu">
          {navItems.map((item) => {
            const isActive =
              location.pathname === item.path ||
              (item.path === '/home' && location.pathname === '/');
            const Icon = item.icon;

            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors text-left focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-border ${
                  isActive
                    ? 'bg-surface-2 text-text border border-border/70'
                    : 'text-text-muted hover:text-text hover:bg-surface-2/60 border border-transparent'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-text' : 'text-text-muted'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}

          <button
            onClick={() => onOpenHelp?.()}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium text-text-muted hover:text-text hover:bg-surface-2/60 transition-colors text-left border border-transparent"
          >
            <HelpCircle className="w-4 h-4 shrink-0 text-text-muted" />
            <span>Help &amp; FAQ</span>
          </button>
        </nav>
      </div>

      {/* Footer Area: Helpline + Theme Toggle */}
      <div className="space-y-4 pt-3 border-t border-border/60">
        {/* Region badge */}
        <div className="px-3 py-2 rounded-lg bg-surface-2/50 border border-border/70">
          <div className="text-[10px] font-mono text-text-muted uppercase tracking-wider">
            {region.name} Helpline
          </div>
          <div className="text-xs text-text font-medium mt-0.5 truncate">
            {region.helpline ? `Dial ${region.helpline}` : region.portalName}
          </div>
        </div>

        {/* Theme segmented control */}
        <div>
          <div className="text-[11px] font-mono text-text-muted uppercase tracking-wider mb-1.5">Theme</div>
          <ThemeToggle />
        </div>
      </div>
    </aside>
  );
};
