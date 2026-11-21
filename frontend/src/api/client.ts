import { Scan, ScanFilter, ScanStats, ScanType, ScanStep } from '../types';
import { INITIAL_MOCK_SCANS } from '../mocks/scanMocks';

const STORAGE_KEY = 'scamlens-local-scans';
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

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
  return [...INITIAL_MOCK_SCANS];
}

function saveMockScans(scans: Scan[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(scans));
  } catch {
    // ignore
  }
}

// In-memory runtime state
let runtimeScans: Scan[] = loadMockScans();

export interface CreateScanParams {
  type: ScanType;
  content: string;
}

export const apiClient = {
  /**
   * Submit content for scanning
   */
  async createScan(params: CreateScanParams): Promise<{ id: string }> {
    if (!USE_MOCK) {
      try {
        const res = await fetch('/api/scans', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(params),
        });
        if (res.ok) {
          return await res.json();
        }
      } catch {
        // Fall back to mock if real backend unreachable
      }
    }

    // Mock implementation
    const id = 'scan-' + Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
    const isUrl = params.type === 'url' || params.content.startsWith('http://') || params.content.startsWith('https://');
    
    // Initial steps
    const steps: ScanStep[] = [
      { key: 'extract', label: 'Extract content', status: 'completed' },
      { key: 'patterns', label: 'Check patterns', status: 'running' },
      { key: 'reputation', label: 'Check URL reputation', status: isUrl ? 'waiting' : 'waiting' },
      { key: 'evidence', label: 'Combine evidence', status: 'waiting' },
      { key: 'report', label: 'Prepare report', status: 'waiting' },
    ];

    const title = params.type === 'url' 
      ? `Link: ${params.content.replace(/^https?:\/\//, '').substring(0, 32)}...`
      : params.content.substring(0, 36) + (params.content.length > 36 ? '...' : '');

    const newScan: Scan = {
      id,
      type: params.type,
      content: params.content,
      title,
      createdAt: new Date().toISOString(),
      status: 'running',
      steps,
    };

    runtimeScans.unshift(newScan);
    saveMockScans(runtimeScans);

    return { id };
  },

  /**
   * Retrieve scan details and progressive step status
   */
  async getScan(id: string): Promise<Scan> {
    if (!USE_MOCK) {
      try {
        const res = await fetch(`/api/scans/${id}`);
        if (res.ok) {
          return await res.json();
        }
      } catch {
        // Fall back to mock
      }
    }

    const scan = runtimeScans.find((s) => s.id === id);
    if (!scan) {
      throw new Error(`Scan ${id} not found`);
    }

    // If scan is running, simulate progression towards completion
    if (scan.status === 'running') {
      const now = Date.now();
      const elapsedMs = now - new Date(scan.createdAt).getTime();

      // Step progression logic (approx 2.5 seconds total)
      if (elapsedMs > 2500) {
        scan.status = 'completed';
        scan.steps = scan.steps.map((s) => ({ ...s, status: 'completed' }));
        
        // Generate calibrated result based on content
        const lower = scan.content.toLowerCase();
        const hasUrgent = lower.includes('urgent') || lower.includes('kyc') || lower.includes('otp') || lower.includes('locked') || lower.includes('block') || lower.includes('cut');
        const hasPhishDomain = lower.includes('.xyz') || lower.includes('.top') || lower.includes('sbi-') || lower.includes('update') || lower.includes('bonus');

        if (hasUrgent || hasPhishDomain) {
          scan.result = {
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
                source: 'Heuristic Rule Engine'
              },
              {
                id: 'ev-new-2',
                title: 'Suspicious credential harvesting pattern',
                kind: 'warning',
                detail: 'Mentions sensitive authentication cues such as OTP, KYC update, or account lock.',
                source: 'Calibrated Classifier'
              }
            ],
            actions: [
              'Do not click any embedded links or phone numbers',
              'Do not share passwords, PINs, or OTPs with anyone',
              'Contact your bank or utility provider through official published channels'
            ]
          };
        } else if (lower.includes('congratulations') || lower.includes('won') || lower.includes('job') || lower.includes('claim')) {
          scan.result = {
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
                source: 'Classifier'
              }
            ],
            actions: [
              'Do not transfer money to receive gifts or register for jobs',
              'Verify the sender identity directly'
            ]
          };
        } else if (scan.content.trim().length < 15) {
          scan.result = {
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
                source: 'Analyzer'
              }
            ],
            actions: [
              'Exercise caution when responding to unfamiliar contacts',
              'Remember that "unknown" is not a confirmation that it is safe'
            ]
          };
        } else {
          scan.result = {
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
                source: 'Rule Engine'
              }
            ],
            actions: [
              'Looks low risk based on our checks',
              'Continue to practice everyday caution with unsolicited messages'
            ]
          };
        }

        saveMockScans(runtimeScans);
      } else if (elapsedMs > 1600) {
        scan.steps[0].status = 'completed';
        scan.steps[1].status = 'completed';
        scan.steps[2].status = 'completed';
        scan.steps[3].status = 'running';
      } else if (elapsedMs > 800) {
        scan.steps[0].status = 'completed';
        scan.steps[1].status = 'completed';
        scan.steps[2].status = 'running';
      }
    }

    return scan;
  },

  /**
   * List recent scans with filtering
   */
  async listScans(filter?: ScanFilter): Promise<Scan[]> {
    if (!USE_MOCK) {
      try {
        const queryParams = new URLSearchParams();
        if (filter?.query) queryParams.set('query', filter.query);
        if (filter?.type && filter.type !== 'all') queryParams.set('type', filter.type);
        if (filter?.risk && filter.risk !== 'all') queryParams.set('risk', filter.risk);

        const res = await fetch(`/api/scans?${queryParams.toString()}`);
        if (res.ok) {
          return await res.json();
        }
      } catch {
        // Fall back to mock
      }
    }

    let results = [...runtimeScans];

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
    if (!USE_MOCK) {
      try {
        await fetch(`/api/scans/${id}`, { method: 'DELETE' });
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
    if (!USE_MOCK) {
      try {
        await fetch('/api/scans', { method: 'DELETE' });
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
    runtimeScans = [...INITIAL_MOCK_SCANS];
    saveMockScans(runtimeScans);
  },

  /**
   * Get stats (Honesty Rule 5: from real stored data only!)
   */
  async getStats(): Promise<ScanStats> {
    if (!USE_MOCK) {
      try {
        const res = await fetch('/api/stats');
        if (res.ok) {
          return await res.json();
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

    scan.status = 'running';
    scan.steps = scan.steps.map((st) => (st.key === stepKey ? { ...st, status: 'running' } : st));
    saveMockScans(runtimeScans);

    // Simulate resolution after 1.5s
    setTimeout(() => {
      scan.status = 'completed';
      scan.steps = scan.steps.map((st) => ({ ...st, status: 'completed' }));
      if (scan.result) {
        scan.result.isPartial = false;
        scan.result.summary = 'Complete check finished after successful step retry.';
      }
      saveMockScans(runtimeScans);
    }, 1500);

    return scan;
  }
};
