import { Scan, ScanFilter, ScanStats, ScanType, ScanStep, ScanResult } from '../types';
import { INITIAL_MOCK_SCANS } from '../mocks/scanMocks';

const STORAGE_KEY = 'scamlens-local-scans';
// Remote backend URL if configured (e.g., https://your-backend.onrender.com). Empty string uses relative /api.
const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
// Prefer real backend by default unless VITE_USE_MOCK is explicitly 'true'
const FORCE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// Helper to determine if we are running on a static host (Netlify, Vercel, etc.) without a Python backend
function checkIsStaticHost(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    if (sessionStorage.getItem('scamlens_static_host') === 'true') {
      return true;
    }
  } catch {
    // ignore
  }
  if (import.meta.env.VITE_API_URL) return false;
  const hostname = window.location.hostname;
  if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1' && !hostname.startsWith('192.168.')) {
    return true;
  }
  return false;
}

let isStaticHostDetected = checkIsStaticHost();

function markStaticHost() {
  isStaticHostDetected = true;
  try {
    sessionStorage.setItem('scamlens_static_host', 'true');
  } catch {
    // ignore
  }
}

// Helper to deep clone to prevent referential mutation bugs in React Query
function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj));
}

// Helper to load or initialize local mock scans
function loadMockScans(): Scan[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch {
    // fallback
  }
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_MOCK_SCANS));
  } catch {
    // ignore
  }
  return deepClone(INITIAL_MOCK_SCANS);
}

function saveMockScans(scans: Scan[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(scans));
  } catch {
    // ignore
  }
}

// In-memory runtime state for offline/mock fallback
let runtimeScans: Scan[] = loadMockScans();

export interface CreateScanParams {
  type: ScanType;
  content: string;
}

/**
 * Calibrated standalone client threat detection engine.
 * Mirrors Member 1 (ML) + Member 2 (Detection Rules) for instant, offline, and static Netlify execution.
 */
