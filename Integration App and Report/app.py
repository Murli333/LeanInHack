"""
ScamLens — Member 3: Streamlit Application (app.py)
====================================================
Mobile-first, accessible Streamlit UI that integrates:
  • Member 1 — ML models  (text_model.joblib, url_model.joblib)
  • Member 2 — Heuristic signals & blocklist  (signals.py)
  • Member 3 — Weighted scoring engine  (scoring.py → analyze())

Follows Member 4's design specs:
  - Three-state colour cards  (Safe / Suspicious / Scam)
  - Risk meter  (0–100 %)
  - "Why we think this" plain-language reasons
  - Screenshot preview with OCR text
  - Safety tips box
  - Accessibility icons  (✅ ⚠️ 🚨)  — no colour-only signals

Run:
    cd "Integration App and Report"
    streamlit run app.py
"""

import os
import sys
import streamlit as st

# ── Path bootstrap ──────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)

for _p in [
    _THIS_DIR,
    _PROJECT_ROOT,
    os.path.join(_PROJECT_ROOT, "Data And ML", "models"),
    os.path.join(_PROJECT_ROOT, "Data And ML", "src"),
    os.path.join(_PROJECT_ROOT, "Detection Logic"),
]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from scoring import analyze


# ═══════════════════════════════════════════════════════════════════════
#  Streamlit page configuration
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ScamLens 🛡️",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Inject Member 4 colour palette & typography ───────────────────────
st.markdown("""
<style>
/* ---- Global fonts ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ---- Verdict cards ---- */
.verdict-safe       { background:#ECFDF5; border-left:6px solid #10B981;
                      border-radius:12px; padding:24px; margin:12px 0; }
.verdict-suspicious { background:#FFFBEB; border-left:6px solid #F59E0B;
                      border-radius:12px; padding:24px; margin:12px 0; }
.verdict-scam       { background:#FEF2F2; border-left:6px solid #EF4444;
                      border-radius:12px; padding:24px; margin:12px 0; }
.verdict-empty      { background:#F3F4F6; border-left:6px solid #9CA3AF;
                      border-radius:12px; padding:24px; margin:12px 0; }

.verdict-title { font-size:28px; font-weight:700; margin-bottom:4px; }
.risk-label    { font-size:16px; color:#6B7280; margin-bottom:16px; }

/* ---- Reason bullets ---- */
.reason-box  { background:#F9FAFB; border-radius:8px; padding:16px; margin:12px 0; }
.reason-item { font-size:15px; color:#374151; padding:4px 0; }

/* ---- Safety tips ---- */
.tips-box   { background:#EFF6FF; border-radius:8px; padding:16px; margin:12px 0; }
.tip-item   { font-size:14px; color:#1E40AF; padding:3px 0; }

/* ---- OCR preview ---- */
.ocr-box    { background:#F5F3FF; border-radius:8px; padding:16px; margin:12px 0; }

/* ---- Score details ---- */
.detail-row { font-size:13px; color:#6B7280; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  Header
# ═══════════════════════════════════════════════════════════════════════
st.markdown("# 🛡️ ScamLens")
st.markdown(
    "**AI-powered scam detector** — Paste a suspicious message, enter a link, "
    "or upload a screenshot. We'll tell you if it's safe, suspicious, or a scam."
)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════
#  Quick Demo Examples (For Hackathon Judges & Testing)
# ═══════════════════════════════════════════════════════════════════════
if "msg_val" not in st.session_state:
    st.session_state["msg_val"] = ""
if "url_val" not in st.session_state:
    st.session_state["url_val"] = ""

st.markdown("##### 🚀 Quick Demo Scenarios (One-Click Test)")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏦 Fake SBI KYC", use_container_width=True):
        st.session_state["msg_val"] = "Dear SBI Customer, your YONO account has been suspended due to pending KYC update. Please visit immediately to complete verification."
        st.session_state["url_val"] = "http://sbi-kyc-verify.top/sbi.apk"
        st.rerun()
    if st.button("💸 Fake UPI Collect", use_container_width=True):
        st.session_state["msg_val"] = "Dear Customer, you received UPI collect request of Rs 4999 from Amazon Pay. Enter your UPI PIN to receive money in your bank account."
        st.session_state["url_val"] = ""
        st.rerun()

with c2:
    if st.button("⚡ Electricity Threat", use_container_width=True):
        st.session_state["msg_val"] = "Urgent: Electricity power will be disconnected at 9:30 PM from power office because your previous month bill was not updated. Please immediately contact our electricity officer 9876543210."
        st.session_state["url_val"] = "http://electricity-bill-disconnection-alert.fit/pay"
        st.rerun()
    if st.button("✅ Genuine Bank OTP", use_container_width=True):
        st.session_state["msg_val"] = "Dear Customer, 849201 is your one time password (OTP) for SBI Internet Banking login. Valid for 3 mins. Never share OTP with anyone."
        st.session_state["url_val"] = ""
        st.rerun()

with c3:
    if st.button("👮 Digital Arrest", use_container_width=True):
        st.session_state["msg_val"] = "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype."
        st.session_state["url_val"] = ""
        st.rerun()
    if st.button("📦 Genuine Delivery", use_container_width=True):
        st.session_state["msg_val"] = "Dear Customer, your Swiggy order from Biryani Blues is out for delivery. Delivery partner Ravi will reach you shortly."
        st.session_state["url_val"] = ""
        st.rerun()

st.markdown("")

# ═══════════════════════════════════════════════════════════════════════
#  Input section
# ═══════════════════════════════════════════════════════════════════════
st.subheader("📝 What do you want to check?")
st.caption("Paste anything that looks suspicious, or click one of the quick scenarios above.")

message_input = st.text_area(
    "Message / SMS / WhatsApp text",
    value=st.session_state["msg_val"],
    height=130,
    placeholder="e.g.  Dear SBI Customer, your YONO account has been suspended…",
)

url_input = st.text_input(
    "🔗 Suspicious link (optional)",
    value=st.session_state["url_val"],
    placeholder="e.g.  http://sbi-kyc-verify.top/sbi.apk",
)

uploaded_image = st.file_uploader(
    "📷 Upload a screenshot (optional)",
    type=["png", "jpg", "jpeg", "webp"],
    help="We'll try to read the text from the image using OCR.",
)

st.markdown("")
check_clicked = st.button("🔍  Check for Scam", type="primary", use_container_width=True)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════
#  Analysis & result rendering
# ═══════════════════════════════════════════════════════════════════════
if check_clicked:
    # Validate at least some input
    has_input = bool(
        (message_input and message_input.strip())
        or (url_input and url_input.strip())
        or uploaded_image
    )
    if not has_input:
        st.warning("⚠️  Please enter a message, paste a link, or upload a screenshot first.")
        st.stop()

    # Show spinner while analysing
    with st.spinner("🔍 Analyzing — checking message patterns, URL reputation & scam signals…"):
        image_bytes = uploaded_image.read() if uploaded_image else None
        result = analyze(
            message_text=message_input if message_input and message_input.strip() else None,
            url=url_input if url_input and url_input.strip() else None,
            image_input=image_bytes,
        )

    verdict = result["verdict"]
    score   = result["risk_score"]
    color   = result["status_color"]
    icon    = result["icon"]
    reasons = result["reasons"]
    tips    = result["safety_tips"]
    details = result.get("details", {})

    # ── Verdict card ──────────────────────────────────────────────
    card_class = {
        "green": "verdict-safe",
        "amber": "verdict-suspicious",
        "red":   "verdict-scam",
    }.get(color, "verdict-empty")

    st.markdown(f"""
    <div class="{card_class}">
        <div class="verdict-title">{icon}  {verdict}</div>
        <div class="risk-label">Risk Score: {score}%</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Risk meter (Streamlit progress bar) ───────────────────────
    bar_color = "normal"
    if score >= 70:
        st.error(f"🚨 **Risk Level: {score}% — HIGH**")
    elif score >= 40:
        st.warning(f"⚠️ **Risk Level: {score}% — MODERATE**")
    else:
        st.success(f"✅ **Risk Level: {score}% — LOW**")
    st.progress(min(score, 100))

    # ── Why we think this ─────────────────────────────────────────
    if reasons:
        st.markdown("### 🧐 Why we think this")
        st.markdown('<div class="reason-box">', unsafe_allow_html=True)
        for r in reasons:
            st.markdown(f'<div class="reason-item">• {r}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Screenshot preview + OCR text ─────────────────────────────
    if uploaded_image:
        st.markdown("### 📸 Screenshot Preview")
        uploaded_image.seek(0)
        st.image(uploaded_image, use_container_width=True)
        ocr = details.get("ocr_extracted_text")
        if ocr:
            st.markdown('<div class="ocr-box">', unsafe_allow_html=True)
            st.markdown(f"**Text we read from the image:**\n\n{ocr}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ We couldn't extract readable text from this screenshot. "
                    "Try pasting the message text directly above.")

    # ── Safety tips ───────────────────────────────────────────────
    if tips:
        st.markdown("### 🛡️ Safety Tips")
        st.markdown('<div class="tips-box">', unsafe_allow_html=True)
        for t in tips:
            st.markdown(f'<div class="tip-item">{t}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Score breakdown (collapsed by default) ────────────────────
    with st.expander("📊 Detailed Score Breakdown"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Text ML Score", f"{details.get('text_ml_score', 0)}%")
            st.metric("URL ML Score",  f"{details.get('url_ml_score', 0)}%")
        with col2:
            st.metric("Text Rule Score", f"{details.get('text_rule_score', 0)}%")
            st.metric("URL Rule Score",  f"{details.get('url_rule_score', 0)}%")

        triggered = details.get("triggered_signals", [])
        if triggered:
            st.markdown(f"**Triggered Signals:** `{'`, `'.join(triggered)}`")
        if details.get("effective_url"):
            st.markdown(f"**Analysed URL:** `{details['effective_url']}`")

    st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
#  Footer — safety resources
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; padding:16px; color:#6B7280; font-size:13px;">
    🛡️ <strong>ScamLens</strong> — AI-Powered Digital Fraud Detection<br>
    Never share your OTP or PIN &nbsp;•&nbsp;
    Report fraud at <a href="https://cybercrime.gov.in" target="_blank">cybercrime.gov.in</a>
    or call <strong>1930</strong><br>
    <em>Built for LeanInHack 2026</em>
</div>
""", unsafe_allow_html=True)
