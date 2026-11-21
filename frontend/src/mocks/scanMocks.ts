import { Scan, ScanStats } from '../types';

export const INITIAL_MOCK_SCANS: Scan[] = [
  {
    id: 'scan-mock-1',
    type: 'text',
    title: 'Urgent SBI OTP verification request',
    content: 'Dear Customer, your SBI account has been locked. Please update your KYC immediately at http://sbi-kyc-update.me/login or call 9876543210. Do not share your OTP.',
    createdAt: '2026-11-20T14:32:00Z',
    status: 'completed',
    steps: [
      { key: 'extract', label: 'Extract content', status: 'completed' },
      { key: 'patterns', label: 'Check patterns', status: 'completed' },
      { key: 'reputation', label: 'Check URL reputation', status: 'completed' },
      { key: 'evidence', label: 'Combine evidence', status: 'completed' },
      { key: 'report', label: 'Prepare report', status: 'completed' }
    ],
    result: {
      riskLevel: 'high',
      summary: 'Fake bank message impersonating SBI and asking for sensitive credentials.',
      score: 92,
      scoreValidated: true, // Honesty rule: validated score
      category: 'Banking / KYC Fraud',
      evidence: [
        {
          id: 'ev-1',
          title: 'Threat database match',
          kind: 'confirmed',
          detail: 'Domain sbi-kyc-update.me is listed on OpenPhish and verified blocklists.',
          source: 'OpenPhish Threat Feed'
        },
        {
          id: 'ev-2',
          title: 'Urgent account lockout threat',
          kind: 'warning',
          detail: 'Message claims your account has been locked to induce panic and immediate compliance.',
          source: 'Heuristic Rule Engine'
        },
        {
          id: 'ev-3',
          title: 'Unofficial contact mobile number',
          kind: 'warning',
          detail: 'Requests communication via an unverified personal 10-digit mobile number.',
          source: 'Heuristic Rule Engine'
        }
      ],
      actions: [
        'Do not click the link or reply to the sender',
        'Do not share your OTP, PIN, password, or Aadhaar number',
        'Verify your account status exclusively via official bank net-banking or mobile app',
        'Report this message to your local cyber helpline'
      ],
      providerDetails: {
        modelScore: 94,
        ruleScore: 90,
        openPhishMatch: true,
        patternsDetected: ['Fake KYC', 'Account Lockout', 'Unofficial Domain']
      }
    }
  },
  {
    id: 'scan-mock-2',
    type: 'url',
    title: 'Suspicious reward portal link',
    content: 'http://claim-festive-bonus-now.xyz/spin',
    createdAt: '2026-11-19T10:15:00Z',
    status: 'completed',
    steps: [
      { key: 'extract', label: 'Extract content', status: 'completed' },
      { key: 'patterns', label: 'Check patterns', status: 'completed' },
      { key: 'reputation', label: 'Check URL reputation', status: 'completed' },
      { key: 'evidence', label: 'Combine evidence', status: 'completed' },
      { key: 'report', label: 'Prepare report', status: 'completed' }
    ],
    result: {
      riskLevel: 'medium',
      summary: 'Unverified website with high-pressure reward hooks and non-standard domain registry.',
      score: 58,
      scoreValidated: true,
      category: 'Prize / Lottery Lure',
      evidence: [
        {
          id: 'ev-201',
          title: 'Unverified domain registry',
          kind: 'warning',
          detail: 'Domain has no legitimate commercial history and uses a disposable .xyz top-level domain.',
          source: 'Structural URL Inspection'
        },
        {
          id: 'ev-202',
          title: 'Deceptive path parameters',
          kind: 'warning',
          detail: 'URL path uses game / spin lottery keywords typically associated with deposit traps.',
          source: 'Pattern Matching Engine'
        }
      ],
      actions: [
        'Avoid submitting any personal or bank information on this website',
        'Do not pay any advance fee or registration charge to claim prizes',
        'Close the browser tab and verify through official brand channels'
      ]
    }
  },
  {
    id: 'scan-mock-3',
    type: 'text',
    title: 'Food delivery confirmation notification',
    content: 'Your Swiggy order #98214 from Pizza Hut has been picked up by delivery partner Ramesh. Track live in the Swiggy app.',
    createdAt: '2026-11-18T19:45:00Z',
    status: 'completed',
    steps: [
      { key: 'extract', label: 'Extract content', status: 'completed' },
      { key: 'patterns', label: 'Check patterns', status: 'completed' },
      { key: 'reputation', label: 'Check URL reputation', status: 'completed' },
      { key: 'evidence', label: 'Combine evidence', status: 'completed' },
      { key: 'report', label: 'Prepare report', status: 'completed' }
    ],
    result: {
      riskLevel: 'low',
      summary: 'Standard service fulfillment notification with no suspicious links, demands, or credential requests.',
      score: 4,
      scoreValidated: true,
      category: 'Service Notification',
      evidence: [
        {
          id: 'ev-301',
          title: 'No malicious indicators detected',
          kind: 'confirmed',
          detail: 'Contains no urgent threats, no external links, and requests no payment or OTP.',
          source: 'Calibrated Classifier Engine'
        }
      ],
      actions: [
        'No immediate risk indicators found',
        'Always verify orders directly through the official app rather than unknown links'
      ]
    }
  },
  {
    id: 'scan-mock-4',
    type: 'text',
    title: 'Short greeting from unknown number',
    content: 'Hi, are you free this afternoon?',
    createdAt: '2026-11-17T11:20:00Z',
    status: 'completed',
    steps: [
      { key: 'extract', label: 'Extract content', status: 'completed' },
      { key: 'patterns', label: 'Check patterns', status: 'completed' },
      { key: 'reputation', label: 'Check URL reputation', status: 'completed' },
      { key: 'evidence', label: 'Combine evidence', status: 'completed' },
      { key: 'report', label: 'Prepare report', status: 'completed' }
    ],
    result: {
      riskLevel: 'unknown',
      summary: "We can't tell whether this message is malicious or benign because it contains too little context.",
      scoreValidated: false, // Honesty rule: No numeric score for unknown!
      category: 'Ambiguous / Inconclusive',
      evidence: [
        {
          id: 'ev-401',
          title: 'Insufficient text context',
          kind: 'not_run',
          detail: 'The message is very short and does not contain any links, phone numbers, or clear fraud keywords.',
          source: 'Content Analyzer'
        }
      ],
      actions: [
        'Treat with caution if sent from an unfamiliar sender or international country code',
        'Do not click any links or send money if they follow up asking for help or offering jobs',
        'Remember that an "unknown" rating is not a guarantee of safety'
      ]
    }
  },
  {
    id: 'scan-mock-5',
    type: 'url',
    title: 'Unreachable web destination check',
    content: 'http://internal-corp-test-portal-7721.local:8080/auth',
    createdAt: '2026-11-16T08:12:00Z',
    status: 'partial',
    steps: [
      { key: 'extract', label: 'Extract content', status: 'completed' },
      { key: 'patterns', label: 'Check patterns', status: 'completed' },
      { key: 'reputation', label: 'Check URL reputation', status: 'failed', detail: 'DNS resolution timed out' },
      { key: 'evidence', label: 'Combine evidence', status: 'completed' },
      { key: 'report', label: 'Prepare report', status: 'completed' }
    ],
    result: {
      riskLevel: 'unknown',
      summary: 'Partial check completed. External reputation checks could not connect to verify this address.',
      scoreValidated: false,
      isPartial: true,
      category: 'Incomplete Inspection',
      evidence: [
        {
          id: 'ev-501',
          title: 'Reputation database lookup unreachable',
          kind: 'not_run',
          detail: 'The domain uses an internal or local address that could not be evaluated by external threat feeds.',
          source: 'DNS Resolver'
        },
        {
          id: 'ev-502',
          title: 'Non-standard port detected',
          kind: 'warning',
          detail: 'Destination specifies explicit port 8080.',
          source: 'Structural URL Inspection'
        }
      ],
      actions: [
        'Retry check when you have an active internet connection',
        'Do not enter company credentials into non-HTTPS or non-standard port websites'
      ]
    }
  }
];

export function getInitialStats(): ScanStats {
  return {
    total: INITIAL_MOCK_SCANS.length,
    highRisk: INITIAL_MOCK_SCANS.filter(s => s.result?.riskLevel === 'high').length
  };
}
