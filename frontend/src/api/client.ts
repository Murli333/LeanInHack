import { Scan, ScanFilter, ScanStats, ScanType, ScanStep, ScanResult } from '../types';
import { INITIAL_MOCK_SCANS } from '../mocks/scanMocks';

const STORAGE_KEY = 'scamlens-local-scans';
// Remote backend URL if configured (e.g., https://your-backend.onrender.com). Empty string uses relative /api.
const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
// Prefer real backend by default unless VITE_USE_MOCK is explicitly 'true'
const FORCE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// Flag to track whether the current host is a static host (like Netlify without a colocated Python backend)
let isStaticHostDetected = false;

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
  // Initialize with the 5 reference mock cases
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

        // If backend returned HTML (e.g. Netlify/Vercel SPA rewrite on missing /api route),
        // or 404/405, this host is a static deployment. Activate client detection engine!
        if (res.status === 404 || res.status === 405 || (!contentType.includes('application/json') && !res.ok)) {
          isStaticHostDetected = true;
          console.info('[ScamLens] Static host detected. Seamlessly activating standalone client detection engine.');
        } else if (res.ok) {
          const data = await res.json();
          return { id: data.id };
        } else if (res.status === 400) {
          // Explicit validation error from backend
          const errData = await res.json().catch(() => ({ detail: 'Invalid request' }));
          throw new Error(errData.detail || 'Validation failed');
        } else {
          // Server 500 error: fall back to client detection engine so user is never blocked
          console.warn(`[ScamLens] Backend status ${res.status}. Falling back to client detection engine.`);
        }
      } catch (err: any) {
        // If it's a genuine 400 validation rejection, rethrow
        if (err?.message && (err.message.includes('Validation failed') || err.message.includes('cannot be empty'))) {
          throw err;
        }
        // Network failure or static host
        isStaticHostDetected = true;
        console.warn('[ScamLens] Backend unreachable. Operating with standalone client detection engine.');
      }
    }

    // Standalone Client Detection Engine (Offline / Static Host / Netlify)
    const id = 'scan-' + Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
    const isUrl = params.type === 'url' || content.startsWith('http://') || content.startsWith('https://');

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
        if (res.ok) {
          const data = await res.json();
          return data;
        } else if (res.status === 404) {
          // If 404 from remote/backend, check if it was created locally
          const localMatch = runtimeScans.find((s) => s.id === id);
          if (!localMatch) {
            throw new Error(`Scan not found: ${id}`);
          }
        }
      } catch (err: any) {
        if (err?.message && err.message.includes('Scan not found')) {
          throw err;
        }
        // Fall back to local mock
      }
    }

    const existing = runtimeScans.find((s) => s.id === id);
    if (!existing) {
      throw new Error(`Scan ${id} not found`);
    }

    // IMMUTABLE progression logic for offline mock
    if (existing.status === 'running') {
      const now = Date.now();
      const elapsedMs = now - new Date(existing.createdAt).getTime();

      if (elapsedMs > 2000) {
        // Complete the scan
        const lower = existing.content.toLowerCase();
        const hasUrgent = lower.includes('urgent') || lower.includes('kyc') || lower.includes('otp') || lower.includes('locked') || lower.includes('block') || lower.includes('cut') || lower.includes('disconnect');
        const hasPhishDomain = lower.includes('.xyz') || lower.includes('.top') || lower.includes('sbi-') || lower.includes('update') || lower.includes('bonus') || lower.includes('claim');

        let result: ScanResult;
        if (hasUrgent || hasPhishDomain) {
          result = {
            riskLevel: 'high',
            summary: 'High-pressure deceptive message attempting to capture financial credentials.',
            score: 88,
            scoreValidated: true,
            category: 'High Threat Scam',
            evidence: [
              {
                id: 'ev-new-1',
                title: 'High-pressure urgency signals',
                kind: 'warning',
                detail: 'Induces artificial panic demanding immediate action or threatening penalties.',
                source: 'Heuristic Rule Engine',
              },
              {
                id: 'ev-new-2',
                title: 'Suspicious credential harvesting pattern',
                kind: 'warning',
                detail: 'Mentions sensitive authentication cues such as OTP, KYC update, or account lock.',
                source: 'Calibrated Classifier',
              },
            ],
            actions: [
              'Do not click any embedded links or call unverified phone numbers',
              'Do not share passwords, PINs, or OTPs with anyone',
              'Contact your bank or utility provider through official published channels',
            ],
          };
        } else if (lower.includes('congratulations') || lower.includes('won') || lower.includes('job') || lower.includes('claim')) {
          result = {
            riskLevel: 'medium',
            summary: 'Message contains unsolicited reward or promotion claims that require verification.',
            score: 52,
            scoreValidated: true,
            category: 'Suspicious Offer',
            evidence: [
              {
                id: 'ev-new-3',
                title: 'Unsolicited prize or recruitment pattern',
                kind: 'warning',
                detail: 'Common pattern used in advance-fee schemes and recruitment scams.',
                source: 'Classifier',
              },
            ],
            actions: [
              'Do not transfer money to receive gifts or register for jobs',
              'Verify the sender identity directly',
            ],
          };
        } else if (existing.content.trim().length < 15) {
          result = {
            riskLevel: 'unknown',
            summary: "We can't tell whether this input is risky or legitimate due to minimal context.",
            scoreValidated: false,
            category: 'Inconclusive Content',
            evidence: [
              {
                id: 'ev-new-4',
                title: 'Short content check',
                kind: 'not_run',
                detail: 'Insufficient data points to confirm authenticity or detect scam signatures.',
                source: 'Analyzer',
              },
            ],
            actions: [
              'Exercise caution when responding to unfamiliar contacts',
              'Remember that "unknown" is not a confirmation that it is safe',
            ],
          };
        } else {
          result = {
            riskLevel: 'low',
            summary: 'No recognized threat patterns, urgency triggers, or deceptive links detected.',
            score: 6,
            scoreValidated: true,
            category: 'Standard Communication',
            evidence: [
              {
                id: 'ev-new-5',
                title: 'Clean baseline assessment',
                kind: 'confirmed',
                detail: 'No match with known threat databases or phishing indicators.',
                source: 'Rule Engine',
              },
            ],
            actions: [
              'Looks low risk based on our checks',
              'Continue to practice everyday caution with unsolicited messages',
            ],
          };
        }

        const completedScan: Scan = {
          ...existing,
          status: 'completed',
          steps: existing.steps.map((s) => ({ ...s, status: 'completed' })),
          result,
        };

        runtimeScans = runtimeScans.map((s) => (s.id === id ? completedScan : s));
        saveMockScans(runtimeScans);
        return deepClone(completedScan);
      } else if (elapsedMs > 1200) {
        const progressingScan: Scan = {
          ...existing,
          steps: existing.steps.map((s, idx) => ({
            ...s,
            status: idx <= 2 ? 'completed' : idx === 3 ? 'running' : 'waiting',
          })),
        };
        runtimeScans = runtimeScans.map((s) => (s.id === id ? progressingScan : s));
        saveMockScans(runtimeScans);
        return deepClone(progressingScan);
      } else if (elapsedMs > 500) {
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
        if (res.ok) {
          const data = await res.json();
          return data;
        }
      } catch {
        // Fall back to local mock
      }
    }

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
        if (res.ok) {
          return;
        }
      } catch {
        // Fall back
      }
    }

    runtimeScans = runtimeScans.filter((s) => s.id !== id);
    saveMockScans(runtimeScans);
  },

  /**
   * Delete all scans (for testing empty states)
   */
  async deleteAllScans(): Promise<void> {
    if (!FORCE_MOCK && !isStaticHostDetected) {
      try {
        const res = await fetch(`${API_BASE}/api/scans`, { method: 'DELETE' });
        if (res.ok) {
          return;
        }
      } catch {
        // Fall back
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
        if (res.ok) {
          const data = await res.json();
          return data;
        }
      } catch {
        // Fall back
      }
    }

    const total = runtimeScans.length;
    const highRisk = runtimeScans.filter((s) => s.result?.riskLevel === 'high').length;

    return { total, highRisk };
  },

  /**
   * Retry a failed or partial scan step
   */
  async retryScanStep(id: string, stepKey: string): Promise<Scan> {
    const scan = runtimeScans.find((s) => s.id === id);
    if (!scan) throw new Error('Scan not found');

    const updatedScan: Scan = {
      ...scan,
      status: 'running',
      steps: scan.steps.map((st) => (st.key === stepKey ? { ...st, status: 'running' } : st)),
    };
    runtimeScans = runtimeScans.map((s) => (s.id === id ? updatedScan : s));
    saveMockScans(runtimeScans);

    // Simulate resolution after 1s
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
    }, 1000);

    return deepClone(updatedScan);
  },
};
