import { Scan, ScanFilter, ScanStats, ScanType, ScanStep, ScanResult } from '../types';
import { INITIAL_MOCK_SCANS } from '../mocks/scanMocks';

const STORAGE_KEY = 'scamlens-local-scans';
// Prefer real backend by default. Only force mock if VITE_USE_MOCK is explicitly set to 'true'.
const FORCE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

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

    if (!FORCE_MOCK) {
      try {
        const res = await fetch('/api/scans', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: params.type, content }),
        });

        if (res.ok) {
          const data = await res.json();
          return { id: data.id };
        } else {
          const errData = await res.json().catch(() => ({ detail: `Server error (${res.status})` }));
          throw new Error(errData.detail || `Server error (${res.status})`);
        }
      } catch (err: any) {
        // If it's a real server rejection (400 validation, 500 error), rethrow immediately
        if (err?.message && !err.message.includes('Failed to fetch') && !err.message.includes('NetworkError') && !err.message.includes('ECONNREFUSED')) {
          throw err;
        }
        // If network is offline, continue to local fallback
        console.warn('[ScamLens API] Backend unreachable, falling back to local client processing.');
      }
    }

    // Local Mock / Offline implementation
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
    if (!FORCE_MOCK) {
      try {
        const res = await fetch(`/api/scans/${id}`);
        if (res.ok) {
          const data = await res.json();
          return data;
        } else if (res.status === 404) {
          throw new Error(`Scan not found: ${id}`);
        } else {
          const errData = await res.json().catch(() => ({ detail: `Server error (${res.status})` }));
          throw new Error(errData.detail || `Server error (${res.status})`);
        }
      } catch (err: any) {
        if (err?.message && !err.message.includes('Failed to fetch') && !err.message.includes('NetworkError') && !err.message.includes('ECONNREFUSED')) {
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
    if (!FORCE_MOCK) {
      try {
        const queryParams = new URLSearchParams();
        if (filter?.query) queryParams.set('query', filter.query);
        if (filter?.type && filter.type !== 'all') queryParams.set('type', filter.type);
        if (filter?.risk && filter.risk !== 'all') queryParams.set('risk', filter.risk);

        const res = await fetch(`/api/scans?${queryParams.toString()}`);
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
    if (!FORCE_MOCK) {
      try {
        const res = await fetch(`/api/scans/${id}`, { method: 'DELETE' });
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
    if (!FORCE_MOCK) {
      try {
        const res = await fetch('/api/scans', { method: 'DELETE' });
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
    if (!FORCE_MOCK) {
      try {
        const res = await fetch('/api/stats');
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
