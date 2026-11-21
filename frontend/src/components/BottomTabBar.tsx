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
      className="fixed bottom-0 left-0 right-0 z-40 bg-bg/95 backdrop-blur-md border-t border-border lg:hidden transition-colors"
      style={{ paddingBottom: 'max(0.75rem, env(safe-area-inset-bottom))' }}
      aria-label="Mobile Navigation Bar"
    >
      <div className="max-w-md mx-auto px-4 h-14 flex items-center justify-around">
        {tabs.map((tab) => {
          const isActive =
            location.pathname === tab.path ||
            (tab.path === '/home' && location.pathname === '/');
          const Icon = tab.icon;

          return (
            <button
              key={tab.path}
              onClick={() => navigate(tab.path)}
              className={`flex flex-col items-center justify-center gap-1 w-16 h-12 rounded-xl transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                isActive ? 'text-primary' : 'text-text-muted hover:text-text'
              }`}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon
                className={`w-5 h-5 transition-transform ${
                  isActive ? 'scale-110 stroke-[2.5]' : 'stroke-[1.8]'
                }`}
              />
              <span className={`text-[11px] font-medium ${isActive ? 'font-bold' : ''}`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
