# ScamLens - Frontend Web & Mobile Application

> **Module:** Frontend User Interface  
> **Target Devices:** Mobile Phones (PWA / Responsive Shell) & Desktop Web Browsers  
> **Status:** ✅ Production Ready with Live FastAPI Integration and Offline Standalone Demo Mode  

---

## 📱 Features & Capabilities

1. **Dual-Mode Responsive Viewport:**
   - **Mobile Shell Mockup:** Provides an iOS/Android smartphone frame with status bar, touch-friendly 48px tap targets, and bottom navigation bar.
   - **Full Desktop View:** Seamlessly expands into a clean, card-based desktop web console via the topbar toggle.
2. **Multimodal Input Suite:**
   - **Text Messages:** Clean textarea for pasting SMS or WhatsApp messages.
   - **Target URLs:** Monospace input box for analyzing suspicious links and shorteners.
   - **Screenshot Uploads:** Drag-and-drop dropzone supporting image previews and OCR extraction.
3. **1-Click Quick Demo Chips:**
   - ⚡ Fake SBI YONO KYC
   - ⚡ Urgent Electricity Cutoff
   - ⚡ CBI Digital Arrest
   - ⚡ UPI Collect PIN Fraud
   - ⚡ Authentic SBI OTP
   - ⚡ Swiggy Food Delivery
4. **Three Distinct Outcome States (Color-Blind Accessible):**
   - **Safe (Green):** `✅ Safe` (0–39%), calm styling, why we think this, safety tips.
   - **Suspicious (Amber):** `⚠️ Suspicious` (40–69%), cautious styling, sender verification guidance.
   - **Scam (Crimson Red):** `🚨 Scam Alert` (70–100%), urgent styling, threat breakdown, and 1-click **Call 1930 Helpline** & **cybercrime.gov.in** reporting buttons.
5. **Local Scan History:**
   - Slide-out history drawer storing recent scans locally with timestamps and 1-click review.
6. **Zero-Setup Standalone Demo:**
   - Connects automatically to `http://localhost:8000/api/analyze` when the FastAPI backend is running.
   - If the backend is offline, falls back seamlessly to an internal intelligence engine so you can demo the frontend immediately in any browser by simply double-clicking `index.html`!

---

## 🚀 How to Run the Frontend

### Option A: Standalone in Browser (Instant)
Simply open `frontend/index.html` directly in any web browser (Chrome, Edge, Safari, Firefox).

### Option B: With Python HTTP Server
```bash
cd frontend
python -m http.server 3000
# Open http://localhost:3000 in your browser or mobile phone on the same Wi-Fi
```

### Option C: Connected with FastAPI Backend
```bash
# Terminal 1: Start Backend API
python backend/main.py

# Terminal 2: Serve Frontend
cd frontend
python -m http.server 3000
```