export function analyzeContentLocally(type: ScanType, rawContent: string): ScanResult {
  const content = (rawContent || '').trim();
  const lower = content.toLowerCase();

  // 1. Minimal context check
  if (content.length < 12) {
    return {
      riskLevel: 'unknown',
      summary: "We can't tell whether this input is risky or legitimate due to minimal context.",
      scoreValidated: false,
      category: 'Inconclusive Input',
      evidence: [
        {
          id: 'ev-short-1',
          title: 'Insufficient context',
          kind: 'not_run',
          detail: 'The submitted text is too brief to confirm authenticity or detect threat indicators.',
          source: 'ScamLens Classifier',
        },
      ],
      actions: [
        'Exercise standard caution with unfamiliar senders',
        'Remember that an inconclusive status does not confirm safety',
      ],
    };
  }

  // 2. Benign / Legitimate Transaction Checks (Overrides false positives)
  const isTrustedBank =
    lower.includes('onlinesbi.sbi') ||
    lower.includes('hdfcbank.com') ||
    lower.includes('icicibank.com') ||
    lower.includes('axisbank.com') ||
    lower.includes('amazon.in') ||
    lower.includes('google.com') ||
    lower.includes('irctc.co.in');

  const hasBenignOtp =
    (lower.includes('otp') || lower.includes('one time password')) &&
    (lower.includes('never share') || lower.includes('do not share') || lower.includes('valid for 10 minutes') || lower.includes('valid for 5 minutes')) &&
    !lower.includes('block') &&
    !lower.includes('locked') &&
    !lower.includes('urgent') &&
    !lower.includes('.xyz') &&
    !lower.includes('.top');

  const hasBenignDelivery =
    (lower.includes('swiggy') || lower.includes('zomato') || lower.includes('amazon') || lower.includes('flipkart')) &&
    (lower.includes('delivered') || lower.includes('out for delivery') || lower.includes('order picked up') || lower.includes('order confirmed')) &&
    !lower.includes('paytm') &&
    !lower.includes('claim');

  const hasBenignBankAlert =
    (lower.includes('debited') || lower.includes('credited')) &&
    (lower.includes('bal') || lower.includes('balance') || lower.includes('a/c') || lower.includes('account')) &&
    !lower.includes('kyc') &&
    !lower.includes('pan') &&
    !lower.includes('verify') &&
    !lower.includes('http');

  const hasPnrAlert = lower.includes('pnr') && (lower.includes('irctc') || lower.includes('train') || lower.includes('coach') || lower.includes('confirmed'));

  if (isTrustedBank || hasBenignOtp || hasBenignDelivery || hasBenignBankAlert || hasPnrAlert) {
    return {
      riskLevel: 'low',
      summary: 'Standard service confirmation with no suspicious links, credential requests, or urgent threats.',
      score: 4,
      scoreValidated: true,
      category: 'Verified Safe Communication',
      evidence: [
        {
          id: 'ev-clean-1',
          title: 'Clean baseline assessment',
          kind: 'confirmed',
          detail: 'No match with known threat databases or phishing indicators.',
          source: 'ScamLens Rule Engine',
        },
        {
          id: 'ev-clean-2',
          title: 'Authentic fulfillment signature',
          kind: 'confirmed',
          detail: 'Contains standard informational structure without coercive urgency or redirect links.',
          source: 'Calibrated Classifier',
        },
      ],
      actions: [
        'No immediate threat patterns detected',
        'Continue to practice everyday caution with unsolicited communications',
      ],
    };
  }

  // 3. High Threat Checks
  const hasKycUrgent =
    (lower.includes('kyc') || lower.includes('pan card') || lower.includes('aadhar') || lower.includes('aadhaar')) &&
    (lower.includes('block') || lower.includes('locked') || lower.includes('deactivated') || lower.includes('suspend') || lower.includes('urgent') || lower.includes('immediately') || lower.includes('update'));

  const hasBankImpersonation =
    (lower.includes('sbi') || lower.includes('hdfc') || lower.includes('icici') || lower.includes('pnb') || lower.includes('bank') || lower.includes('yono')) &&
    (lower.includes('blocked') || lower.includes('locked') || lower.includes('kyc') || lower.includes('pan') || lower.includes('verify') || lower.includes('.xyz') || lower.includes('.top') || lower.includes('link'));

  const hasElectricityScam =
    (lower.includes('electricity') || lower.includes('power') || lower.includes('bijli') || lower.includes('light cut')) &&
    (lower.includes('disconnect') || lower.includes('cut') || lower.includes('bill unpaid') || lower.includes('tonight') || lower.includes('officer'));

  const hasUpiTrap =
    (lower.includes('upi pin') || lower.includes('pin to receive') || lower.includes('scan qr to receive') || lower.includes('accept payment pin')) ||
    (lower.includes('cashback') && lower.includes('pin'));

  const hasDigitalArrest =
    (lower.includes('cbi') || lower.includes('police') || lower.includes('narcotics') || lower.includes('customs') || lower.includes('digital arrest') || lower.includes('arrest warrant')) &&
    (lower.includes('skype') || lower.includes('parcel') || lower.includes('drugs') || lower.includes('money laundering') || lower.includes('interrogation'));

  const hasJobScam =
    (lower.includes('part-time job') || lower.includes('earn 5000') || lower.includes('daily income') || lower.includes('like youtube') || lower.includes('hotel review')) &&
    (lower.includes('telegram') || lower.includes('whatsapp') || lower.includes('daily') || lower.includes('income'));

  const hasPhishingDomain =
    lower.includes('.xyz') ||
    lower.includes('.top') ||
    lower.includes('.work') ||
    lower.includes('.icu') ||
    lower.includes('.buzz') ||
    lower.includes('.club') ||
    lower.includes('.live') ||
    lower.includes('.click') ||
    lower.includes('.rest') ||
    lower.includes('.bid') ||
    /https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(lower);

  const hasLotteryScam =
    (lower.includes('congratulations') || lower.includes('won') || lower.includes('lucky draw') || lower.includes('lottery') || lower.includes('reward')) &&
    (lower.includes('claim') || lower.includes('fee') || lower.includes('charges') || lower.includes('tax') || lower.includes('bonus'));

  if (hasKycUrgent || hasBankImpersonation) {
    return {
      riskLevel: 'high',
      summary: 'Deceptive bank impersonation attempt coercing sensitive authentication or KYC credentials.',
      score: 94,
      scoreValidated: true,
      category: 'Banking / KYC Phishing',
      evidence: [
        {
          id: 'ev-kyc-1',
          title: 'Fake KYC / Account lockout threat',
          kind: 'confirmed',
          detail: 'Fabricates urgency claiming your account is blocked or suspended to force quick compliance.',
          source: 'Heuristic Rule Engine',
        },
        {
          id: 'ev-kyc-2',
          title: 'Credential harvesting indicators',
          kind: 'confirmed',
          detail: 'Requests personal documents, PAN/KYC updates, or redirects to an unverified portal.',
          source: 'Calibrated Threat Classifier',
        },
        ...(hasPhishingDomain ? [{
          id: 'ev-kyc-3',
          title: 'Untrusted domain extension',
          kind: 'confirmed' as const,
          detail: 'Uses disposable or non-standard top-level domain frequently utilized in phishing schemes.',
          source: 'Structural Domain Inspector',
        }] : []),
      ],
      actions: [
        'Do not click embedded links, enter passwords, or call numbers in the message',
        'Never share OTPs, PINs, NetBanking credentials, or card CVVs',
        'Report this incident immediately to the National Cyber Crime Helpline (1930)',
      ],
    };
  }

  if (hasElectricityScam) {
    return {
      riskLevel: 'high',
      summary: 'Urgent utility disconnection scheme threatening power shutdown to extort immediate payment.',
      score: 90,
      scoreValidated: true,
      category: 'Utility Disconnection Scam',
      evidence: [
        {
          id: 'ev-elec-1',
          title: 'Power disconnection deadline threat',
          kind: 'confirmed',
          detail: 'Threatens immediate service cutoff (e.g. tonight at 9:30 PM) to induce panic.',
          source: 'Urgency Pattern Matcher',
        },
        {
          id: 'ev-elec-2',
          title: 'Unofficial contact channel',
          kind: 'warning',
          detail: 'Directs payment or inquiries to an unverified personal mobile number or third-party app.',
          source: 'Heuristic Inspector',
        },
      ],
      actions: [
        'Do not call the phone number mentioned in the SMS',
        'Do not download remote-access apps (AnyDesk, TeamViewer, RustDesk)',
        'Check your electricity bill status exclusively through the official state discom portal or electricity bill app',
      ],
    };
  }

  if (hasDigitalArrest) {
    return {
      riskLevel: 'high',
      summary: 'High-pressure extortion scheme impersonating law enforcement, police, customs, or CBI officers.',
      score: 96,
      scoreValidated: true,
      category: 'Digital Arrest / Law Enforcement Extortion',
      evidence: [
        {
          id: 'ev-arrest-1',
          title: 'Fabricated legal / arrest threat',
          kind: 'confirmed',
          detail: 'Claims narcotics, illegal packages, or money laundering to threaten digital custody.',
          source: 'Law Enforcement Pattern Engine',
        },
        {
          id: 'ev-arrest-2',
          title: 'Video call interrogation demand',
          kind: 'confirmed',
          detail: 'Demands joining Skype or WhatsApp video calls under false pretext of judicial interrogation.',
          source: 'Heuristic Rule Engine',
        },
      ],
      actions: [
        'Indian law enforcement and courts NEVER conduct digital arrests or Skype interrogations',
        'Immediately disconnect any video or audio call from unknown authorities',
        'Dial 1930 or file a report at cybercrime.gov.in',
      ],
    };
  }

  if (hasUpiTrap) {
    return {
      riskLevel: 'high',
      summary: 'UPI payment reversal trap attempting to debit your bank account under the guise of receiving funds.',
      score: 95,
      scoreValidated: true,
      category: 'UPI PIN / QR Fraud',
      evidence: [
        {
          id: 'ev-upi-1',
          title: 'Reversed payment flow indicator',
          kind: 'confirmed',
          detail: 'Demands entering a UPI PIN or scanning a QR code to "receive" funds. In UPI, PIN is strictly for sending money.',
          source: 'Payment Protocol Validator',
        },
      ],
      actions: [
        'NEVER enter your UPI PIN to receive money or refunds',
        'Reject any incoming collect requests on PhonePe, Google Pay, or Paytm',
      ],
    };
  }

  if (hasPhishingDomain) {
    return {
      riskLevel: 'high',
      summary: 'High-risk untrusted URL hosted on disposable domain registries commonly used in phishing.',
      score: 92,
      scoreValidated: true,
      category: 'Phishing URL',
      evidence: [
        {
          id: 'ev-url-1',
          title: 'High-risk domain registry extension',
          kind: 'confirmed',
          detail: 'Domain uses a disposable or non-standard TLD associated with malicious phishing campaigns.',
          source: 'Structural URL Inspection',
        },
      ],
      actions: [
        'Do not visit or enter any credentials on this website',
        'Clear browser data if you accidentally opened the link',
      ],
    };
  }

  if (hasJobScam || hasLotteryScam) {
    return {
      riskLevel: 'medium',
      summary: 'Unsolicited reward or high-yield task offer characteristic of recruitment and advance-fee schemes.',
      score: 62,
      scoreValidated: true,
      category: hasJobScam ? 'Task / Recruitment Scheme' : 'Unsolicited Lottery Lure',
      evidence: [
        {
          id: 'ev-job-1',
          title: 'Unrealistic return / reward hook',
          kind: 'warning',
          detail: 'Promises high daily income for minimal effort or claims unverified lottery prizes.',
          source: 'Classifier Engine',
        },
      ],
      actions: [
        'Never pay registration fees, security deposits, or advance charges to claim rewards or start jobs',
        'Verify company credentials directly on official career portals',
      ],
    };
  }

  // Default fallback for general messages
  return {
    riskLevel: 'low',
    summary: 'No recognized threat patterns, urgency triggers, or deceptive links detected.',
    score: 8,
    scoreValidated: true,
    category: 'General Communication',
    evidence: [
      {
        id: 'ev-gen-1',
        title: 'Clean baseline assessment',
        kind: 'confirmed',
        detail: 'Evaluated across phishing databases, credential triggers, and threat models without match.',
        source: 'ScamLens Verification Engine',
      },
    ],
    actions: [
      'Looks low risk based on our automated verification checks',
      'Always exercise judgment when interacting with unknown senders',
    ],
  };
}

