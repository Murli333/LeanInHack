import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Lock, Search, CheckCircle, Shield } from 'lucide-react';
import { Button } from '../components/Button';

export const WelcomePage: React.FC = () => {
  const navigate = useNavigate();

  const handleStart = () => {
    try {
      localStorage.setItem('scamlens-visited', 'true');
    } catch {
      // ignore
    }
    navigate('/home');
  };

  const steps = [
    {
      num: '1',
      title: 'Choose what to check',
      desc: 'Paste a suspicious SMS message, WhatsApp text, or unverified link.',
      icon: Search,
    },
    {
      num: '2',
      title: 'Submit and wait a moment',
      desc: 'Our engine runs pattern matching, calibrated models, and threat-database checks.',
      icon: Shield,
    },
    {
      num: '3',
      title: 'See the risk and next steps',
      desc: 'Get plain-language evidence, danger warnings, and official helpline assistance.',
      icon: CheckCircle,
    },
  ];

  return (
    <div className="py-6 sm:py-12 space-y-10 max-w-2xl mx-auto">
      {/* Hero Header */}
      <div className="text-center space-y-4">
        <div className="w-16 h-16 rounded-3xl bg-primary text-on-primary flex items-center justify-center mx-auto shadow-lg shadow-primary/20">
          <ShieldCheck className="w-9 h-9" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-text">
            Think before you trust.
            <br />
            Scan before you click.
          </h1>
          <p className="text-sm sm:text-base text-text-muted max-w-md mx-auto leading-relaxed">
            Detect the scam. Understand the risk. Stay protected from everyday digital fraud.
          </p>
        </div>

        <div className="pt-2">
          <Button
            variant="primary"
            size="huge"
            icon={<ArrowRight className="w-5 h-5" />}
            onClick={handleStart}
            className="w-full sm:w-auto"
          >
            Start a scan
          </Button>
        </div>
      </div>

      {/* 3-Step How It Works */}
      <div className="space-y-4">
        <h2 className="text-xs font-bold text-text-muted uppercase tracking-wider text-center">
          How it works in 3 easy steps
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {steps.map((st) => {
            const Icon = st.icon;
            return (
              <div
                key={st.num}
                className="p-5 rounded-card-lg bg-surface-2 border border-border space-y-3 text-center sm:text-left transition-all hover:border-text-muted/30"
              >
                <div className="w-10 h-10 rounded-xl bg-surface border border-border flex items-center justify-center text-primary shadow-sm mx-auto sm:mx-0">
                  <Icon className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-sm font-bold text-text">
                    {st.num}. {st.title}
                  </h3>
                  <p className="text-xs text-text-muted leading-relaxed">
                    {st.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Privacy Guarantee Note */}
      <div className="rounded-card-lg border border-border bg-surface-2/60 p-4 flex items-start gap-3 text-xs text-text-muted leading-relaxed">
        <Lock className="w-4 h-4 text-primary shrink-0 mt-0.5" />
        <div>
          <strong className="text-text">Privacy commitment:</strong> Submitted messages may contain sensitive or personal details. ScamLens evaluates text in memory without selling data or storing submission content on external servers.
        </div>
      </div>
    </div>
  );
};
