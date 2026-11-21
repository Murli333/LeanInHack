"""
ScamLens Autonomous Cybersecurity Investigation Agent (Member 1: Data & ML)
Implements Agentic AI for digital scam intelligence:
- Autonomous Multi-Tool Orchestration (NLP Model, URL Model, Heuristic Signatures, IOC Extraction)
- Tool-Result Schema Validation and Provenance Tracking
- Step-by-Step Investigation Trace (ReAct / Chain-of-Thought)
- Multi-Source Evidence Synthesis & Cross-Corroboration
- Grounded Evidence-Based Scoring (Probabilistic Fusion)
- Context-Aware Remediation Advisory
"""
import os
import re
import sys
import json
import datetime
from typing import Dict, Any, List, Optional

# Adjust system path to import local modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
MODELS_DIR = os.path.join(BASE_DIR, "models")
for p in [SRC_DIR, MODELS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from predictor import ScamLensPredictor


class ToolExecutionError(Exception):
    """Raised when a sub-tool returns invalid or malformed output."""
    pass


class ScamInvestigatorAgent:
    """
    Autonomous Cybersecurity Agent for Fraud Investigation.
    Orchestrates specialized tools, reasons over multimodal evidence,
    validates tool provenance, and produces an actionable threat intelligence report.
    """

    def __init__(self, models_dir: Optional[str] = None):
        self.predictor = ScamLensPredictor(models_dir=models_dir)
        self.agent_name = "ScamLens Cyber-Investigation Agent v2.1"
        self.version = "2.1.0"
        
        # Indian Cyber Crime Modus Operandi Threat Signatures
        self.threat_signatures = {
            "digital_arrest": {
                "name": "Digital Arrest / Law Enforcement Impersonation",
                "keywords": ["cbi", "police", "customs", "narcotics", "digital arrest", "skype", "warrant", "illegal parcel", "mumbai airport", "court", "remand"],
                "modus_operandi": "Threatens victim with fake arrest warrants or seized contraband parcels and demands video interrogation on Skype/WhatsApp to extort money.",
                "legal_fact": "Law enforcement agencies (Police, CBI, ED, Customs) NEVER conduct trials, arrest warrants, or interrogations via Skype or WhatsApp.",
                "evidence_weight": 0.90
            },
            "electricity_disconnection": {
                "name": "Urgent Electricity Disconnection Threat",
                "keywords": ["electricity", "power", "disconnected", "power office", "bill unpaid", "officer at", "previous month bill", "bijli"],
                "modus_operandi": "Pressures consumers with immediate nighttime power disconnection to induce panic and force calls to fraudulent personal mobile numbers.",
                "legal_fact": "Power discoms never send disconnection SMS with personal 10-digit mobile numbers for bill clearance.",
                "evidence_weight": 0.85
            },
            "fake_kyc": {
                "name": "Fake Banking / KYC Block Threat",
                "keywords": ["kyc", "yono", "pan card", "card blocked", "debit card", "unblock", "suspended", "aadhaar mismatch", "re-kyc"],
                "modus_operandi": "Tricks victims into downloading rogue APKs or entering netbanking credentials on lookalike domains to bypass 2FA.",
                "legal_fact": "Banks never require customers to update KYC via third-party APK downloads or unofficial websites.",
                "evidence_weight": 0.88
            },
            "upi_collect_fraud": {
                "name": "UPI Collect Request / PIN Phishing",
                "keywords": ["upi collect", "enter upi pin", "receive money", "refund of rs", "cashback", "lottery", "scratch card"],
                "modus_operandi": "Deceptively sends a UPI Collect Request claiming the victim is receiving money, whereas entering the UPI PIN deducts money from their account.",
                "legal_fact": "You NEVER need to enter your UPI PIN to receive money in your bank account.",
                "evidence_weight": 0.92
            },
            "part_time_task_scam": {
                "name": "Part-Time Task & Job Investment Fraud",
                "keywords": ["part-time work", "work from home", "earn rs", "liking youtube", "telegram @", "daily income", "part time", "review task"],
                "modus_operandi": "Offers easy money for small tasks (YouTube likes, Google ratings), builds trust with small payouts, then freezes deposits in high-yield investment traps.",
                "legal_fact": "Legitimate employers never recruit for daily payouts via Telegram or demand deposit money for task unlocking.",
                "evidence_weight": 0.80
            },
            "customs_parcel_scam": {
                "name": "Overseas Parcel Customs Clearance Scam",
                "keywords": ["customs", "parcel", "fedex", "dhl", "clearance fee", "consignment", "airport hub", "unpaid duty"],
                "modus_operandi": "Claims a valuable foreign parcel is stuck at airport customs and demands online clearance duty transfers.",
                "legal_fact": "Customs duties are never collected via personal bank accounts or instant UPI links.",
                "evidence_weight": 0.82
            }
        }

    # =================================================================
    # TOOL CAPABILITIES WITH PROVENANCE AND SCHEMA VALIDATION
    # =================================================================

    def tool_inspect_nlp_semantics(self, text: str) -> Dict[str, Any]:
        """Tool: Evaluates semantic patterns using calibrated text model."""
        res = self.predictor.predict_text(text)
        # Schema validation
        required_keys = {"verdict", "risk_score", "raw_ml_score", "confidence", "reasons"}
        if not required_keys.issubset(res.keys()):
            raise ToolExecutionError(f"NLP tool returned incomplete schema. Missing: {required_keys - set(res.keys())}")
        return {
            "tool_name": "tool_inspect_nlp_semantics",
            "provenance": "Calibrated TF-IDF + Logistic Regression Model v2.1",
            "execution_status": "SUCCESS",
            "output": res
        }

    def tool_inspect_url_infrastructure(self, url: str) -> Dict[str, Any]:
        """Tool: Inspects URL structural features using calibrated URL model."""
        res = self.predictor.predict_url(url)
        required_keys = {"verdict", "risk_score", "raw_ml_score", "confidence", "reasons", "features"}
        if not required_keys.issubset(res.keys()):
            raise ToolExecutionError(f"URL tool returned incomplete schema. Missing: {required_keys - set(res.keys())}")
        return {
            "tool_name": "tool_inspect_url_infrastructure",
            "provenance": "Calibrated Random Forest Ensemble (28 features) v2.1",
            "execution_status": "SUCCESS",
            "output": res
        }

    def tool_match_cybercrime_signatures(self, text: str) -> Dict[str, Any]:
        """Tool: Identifies known Indian cybercrime modus operandi."""
        lower = text.lower()
        matched = []
        for key, sig in self.threat_signatures.items():
            hit_count = sum(1 for kw in sig["keywords"] if kw in lower)
            if hit_count >= 2:
                matched.append({
                    "id": key,
                    "name": sig["name"],
                    "hits": hit_count,
                    "modus_operandi": sig["modus_operandi"],
                    "legal_fact": sig["legal_fact"],
                    "evidence_weight": sig["evidence_weight"]
                })
        return {
            "tool_name": "tool_match_cybercrime_signatures",
            "provenance": "Indian Cybercrime Modus Operandi Knowledge Base",
            "execution_status": "SUCCESS",
            "output": matched
        }

    def tool_extract_embedded_indicators(self, text: str) -> Dict[str, Any]:
        """Tool: Extracts actionable IOCs (URLs, phone numbers, UPI references, amounts)."""
        urls = self.predictor.preprocessor.url_pattern.findall(text)
        phones = self.predictor.preprocessor.phone_pattern.findall(text)
        currencies = self.predictor.preprocessor.currency_pattern.findall(text)
        return {
            "tool_name": "tool_extract_embedded_indicators",
            "provenance": "Regex-Based Lexical Entity Extractor",
            "execution_status": "SUCCESS",
            "output": {
                "extracted_urls": urls,
                "extracted_phones": phones,
                "extracted_currencies": currencies
            }
        }

    # =================================================================
    # AUTONOMOUS AGENT INVESTIGATION ENGINE (ReAct Orchestration)
    # =================================================================

    def investigate(self, text: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes an autonomous, multi-step investigation loop:
        1. Observation -> Collect inputs, check emptiness, extract IOCs.
        2. Tool Invocation -> Run NLP semantics, URL inspector, signature matcher with provenance.
        3. Deliberation -> Chain-of-thought evidence cross-corroboration.
        4. Threat Verdict -> Grounded probabilistic evidence fusion.
        5. Action Plan -> Context-aware remediation and reporting guidance.
        """
        investigation_log: List[str] = []
        structured_trace: List[Dict[str, Any]] = []

        # Step 0: Input validation
        has_text = text is not None and bool(str(text).strip())
        has_url = url is not None and bool(str(url).strip())

        if not has_text and not has_url:
            return {
                "agent_name": self.agent_name,
                "verdict": "Unknown",
                "status_color": "gray",
                "icon": "❓",
                "risk_score": 0,
                "is_empty": True,
                "investigation_trace": ["🔍 [AGENT OBSERVATION] No input provided. Standing by."],
                "structured_trace": [],
                "deliberation_summary": ["No actionable text or URL was submitted."],
                "reasons": ["No content provided for analysis."],
                "safety_tips": ["Paste a suspicious message, link, or phone number to start an investigation."]
            }

        investigation_log.append("🔍 [AGENT OBSERVATION] Initializing threat investigation on incoming input.")
        
        # Step 1: IOC Extraction
        extracted_iocs = {"extracted_urls": [], "extracted_phones": [], "extracted_currencies": []}
        if has_text:
            ioc_result = self.tool_extract_embedded_indicators(text)
            extracted_iocs = ioc_result["output"]
            structured_trace.append(ioc_result)
            
            if extracted_iocs["extracted_urls"] and not has_url:
                url = extracted_iocs["extracted_urls"][0]
                has_url = True
                investigation_log.append(f"🔗 [IOC EXTRACTION] Extracted embedded URL from text: '{url}'")
            if extracted_iocs["extracted_phones"]:
                investigation_log.append(f"📞 [IOC EXTRACTION] Extracted phone numbers: {extracted_iocs['extracted_phones']}")

        # Step 2: Tool Invocations
        text_findings = None
        if has_text:
            investigation_log.append("🧠 [TOOL CALL] Invoking 'tool_inspect_nlp_semantics' on message text...")
            nlp_result = self.tool_inspect_nlp_semantics(text)
            text_findings = nlp_result["output"]
            structured_trace.append(nlp_result)
            investigation_log.append(
                f"   -> Result: Semantic Scam Probability: {text_findings['risk_score']}% | "
                f"Verdict: {text_findings['verdict']} | Confidence: {text_findings['confidence']}"
            )

        url_findings = None
        if has_url:
            investigation_log.append(f"🌐 [TOOL CALL] Invoking 'tool_inspect_url_infrastructure' on target URL: '{url}'...")
            url_result = self.tool_inspect_url_infrastructure(url)
            url_findings = url_result["output"]
            structured_trace.append(url_result)
            investigation_log.append(
                f"   -> Result: Infrastructure Phishing Score: {url_findings['risk_score']}% | "
                f"Verdict: {url_findings['verdict']} | Confidence: {url_findings['confidence']}"
            )

        signature_matches = []
        if has_text:
            investigation_log.append("📑 [TOOL CALL] Invoking 'tool_match_cybercrime_signatures' against known fraud patterns...")
            sig_result = self.tool_match_cybercrime_signatures(text)
            signature_matches = sig_result["output"]
            structured_trace.append(sig_result)
            if signature_matches:
                names = [s["name"] for s in signature_matches]
                investigation_log.append(f"   -> Confirmed Threat Signatures: {', '.join(names)}")
            else:
                investigation_log.append("   -> No specific high-threat institutional signatures triggered.")

        # Step 3: Agent Deliberation & Chain of Thought
        investigation_log.append("⚖️ [AGENT DELIBERATION] Synthesizing cross-evidence from NLP, URL infrastructure, and signatures...")
        deliberation_notes: List[str] = []
        
        # Case A: Signature Match Corroboration
        if signature_matches:
            top_sig = signature_matches[0]
            deliberation_notes.append(
                f"Attack modus operandi matches '{top_sig['name']}'. {top_sig['legal_fact']}"
            )
            
        # Case B: Multi-Vector Confirmation (Text + URL)
        if text_findings and url_findings:
            if url_findings["risk_score"] >= 70:
                deliberation_notes.append(
                    f"Malicious link detected. Attributes: {', '.join(url_findings['reasons'][:2])}."
                )
            if text_findings["risk_score"] >= 70 and url_findings["risk_score"] >= 70:
                deliberation_notes.append(
                    "Coordinated phishing delivery confirmed: Text urgency is crafted specifically to coerce clicks on the malicious link."
                )

        # Case C: Benign Transaction Verification
        if text_findings and text_findings["verdict"] == "Safe" and (not url_findings or url_findings["verdict"] == "Safe"):
            deliberation_notes.append(
                "Cross-evaluation shows legitimate service or personal communication indicators without credential harvesting pressure."
            )

        # Step 4: Grounded Threat Verdict Calculation (Evidence-Weighted Fusion)
        evidence_scores = []
        weights = []
        
        if text_findings:
            evidence_scores.append(text_findings["risk_score"])
            weights.append(0.40)
            
        if url_findings:
            evidence_scores.append(url_findings["risk_score"])
            weights.append(0.45)
            
        if signature_matches:
            top_weight = max(s["evidence_weight"] for s in signature_matches)
            evidence_scores.append(int(top_weight * 100))
            weights.append(0.35)
            
        if weights:
            normalized_weights = [w / sum(weights) for w in weights]
            final_score = int(round(sum(s * w for s, w in zip(evidence_scores, normalized_weights))))
        else:
            final_score = 0

        # Verdict assignment based on grounded threshold
        if final_score >= 70:
            verdict = "Scam"
            status_color = "red"
            icon = "🚨"
            safety_tips = [
                "Do NOT click any links, open APKs, or reply to this message.",
                "Never share your OTP, UPI PIN, or bank passwords with anyone.",
                "Report this immediately on the National Cyber Crime Reporting Portal at https://cybercrime.gov.in or call helpline 1930."
            ]
        elif final_score >= 40:
            verdict = "Suspicious"
            status_color = "amber"
            icon = "⚠️"
            safety_tips = [
                "Verify independently via the official bank or service provider app before taking any action.",
                "Do not approve any UPI collect requests or transfer token booking amounts.",
                "Check sender identity carefully."
            ]
        else:
            verdict = "Safe"
            status_color = "green"
            icon = "✅"
            safety_tips = [
                "Message looks typical of normal communications.",
                "Always remember that genuine organizations will never ask for your PIN or password."
            ]

        # Combine all unique reasons
        candidate_reasons = deliberation_notes
        if text_findings:
            candidate_reasons.extend(text_findings["reasons"])
        if url_findings:
            candidate_reasons.extend(url_findings["reasons"])
            
        all_reasons = list(dict.fromkeys([
            r for r in candidate_reasons 
            if "normal conversational" not in r.lower() or verdict == "Safe"
        ]))

        investigation_log.append(f"🎯 [DECISION] Final Consolidated Verdict: {verdict} ({final_score}%)")

        return {
            "agent_name": self.agent_name,
            "version": self.version,
            "verdict": verdict,
            "status_color": status_color,
            "icon": icon,
            "risk_score": final_score,
            "is_empty": False,
            "investigation_trace": investigation_log,
            "structured_trace": structured_trace,
            "deliberation_summary": deliberation_notes,
            "reasons": all_reasons,
            "safety_tips": safety_tips,
            "matched_signatures": signature_matches,
            "iocs_extracted": extracted_iocs,
            "nlp_analysis": text_findings,
            "url_analysis": url_findings
        }


def get_agent() -> ScamInvestigatorAgent:
    """Convenience factory function."""
    return ScamInvestigatorAgent()


if __name__ == "__main__":
    print("=== Testing ScamLens Autonomous Cyber-Investigation Agent v2.1 ===")
    agent = ScamInvestigatorAgent()
    sample = (
        "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized "
        "at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype: https://cbi-investigation.top/court"
    )
    report = agent.investigate(text=sample)
    print("\n--- INVESTIGATION TRACE ---")
    for step in report["investigation_trace"]:
        print(step)
    print("\n--- AGENT VERDICT ---")
    print(f"Verdict: {report['verdict']} {report['icon']} ({report['risk_score']}%)")
    print("\n--- EXPLAINABLE REASONS ---")
    for r in report["reasons"]:
        print(f"• {r}")
    print("\n--- SAFETY TIPS ---")
    for tip in report["safety_tips"]:
        print(f"-> {tip}")
