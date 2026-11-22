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
      className="fixed bottom-0 left-0 right-0 z-40 bg-bg/90 backdrop-blur-md border-t border-border/80 lg:hidden transition-colors"
      style={{ paddingBottom: 'max(0.6rem, env(safe-area-inset-bottom))' }}
      aria-label="Mobile Navigation Bar"
    >
      <div className="max-w-md mx-auto px-6 h-14 flex items-center justify-around">
        {tabs.map((tab) => {
          const isActive =
            location.pathname === tab.path ||
            (tab.path === '/home' && location.pathname === '/');
          const Icon = tab.icon;

          return (
            <button
              key={tab.path}
              onClick={() => navigate(tab.path)}
              className={`flex flex-col items-center justify-center gap-1 w-14 h-11 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-text-muted active:scale-95 ${
                isActive
                  ? 'text-text'
                  : 'text-text-muted/70 hover:text-text'
              }`}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon
                className={`w-5 h-5 transition-transform ${
                  isActive ? 'stroke-[2.2]' : 'stroke-[1.6]'
                }`}
              />
              <span className={`text-[10px] tracking-tight ${isActive ? 'font-semibold text-text' : 'font-medium'}`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
