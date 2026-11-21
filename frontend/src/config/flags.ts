import { FeatureFlags } from '../types';

/**
 * HONESTY RULE 1 & 7:
 * Screenshot, QR Code, and Audio sit behind feature flags, all false by default.
 * Investigation is also false by default (Later release).
 * When false, the UI honestly informs the user that these capabilities are coming soon.
 */
export const FEATURES: FeatureFlags = {
  screenshot: false, // Set to true to test full image upload & OCR flow
  qr: false,         // Set to true to test QR scanning flow
  audio: false,      // Set to true to test audio transcript flow
  investigation: false // Set to true to access detailed provider inspection
};
