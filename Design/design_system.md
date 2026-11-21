# 🎨 ScamLens Design System Specification

## 1. Color Palette & Semantic Tokens

The ScamLens interface relies on a strict semantic color system designed for high contrast, psychological reassurance, and immediate danger signaling.

### Primary & Neutral Palette
| Token | Hex Value | Usage |
|-------|-----------|-------|
| `--bg-main` | `#0B0F19` | Dark mode background / canvas |
| `--surface-card` | `#111827` | Card and modal surface background |
| `--surface-elevated` | `#1F2937` | Input containers, chips, and elevated panels |
| `--border-subtle` | `#374151` | Subtle divider lines and input borders |
| `--text-primary` | `#F9FAFB` | Primary headings and key labels |
| `--text-secondary` | `#9CA3AF` | Subtitles, helper text, and timestamps |
| `--brand-primary` | `#3B82F6` | Primary CTAs, active states, and accents |
| `--brand-glow` | `rgba(59, 130, 246, 0.25)` | Subtle ambient backlights |

### Semantic Verdict Tokens
| Verdict | Hex Code | Background Tint | Border | Icon | Psychological Cue |
|---------|----------|-----------------|--------|------|-------------------|
| **Safe** | `#10B981` (Emerald) | `rgba(16, 185, 129, 0.12)` | `#059669` | 🟢 Shield Check | Reassuring, legitimate communication |
| **Suspicious** | `#F59E0B` (Amber) | `rgba(245, 158, 11, 0.12)` | `#D97706` | 🟡 Warning Triangle | Caution, unverified links or urgency |
| **Scam / Fraud** | `#EF4444` (Crimson) | `rgba(239, 68, 68, 0.15)` | `#DC2626` | 🔴 Alert Hexagon | Immediate danger, active threat |
| **Unknown / Error** | `#6B7280` (Gray) | `rgba(107, 114, 128, 0.12)` | `#4B5563` | ❓ Help Circle | Inconclusive, unreadable screenshot |

---

## 2. Typography

- **Headings & UI:** `Inter`, `SF Pro Display`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif`
  - Clean, neutral, high legibility on mobile screens.
- **Data & Scores:** `JetBrains Mono`, `ui-monospace`, `monospace`
  - Used for risk percentages (e.g. `87%`), URLs, timestamps, and model metrics.

### Type Scale
| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 (Brand Header) | 28px (1.75rem) | 800 (Bold) | 1.2 |
| H2 (Verdict Title) | 22px (1.375rem) | 700 (Bold) | 1.3 |
| Body / Inputs | 15px (0.9375rem) | 400 (Regular) | 1.5 |
| Micro-copy / Chips | 12px (0.75rem) | 500 (Medium) | 1.4 |

---

## 3. UI Component Hierarchy

1. **Top Navigation Bar:**
   - ScamLens logo + badge (`v2.1.0 AI Engine`).
   - Device Switcher: Toggle between Mobile Phone Mockup and Full Desktop View.
   - Status Indicator: Backend Live / Standalone Heuristic fallback.

2. **Quick Test Chips (1-Click Demo):**
   - Electricity Disconnection (🔴 Scam)
   - SBI KYC Freeze (🔴 Scam)
   - UPI Reverse Charge (🔴 Scam)
   - Legitimate Bank Alert (🟢 Safe)
   - Ambiguous Delivery (🟡 Suspicious)

3. **Multimodal Input Suite:**
   - Tab 1: Plain Text / SMS / WhatsApp Message Input.
   - Tab 2: URL / Domain Quick Inspect.
   - Tab 3: Screenshot Dropzone (Drag-and-drop with client-side OCR preview).

4. **Dynamic Risk Meter (Gauge):**
   - Circular SVG / semi-arc gauge animating from 0% to calculated risk score.
   - Live color shift based on score: Green (0–30) $\to$ Amber (31–69) $\to$ Red (70–100).

5. **Evidence & Breakdown Panels:**
   - Deterministic Rule Matches (e.g., "Demands urgent UPI PIN").
   - Machine Learning Confidence & Uncertainty interval.
   - URL Reputation & Structural Anomaly tags.

6. **Action Center (Remediation):**
   - 1-Click Dial 1930 Cyber Fraud Helpline.
   - Report to National Cyber Crime Reporting Portal (`cybercrime.gov.in`).
   - Copy safety explanation to WhatsApp to alert family members.
