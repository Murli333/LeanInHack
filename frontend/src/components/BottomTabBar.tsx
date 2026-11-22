import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Home, PlusSquare, History, User } from 'lucide-react';

export const BottomTabBar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { path: '/home', label: 'Home', icon: Home },
    { path: '/scan', label: 'Scan', icon: PlusSquare },
    { path: '/history', label: 'History', icon: History },
    { path: '/profile', label: 'Profile', icon: User },
  ];

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 bg-surface/85 backdrop-blur-xl border-t border-border lg:hidden transition-all shadow-2xl"
      style={{ paddingBottom: 'max(0.6rem, env(safe-area-inset-bottom))' }}
      aria-label="Mobile Navigation Bar"
    >
      <div className="max-w-md mx-auto px-4 h-16 flex items-center justify-around">
        {tabs.map((tab) => {
          const isActive =
            location.pathname === tab.path ||
            (tab.path === '/home' && location.pathname === '/');
          const Icon = tab.icon;

          return (
            <button
              key={tab.path}
              onClick={() => navigate(tab.path)}
              className={`flex flex-col items-center justify-center gap-1 w-16 h-12 rounded-2xl transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent active:scale-95 ${
                isActive
                  ? 'bg-primary/15 text-primary dark:text-accent border border-primary/20 shadow-sm'
                  : 'text-text-muted hover:text-text hover:bg-surface-2/60'
              }`}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon
                className={`w-5 h-5 transition-transform ${
                  isActive ? 'scale-110 stroke-[2.4]' : 'stroke-[1.8]'
                }`}
              />
              <span className={`text-[11px] font-semibold tracking-tight ${isActive ? 'text-primary dark:text-accent' : ''}`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
