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
      className="hidden lg:flex flex-col w-64 h-screen sticky top-0 bg-surface border-r border-border p-6 justify-between select-none shrink-0"
      aria-label="Desktop Sidebar Navigation"
    >
      {/* Brand Header */}
      <div className="space-y-6">
        <div
          onClick={() => navigate('/home')}
          className="flex items-center gap-3 cursor-pointer group"
          role="link"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter') navigate('/home');
          }}
        >
          <div className="w-10 h-10 rounded-2xl bg-primary text-on-primary flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight text-text leading-tight">
              ScamLens
            </h1>
            <p className="text-[11px] text-text-muted font-medium">Digital Safety</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1.5" aria-label="Main menu">
          {navItems.map((item) => {
            const isActive =
              location.pathname === item.path ||
              (item.path === '/home' && location.pathname === '/');
            const Icon = item.icon;

            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-full text-sm font-medium transition-all text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                  isActive
                    ? 'bg-primary text-on-primary shadow-sm'
                    : 'text-text-muted hover:text-text hover:bg-surface-2'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}

          <button
            onClick={() => onOpenHelp?.()}
            className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-full text-sm font-medium text-text-muted hover:text-text hover:bg-surface-2 transition-all text-left"
          >
            <HelpCircle className="w-4 h-4 shrink-0" />
            <span>Help &amp; FAQ</span>
          </button>
        </nav>
      </div>

      {/* Footer Area: Helpline + Theme Toggle */}
      <div className="space-y-5 pt-4 border-t border-border">
        {/* Region badge */}
        <div className="px-3 py-2 rounded-card bg-surface-2 border border-border">
          <div className="text-[11px] font-semibold text-text uppercase tracking-wider">
            {region.name} Helpline
          </div>
          <div className="text-xs text-text-muted mt-0.5 truncate">
            {region.helpline ? `Dial ${region.helpline}` : region.portalName}
          </div>
        </div>

        {/* Theme segmented control */}
        <div>
          <div className="text-xs font-semibold text-text mb-2">Appearance</div>
          <ThemeToggle />
        </div>
      </div>
    </aside>
  );
};
