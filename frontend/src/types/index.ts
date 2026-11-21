export type ScanType = 'text' | 'url' | 'screenshot' | 'qr' | 'audio';

export type ScanStatus = 'queued' | 'running' | 'completed' | 'partial' | 'failed';

export type StepStatus = 'waiting' | 'running' | 'completed' | 'failed';

export interface ScanStep {
  key: string;
  label: string;
  status: StepStatus;
  detail?: string;
}

export type RiskLevel = 'high' | 'medium' | 'low' | 'unknown';

export type EvidenceKind = 'confirmed' | 'warning' | 'not_run';

export interface EvidenceItem {
  id: string;
  title: string;
  kind: EvidenceKind;
  detail: string;
  source?: string;
}

export interface ScanResult {
  riskLevel: RiskLevel;
  summary: string;
  score?: number;
  scoreValidated: boolean; // Honesty rule: show numeric score ONLY if scoreValidated is true
  evidence: EvidenceItem[];
  actions: string[];
  submittedContent?: string;
  defangedContent?: string;
  category?: string;
  isPartial?: boolean;
  providerDetails?: {
    modelScore?: number;
    ruleScore?: number;
    urlScore?: number;
    openPhishMatch?: boolean;
    patternsDetected?: string[];
    investigationNotes?: string[];
  };
}

export interface Scan {
  id: string;
  type: ScanType;
  content: string;
  title: string;
  createdAt: string;
  status: ScanStatus;
  steps: ScanStep[];
  result?: ScanResult;
}

export interface ScanStats {
  total: number;
  highRisk: number;
}

export interface ScanFilter {
  query?: string;
  type?: ScanType | 'all';
  risk?: RiskLevel | 'all';
  from?: string;
  to?: string;
}

export type ThemeChoice = 'system' | 'light' | 'dark';
export type ResolvedTheme = 'light' | 'dark';

export interface RegionConfig {
  code: string;
  name: string;
  helpline: string;
  portalName: string;
  portalUrl: string;
  instructionText: string;
}

export interface FeatureFlags {
  screenshot: boolean;
  qr: boolean;
  audio: boolean;
  investigation: boolean;
}
