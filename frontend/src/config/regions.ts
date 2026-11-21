import { RegionConfig } from '../types';

export const SUPPORTED_REGIONS: Record<string, RegionConfig> = {
  IN: {
    code: 'IN',
    name: 'India',
    helpline: '1930',
    portalName: 'cybercrime.gov.in',
    portalUrl: 'https://cybercrime.gov.in',
    instructionText: 'Call 1930 or visit cybercrime.gov.in'
  },
  US: {
    code: 'US',
    name: 'United States',
    helpline: '1-877-382-4357',
    portalName: 'ReportFraud.ftc.gov',
    portalUrl: 'https://reportfraud.ftc.gov',
    instructionText: 'Call 1-877-FTC-HELP or report to ReportFraud.ftc.gov'
  },
  UK: {
    code: 'UK',
    name: 'United Kingdom',
    helpline: '0300 123 2040',
    portalName: 'actionfraud.police.uk',
    portalUrl: 'https://www.actionfraud.police.uk',
    instructionText: 'Call 0300 123 2040 or report to Action Fraud'
  },
  GLOBAL: {
    code: 'GLOBAL',
    name: 'Other / International',
    helpline: '',
    portalName: 'Local Cyber Authorities',
    portalUrl: '#',
    instructionText: 'Contact your bank or local cyber authority immediately'
  }
};

export const DEFAULT_REGION_CODE = 'IN';

export function getActiveRegion(): RegionConfig {
  try {
    const saved = localStorage.getItem('scamlens-region');
    if (saved && SUPPORTED_REGIONS[saved]) {
      return SUPPORTED_REGIONS[saved];
    }
  } catch (e) {
    // ignore
  }
  return SUPPORTED_REGIONS[DEFAULT_REGION_CODE];
}

export function setActiveRegion(code: string): void {
  try {
    localStorage.setItem('scamlens-region', code);
  } catch (e) {
    // ignore
  }
}
