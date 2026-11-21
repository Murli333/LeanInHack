import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { WelcomePage } from './pages/WelcomePage';
import { HomePage } from './pages/HomePage';
import { ScanPage } from './pages/ScanPage';
import { ProgressPage } from './pages/ProgressPage';
import { ReportPage } from './pages/ReportPage';
import { HistoryPage } from './pages/HistoryPage';
import { InvestigationPage } from './pages/InvestigationPage';
import { ProfilePage } from './pages/ProfilePage';
import { DevComponentsPage } from './pages/DevComponentsPage';

function RootRedirect() {
  try {
    const hasVisited = localStorage.getItem('scamlens-visited');
    if (hasVisited === 'true') {
      return <Navigate to="/home" replace />;
    }
  } catch {
    // fallback
  }
  return <Navigate to="/welcome" replace />;
}

export const App: React.FC = () => {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<RootRedirect />} />
        <Route path="/welcome" element={<WelcomePage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/scan/:id/progress" element={<ProgressPage />} />
        <Route path="/report/:id" element={<ReportPage />} />
        <Route path="/report/:id/investigation" element={<InvestigationPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/dev/components" element={<DevComponentsPage />} />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </AppShell>
  );
};
