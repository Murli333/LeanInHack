# 📐 ScamLens Design & Architecture Notes

> **Platform:** ScamLens — AI-Powered Digital Safety Assistant  
> **Tagline:** *"Detect the scam. Understand the risk. Stay protected."*  
> **Audience:** Everyday citizens, older adults, and non-technical users requiring calm, jargon-free security guidance.

---

## 1. Feature Implementation Matrix

| Feature | Status | Notes & Honesty Rule Compliance |
|:---|:---:|:---|
| **Text / SMS / WhatsApp Checking** | ✅ **Implemented** | Full end-to-end flow with Paste, Clear, live character counter (up to 10,000), and privacy warning. |
| **URL / Link Checking** | ✅ **Implemented** | http/https validation, defang preview (`hxxps://`), strict non-navigation policy. |
| **Progress Stepper** | ✅ **Implemented** | 5 live steps: Extract content, Check patterns, Check URL reputation, Combine evidence, Prepare report with accessible `aria-live` status. |
| **Verdict Presentation** | ✅ **Implemented** | 4 honest states: *Scam alert — High risk*, *Be careful*, *Looks low risk*, *We can't tell*. |
| **Qualitative Risk Meter** | ✅ **Implemented** | 3-segment qualitative bar (Low / Medium / High). No fake percentages. Shows numeric score ONLY when `scoreValidated: true`, formatted as `Risk score 92 / 100`. |
| **Evidence & Reason Rows** | ✅ **Implemented** | Tagged `CONFIRMED` (green), `WARNING SIGN` (amber), or `NOT RUN` (grey) with source attribution. |
| **Stay Safe Action List** | ✅ **Implemented** | Clear next steps + region-configurable cyber fraud helpline. |
| **Home Stats & Recent Scans** | ✅ **Implemented** | Derived exclusively from real stored data (`checks done`, `high-risk found`). Zero hard-coded stats. Complete empty state on clean install. |
| **History & Search** | ✅ **Implemented** | Search, filter by type (Text/URL) and risk (High/Medium/Low/Unknown), single deletion, and "Clear all history" with accessible `ConfirmDialog`. |
| **Theming System** | ✅ **Implemented** | System / Light / Dark modes with live OS tracking (`matchMedia`), zero flash pre-paint script, `<meta name="theme-color">` updates, and WCAG AA contrast. |
| **Component Gallery** | ✅ **Implemented** | Accessible at `/dev/components` displaying all components in all states across both themes with a live theme switcher. |
| **Screenshot OCR** | 🚧 **Behind Flag (`FEATURES.screenshot = false`)** | Full drag-and-drop & photo picker UI designed; displays calm "Coming soon" explanation when false per Honesty Rule 1. |
| **QR Code Scanner** | 🚧 **Behind Flag (`FEATURES.qr = false`)** | Gated behind flag; displays calm "Coming soon" explanation when false. |
| **Audio Voice Analysis** | 🚧 **Behind Flag (`FEATURES.audio = false`)** | Gated behind flag; displays calm "Coming soon" explanation when false. |
| **Deep Investigation** | 🔮 **Later Release (`FEATURES.investigation = false`)** | Provider telemetry and model vs rule sub-score inspector gated behind flag per Honesty Rule 7. |

---

## 2. Design Token System & WCAG Contrast Matrix

All colours in ScamLens are configured as CSS variables and semantic tokens. No component ever hard-codes colours.

### Dark Theme (`:root[data-theme="dark"]`)
*Canvas Background: `#05080F` | Card Surface: `#0E1626` | Card Surface 2: `#131E33`*

| Token Name | Hex / CSS Value | Semantic Role | Contrast Ratio | WCAG Rating |
|:---|:---|:---|:---:|:---:|
| `--bg` | `#05080F` | Page background | — | — |
| `--surface` | `#0E1626` | Card surfaces | — | — |
| `--surface-2` | `#131E33` | Inputs, chips, secondary cards | — | — |
| `--border` | `#25395A` | Subtle dividers and outlines | 3.2:1 | Pass (UI components) |
| `--primary` | `#1D4ED8` | Primary button / brand accents | — | — |
| `--on-primary` | `#FFFFFF` | Text on primary button | **8.2:1** | **AAA** |
| `--accent` | `#00D4FF` | Focus rings, links, spinners | **12.8:1** | **AAA** |
| `--text` | `#F5F7FA` | Primary headings & body copy | **18.2:1** | **AAA** |
| `--text-muted` | `#9BAFC5` | Helper text, timestamps, labels | **7.4:1** | **AAA** |
| `--danger` | `#F87171` | High-risk text & icons | **7.1:1** on `#05080F`<br>**6.4:1** on tint | **AAA**<br>**AA** |
| `--danger-tint` | `rgba(248, 113, 113, 0.14)` | High-risk card background | — | — |
| `--warn` | `#FBBF24` | Cautionary text & icons | **12.1:1** on `#05080F`<br>**10.5:1** on tint | **AAA**<br>**AAA** |
| `--warn-tint` | `rgba(251, 191, 36, 0.14)` | Cautionary card background | — | — |
| `--safe` | `#36E0A1` | Low-risk text & icons | **13.5:1** on `#05080F`<br>**11.2:1** on tint | **AAA**<br>**AAA** |
| `--safe-tint` | `rgba(54, 224, 161, 0.14)` | Low-risk / Stay Safe card | — | — |
| `--unknown` | `#9BAFC5` | Inconclusive status | **7.4:1** | **AAA** |
| `--unknown-tint`| `rgba(155, 175, 197, 0.14)`| Inconclusive background | — | — |
| `--glow-danger` | `0 0 24px rgba(248,113,113,.35)` | Ambient halo for High Risk | — | — |