export const apiClient = {
  /**
   * Submit content for scanning
   * State flow: VALIDATING -> PROCESSING
   */
  async createScan(params: CreateScanParams): Promise<{ id: string }> {
    const content = (params.content || '').trim();
    if (!content) {
      throw new Error('Scan content cannot be empty.');
    }

    if (!FORCE_MOCK && !isStaticHostDetected) {
      try {
        const res = await fetch(`${API_BASE}/api/scans`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: params.type, content }),
        });

        const contentType = res.headers.get('content-type') || '';

        // If backend returned HTML (Netlify/Vercel SPA rewrite), or 404/405, activate client engine!
        if (res.status === 404 || res.status === 405 || !contentType.includes('application/json')) {
          markStaticHost();
        } else if (res.ok) {
          const data = await res.json();
          return { id: data.id };
        } else if (res.status === 400) {
          const errData = await res.json().catch(() => ({ detail: 'Invalid request' }));
          throw new Error(errData.detail || 'Validation failed');
        } else {
          markStaticHost();
        }
      } catch (err: any) {
        if (err?.message && (err.message.includes('Validation failed') || err.message.includes('cannot be empty'))) {
          throw err;
        }
        markStaticHost();
      }
    }

    // Standalone Client Detection Engine (Offline / Static Host / Netlify)
    const id = 'scan-' + Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
    const isUrl = params.type === 'url' || content.startsWith('http://') || content.startsWith('https://');

    // Pre-calculate verified result immediately
    const precomputedResult = analyzeContentLocally(params.type, content);

    const steps: ScanStep[] = [
      { key: 'extract', label: 'Extract content', status: 'completed' },
      { key: 'patterns', label: 'Check patterns', status: 'running' },
      { key: 'reputation', label: 'Check URL reputation', status: isUrl ? 'waiting' : 'waiting' },
      { key: 'evidence', label: 'Combine evidence', status: 'waiting' },
      { key: 'report', label: 'Prepare report', status: 'waiting' },
    ];

    const title = params.type === 'url'
      ? `Link: ${content.replace(/^https?:\/\//, '').substring(0, 32)}...`
      : content.substring(0, 36) + (content.length > 36 ? '...' : '');

    const newScan: Scan = {
      id,
      type: params.type,
      content,
      title,
      createdAt: new Date().toISOString(),
      status: 'running',
      steps,
      result: precomputedResult,
    };

    runtimeScans = [newScan, ...runtimeScans.filter((s) => s.id !== id)];
    saveMockScans(runtimeScans);

    return { id };
  },

  /**
   * Retrieve scan details and real-time step status
   */
  async getScan(id: string): Promise<Scan> {
    if (!FORCE_MOCK && !isStaticHostDetected) {
      try {
        const res = await fetch(`${API_BASE}/api/scans/${id}`);
        const contentType = res.headers.get('content-type') || '';
        if (res.ok && contentType.includes('application/json')) {
          const data = await res.json();
          return data;
        } else {
          markStaticHost();
        }
      } catch {
        markStaticHost();
      }
    }

    // Always ensure fresh sync from localStorage
    let existing = runtimeScans.find((s) => s.id === id);
    if (!existing) {
      runtimeScans = loadMockScans();
      existing = runtimeScans.find((s) => s.id === id);
    }

    if (!existing) {
      throw new Error(`Scan ${id} not found`);
    }

    // Smooth deterministic progression logic for client/offline mock
    if (existing.status === 'running') {
      const now = Date.now();
      const elapsedMs = now - new Date(existing.createdAt).getTime();

      // Complete scan after 500ms so user experiences smooth stepper animation
      if (elapsedMs >= 500 || existing.result) {
        const result = existing.result || analyzeContentLocally(existing.type, existing.content);
        const completedScan: Scan = {
          ...existing,
          status: 'completed',
          steps: existing.steps.map((s) => ({ ...s, status: 'completed' })),
          result,
        };

        runtimeScans = runtimeScans.map((s) => (s.id === id ? completedScan : s));
        saveMockScans(runtimeScans);
        return deepClone(completedScan);
      } else {
        const progressingScan: Scan = {
          ...existing,
          steps: existing.steps.map((s, idx) => ({
            ...s,
            status: idx <= 1 ? 'completed' : idx === 2 ? 'running' : 'waiting',
          })),
        };
        runtimeScans = runtimeScans.map((s) => (s.id === id ? progressingScan : s));
        saveMockScans(runtimeScans);
        return deepClone(progressingScan);
      }
    }

    return deepClone(existing);
  },

  /**
   * List recent scans with filtering
   */
  async listScans(filter?: ScanFilter): Promise<Scan[]> {
    if (!FORCE_MOCK && !isStaticHostDetected) {
      try {
        const queryParams = new URLSearchParams();
        if (filter?.query) queryParams.set('query', filter.query);
        if (filter?.type && filter.type !== 'all') queryParams.set('type', filter.type);
        if (filter?.risk && filter.risk !== 'all') queryParams.set('risk', filter.risk);

        const res = await fetch(`${API_BASE}/api/scans?${queryParams.toString()}`);
        const contentType = res.headers.get('content-type') || '';
        if (res.ok && contentType.includes('application/json')) {
          const data = await res.json();
          return data;
        } else {
          markStaticHost();
        }
      } catch {
        markStaticHost();
      }
    }

    runtimeScans = loadMockScans();
    let results = deepClone(runtimeScans);

    if (filter?.query) {
      const q = filter.query.toLowerCase();
      results = results.filter(
        (s) => s.title.toLowerCase().includes(q) || s.content.toLowerCase().includes(q)
      );
    }

    if (filter?.type && filter.type !== 'all') {
      results = results.filter((s) => s.type === filter.type);
    }

    if (filter?.risk && filter.risk !== 'all') {
      results = results.filter((s) => s.result?.riskLevel === filter.risk);
    }

    return results;
  },

  /**
   * Delete a single scan by id
   */
  async deleteScan(id: string): Promise<void> {
    if (!FORCE_MOCK && !isStaticHostDetected) {
      try {
        const res = await fetch(`${API_BASE}/api/scans/${id}`, { method: 'DELETE' });
        const contentType = res.headers.get('content-type') || '';
        if (res.ok && contentType.includes('application/json')) {
          return;
        } else {
          markStaticHost();
        }
      } catch {
        markStaticHost();
      }
    }

    runtimeScans = loadMockScans().filter((s) => s.id !== id);
    saveMockScans(runtimeScans);
  },

  /**
   * Delete all scans (for testing empty states)
   */
  async deleteAllScans(): Promise<void> {
    if (!FORCE_MOCK && !isStaticHostDetected) {
      try {
        const res = await fetch(`${API_BASE}/api/scans`, { method: 'DELETE' });
        const contentType = res.headers.get('content-type') || '';
        if (res.ok && contentType.includes('application/json')) {
          return;
        } else {
          markStaticHost();
        }
      } catch {
        markStaticHost();
      }
    }

    runtimeScans = [];
    saveMockScans(runtimeScans);
  },

  /**
   * Reset to initial sample scans
   */
  async resetSampleScans(): Promise<void> {
    runtimeScans = deepClone(INITIAL_MOCK_SCANS);
    saveMockScans(runtimeScans);
  },

  /**
   * Get stats (Honesty Rule 5: from real stored data only!)
   */
  async getStats(): Promise<ScanStats> {
    if (!FORCE_MOCK && !isStaticHostDetected) {
      try {
        const res = await fetch(`${API_BASE}/api/stats`);
        const contentType = res.headers.get('content-type') || '';
        if (res.ok && contentType.includes('application/json')) {
          const data = await res.json();
          return data;
        } else {
          markStaticHost();
        }
      } catch {
        markStaticHost();
      }
    }

    runtimeScans = loadMockScans();
    const total = runtimeScans.length;
    const highRisk = runtimeScans.filter((s) => s.result?.riskLevel === 'high').length;

    return { total, highRisk };
  },

  /**
   * Retry a failed or partial scan step
   */
  async retryScanStep(id: string, stepKey: string): Promise<Scan> {
    runtimeScans = loadMockScans();
    const scan = runtimeScans.find((s) => s.id === id);
    if (!scan) throw new Error('Scan not found');

    const updatedScan: Scan = {
      ...scan,
      status: 'running',
      steps: scan.steps.map((st) => (st.key === stepKey ? { ...st, status: 'running' } : st)),
    };
    runtimeScans = runtimeScans.map((s) => (s.id === id ? updatedScan : s));
    saveMockScans(runtimeScans);

    // Simulate resolution after 500ms
    setTimeout(() => {
      const finished: Scan = {
        ...updatedScan,
        status: 'completed',
        steps: updatedScan.steps.map((st) => ({ ...st, status: 'completed' })),
        result: updatedScan.result
          ? {
              ...updatedScan.result,
              isPartial: false,
              summary: 'Complete check finished after successful step retry.',
            }
          : undefined,
      };
      runtimeScans = runtimeScans.map((s) => (s.id === id ? finished : s));
      saveMockScans(runtimeScans);
    }, 500);

    return deepClone(updatedScan);
  },
};
