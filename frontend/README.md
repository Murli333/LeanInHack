# 🛡️ ScamLens — Frontend Web & Mobile PWA

> **Tagline:** *"Detect the scam. Understand the risk. Stay protected."*  
> **Tech Stack:** React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router, Lucide Icons, Vite PWA.  
> **Modes:** Full Responsive Web + Installable Mobile PWA (iOS / Android / Desktop).

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Node.js `v18+` or `v20+` or `v24+`
- npm `v9+` or `v11+`

### 2. Installation
```bash
cd frontend
npm install
```

### 3. Run Development Server
```bash
npm run dev
# Opens on http://localhost:3000
```

### 4. Build for Production & PWA
```bash
npm run build
npm run preview
```

---

## ⚙️ Environment Variables & Configuration

Create or modify `.env` in `frontend/`:

```ini
# When true (default), uses the client-side mock adapter with 5 reference scans
# When false, connects to the FastAPI backend API at /api/scans
VITE_USE_MOCK=true
```

---

## 🎨 Dual Theming System (Light & Dark)

ScamLens supports three theme modes:
1. **System (Default):** Automatically matches your OS / device preference and updates live via `window.matchMedia`.
2. **Light Mode:** Crisp, clean styling with high-contrast text (`#0B1220`) on soft background (`#F5F7FB`).
3. **Dark Mode:** Deep navy background (`#05080F`), navy card surfaces (`#0E1626`), and ambient danger halos.

### Zero-Flash Implementation
An inline script in `index.html` reads the saved `localStorage` choice (`scamlens-theme`) before the first paint, eliminating any flash of the wrong theme on page load. Native controls, form inputs, and browser scrollbars automatically synchronize via the CSS `color-scheme` property and `<meta name="theme-color">`.

---

## 🚩 Feature Flags (`src/config/flags.ts`)

Per the **Honesty Rules**, unfinished or unvalidated inputs are never faked:

```typescript
export const FEATURES = {
  screenshot: false, // Set to true to enable full screenshot OCR upload flow
  qr: false,         // Set to true to enable QR code scanning
  audio: false,      // Set to true to enable audio recording check
  investigation: false // Set to true to view deep technical provider traces
};
```

When flags are `false`, chips display a calm `Soon` tag, panels explain that the feature is undergoing verification, and check buttons remain disabled.

---

## 🌍 Regional Cyber Helpline Configuration (`src/config/regions.ts`)

ScamLens supports region-specific cyber helpline numbers and reporting portals:
- **India (IN - Default):** Call `1930` or visit `cybercrime.gov.in`
- **United States (US):** Call `1-877-FTC-HELP` or visit `ReportFraud.ftc.gov`
- **United Kingdom (UK):** Call `0300 123 2040` or visit `actionfraud.police.uk`
- **Global:** Generic *"Contact your bank or local authority directly"*

Users can change their region anytime under the **Profile & Settings** tab.

---

## 🧭 Routes & Screen Architecture

| Route | Purpose | Key Components |
|:---|:---|:---|
| `/welcome` | First-time visitor onboarding | Hero title, 3-step How It Works, privacy commitment |
| `/home` | Main dashboard | "Hello! 👋", huge "Tap here to check" pill, real-data stats, recent checks |
| `/scan` | Content submission | Horizontally scrollable chips (Text, Link, Screenshot, QR, Audio), input cards, desktop two-column layout |
| `/scan/:id/progress` | Live 5-step stepper | Extract content, Check patterns, Check URL reputation, Combine evidence, Prepare report |
| `/report/:id` | Detailed verification report | Qualitative risk meter, "Why it was flagged" evidence rows, "Stay safe" actions, defang link toggle |
| `/report/:id/investigation` | Deep technical inspection | Flagged behind `FEATURES.investigation` (Later release) |
| `/history` | Local scan repository | Search bar, filters by type and risk level, single & bulk deletion |
| `/profile` | User preferences | Segmented ThemeToggle, region selector, data privacy controls |
| `/dev/components` | UI Component Gallery | Comprehensive test gallery showing all components in all states across both themes |

---

## 🧪 Verification & Acceptance Checklist

- [x] Text and link checking work end-to-end: submit, watch live step progress, inspect report, reopen from history.
- [x] Screenshot, QR, and Audio cannot be submitted while flags are false and display honest "Coming soon" explanations.
- [x] No fake percentage-risk bars anywhere. 3-segment qualitative meter (Low / Medium / High) used exclusively.
- [x] "Safe" is never used as an absolute guarantee. "Looks low risk" and "We can't tell" are used instead.
- [x] System / Light / Dark modes all work, persist across reloads, update live on OS changes, with zero theme flash.
- [x] Status colors pass WCAG AA contrast (4.5:1 min) in both themes.
- [x] Responsive on mobile (<768px with fixed bottom bar), tablet (640px centered), and desktop (>=1024px with left sidebar nav and two-column scan/report).
- [x] Tested at 320px, 360px, 390px, 768px, 1024px, 1280px, and 1920px viewports without horizontal scroll.
- [x] Home stats come strictly from real stored data (checks done and high-risk found).