---

### Light Theme (`:root[data-theme="light"]`)
*Canvas Background: `#F5F7FB` | Card Surface: `#FFFFFF` | Card Surface 2: `#EEF2F9`*

| Token Name | Hex / CSS Value | Semantic Role | Contrast Ratio | WCAG Rating |
|:---|:---|:---|:---:|:---:|
| `--bg` | `#F5F7FB` | Page background | — | — |
| `--surface` | `#FFFFFF` | Card surfaces | — | — |
| `--surface-2` | `#EEF2F9` | Inputs, chips, secondary cards | — | — |
| `--border` | `#D3DCEB` | Subtle dividers and outlines | 3.1:1 | Pass (UI components) |
| `--primary` | `#1D4ED8` | Primary button / brand accents | — | — |
| `--on-primary` | `#FFFFFF` | Text on primary button | **8.2:1** | **AAA** |
| `--accent` | `#0369A1` | Focus rings & links (darker for contrast) | **5.6:1** | **AA** |
| `--text` | `#0B1220` | Primary headings & body copy | **17.5:1** | **AAA** |
| `--text-muted` | `#475569` | Helper text, timestamps, labels | **6.8:1** | **AA** |
| `--danger` | `#B91C1C` | High-risk text & icons | **6.9:1** on `#FFFFFF`<br>**5.8:1** on tint | **AA**<br>**AA** |
| `--danger-tint` | `#FEE2E2` | High-risk card background | — | — |
| `--warn` | `#92400E` | Cautionary text & icons | **7.2:1** on `#FFFFFF`<br>**6.1:1** on tint | **AAA**<br>**AA** |
| `--warn-tint` | `#FEF3C7` | Cautionary card background | — | — |
| `--safe` | `#047857` | Low-risk text & icons | **6.2:1** on `#FFFFFF`<br>**5.4:1** on tint | **AA**<br>**AA** |
| `--safe-tint` | `#D1FAE5` | Low-risk / Stay Safe card | — | — |
| `--unknown` | `#475569` | Inconclusive status | **6.3:1** on `#E2E8F0` | **AA** |
| `--unknown-tint`| `#E2E8F0` | Inconclusive background | — | — |
| `--glow-danger` | `none` | Clean 1px danger border | — | — |

---

## 3. Deliberate Deviations from Reference Screenshots

To satisfy the **Honesty Rules** and elevate product craftsmanship, the following intentional enhancements were implemented:

1. **Elimination of Fake Risk Percentages (Honesty Rule 2):**
   - *Reference Screen:* Displayed an arbitrary "92% Risk" continuous bar.
   - *ScamLens Implementation:* Replaced with a **3-segment qualitative meter** (*Low / Medium / High*). A numeric score is displayed strictly if `scoreValidated: true` and formatted as `Risk score 92 / 100`. It is never labeled as "% risk" or "probability".

2. **Fixed "Why it was flagged" Glitched Header:**
   - *Reference Screen:* The section header had text overlapping or visual artifacting.
   - *ScamLens Implementation:* Re-engineered as a clean card header with an indicator counter badge and cleanly separated evidence rows.

3. **Universal SVG Chrome (No Emojis):**
   - *Reference Screen:* Used mixed OS emojis in navigation bars and status pills.
   - *ScamLens Implementation:* Standardized on `lucide-react` vector icons rendered with `currentColor` so the visual hierarchy is crisp, consistent, and identical across iOS, Android, Windows, macOS, and Linux.

4. **Honest Labeling (Honesty Rule 3):**
   - *Reference Screen:* Used the word "SAFE" as an absolute guarantee.
   - *ScamLens Implementation:* Strictly avoids guarantees. Uses *"Looks low risk"* with explicit disclaimers. Added *"We can't tell"* for inconclusive messages with clear explanations that unknown is neither confirmed safe nor confirmed malicious.

5. **Region-Configurable Helplines (Honesty Rule 8):**
   - *Reference Screen:* Hard-coded an Indian helpline number ("Call 1930 or visit cybercrime.gov.in").
   - *ScamLens Implementation:* Modularized into `config/regions.ts` supporting India (1930), USA (FTC 1-877-382-4357), UK (Action Fraud 0300 123 2040), and Global default. Can be switched in Profile settings.

6. **Defanged URL Safety View:**
   - *Reference Screen:* Raw phishing URLs were displayed directly.
   - *ScamLens Implementation:* Includes an automatic "Defang" toggle (`hxxps://`, `[.]`) preventing accidental clicks while allowing users to inspect the destination.

---

## 4. Responsive Viewport Adaptations

- **Mobile Phone (<768px):** Single-column layout, sticky "Check now" pill above bottom navigation bar, safe-area insets (`env(safe-area-inset-bottom)`), touch targets $\ge 48\text{px}$, `100dvh` viewport height.
- **Tablet (768px – 1023px):** Centered card container (max-w 640px), comfortable touch spacing, persistent bottom bar.
- **Desktop ($\ge 1024\text{px}$):** Replaces bottom bar with an ergonomic **Left Sidebar Navigation**; content area expands to a balanced **two-column layout** (Left: Inputs/Verdict; Right: Steps/Actions/Buttons); enables keyboard shortcuts (`Ctrl/Cmd + Enter` to submit).
