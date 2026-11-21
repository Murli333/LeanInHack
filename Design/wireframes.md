# 📱 ScamLens Wireframes & User Journey Flows

## 1. Mobile-First Screen Flow (Primary Citizen Journey)

```
+----------------------------------------+
|  [⚡ ScamLens]            [Mode Toggle] |
|  AI Scam Shield v2.1      [● Backend]  |
+----------------------------------------+
| Quick Test Scenarios:                  |
| [Electricity 🔴] [SBI KYC 🔴] [HDFC 🟢]|
+----------------------------------------+
|  +----------------------------------+  |
|  | [ Text / SMS ] [ URL ] [ Image ] |  |
|  |----------------------------------|  |
|  | Paste suspicious message here... |  |
|  |                                  |  |
|  | [ 🔍 Analyze Threat ]            |  |
|  +----------------------------------+  |
|                                        |
|  ====================================  |
|               SCAN RESULT              |
|  ====================================  |
|             /-----------\              |
|            /     89%     \             |
|           |  HIGH THREAT  |            |
|            \  (CRITICAL) /             |
|             \-----------/              |
|                                        |
|  Verdict: 🔴 HIGH RISK SCAM            |
|  Category: Electricity Disconnection   |
|                                        |
|  [ Detected Evidence ]                 |
|  • Fake emergency cutoff (9:30 PM)     |
|  • Suspicious unofficial mobile number |
|  • Calibrated ML confidence: 91.4%     |
|                                        |
|  [ Recommended Actions ]               |
|  [ 📞 Call 1930 Helpline ]             |
|  [ 🌐 Open cybercrime.gov.in ]         |
|  [ 📋 Share Alert with Family ]        |
+----------------------------------------+
```

---

## 2. Multimodal Screenshot Inspection Flow

```
User selects "Image / Screenshot"
       │
       ▼
Dropzone active: "Drag & drop screenshot or tap to upload"
       │
       ▼
Client-side preview rendered + File size / mime type verified
       │
       ▼
Image sent to OCR pipeline (Tesseract OCR / EasyOCR backend)
       │
       ├─► [SUCCESS]: Extracted text previewed below image
       │               Proceeds to hybrid scoring engine
       │
       └─► [FAILURE / UNREADABLE]:
               Verdict: ❓ Unknown
               Message: "Image text could not be extracted"
               Tip: "Please paste text directly or check lighting"
               (Prevents false-safe loophole!)
```

---

## 3. Desktop Responsive Layout

On wide screens ($\ge 1024\text{px}$), the application shifts from the single-column mobile view to a dual-pane operations dashboard:
- **Left Column (50%):** Multimodal Input Suite (Text / URL / Image Dropzone + Live Config toggles).
- **Right Column (50%):** Real-time Verdict Card, SVG Risk Gauge, Detailed Feature Attribution, and Action Center.
- **Top Navigation Bar:** Persistent status pills, latency counter (ms), and quick scenario switcher.
