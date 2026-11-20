"""
ScamLens Autonomous Cybersecurity Investigation Agent
Implements Agentic AI for digital scam intelligence:
- Autonomous Multi-Tool Orchestration (NLP Model, URL Model, Heuristic Signatures, Reputation)
- Step-by-Step Investigation Trace (ReAct / Chain-of-Thought)
- Multi-Source Evidence Synthesis & Cross-Corroboration
- Context-Aware Remediation Advisory
"""
import os
import re
import json
from typing import Dict, Any, List, Optional

# Adjust system path to import local modules
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
MODELS_DIR = os.path.join(BASE_DIR, "models")
for p in [SRC_DIR, MODELS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from predictor import ScamLensPredictor


class ScamInvestigatorAgent:
    """
    Autonomous Cybersecurity Agent for Fraud Investigation.
    Orchestrates specialized tools, reasons over multimodal evidence,
    and produces an actionable threat intelligence report.
    """

    def __init__(self, models_dir: Optional[str] = None):
        self.predictor = ScamLensPredictor(models_dir=models_dir)
        self.agent_name = "ScamLens Cyber-Investigation Agent v1.0"
        
        # Indian Cyber Crime Modus Operandi Signatures
        self.threat_signatures = {
            "digital_arrest": {
                "name": "Digital Arrest / Agency Impersonation",
                "keywords": ["cbi", "police", "customs", "narcotics", "digital arrest", "skype", "warrant", "illegal parcel", "mumbai airport"],
                "modus_operandi": "Threatens victim with fake arrest warrants or seized contraband parcels and demands video interrogation on Skype/WhatsApp to extort money.",
                "legal_fact": "Law enforcement agencies (Police, CBI, ED, Customs) NEVER conduct trials, arrest warrants, or interrogations via Skype or WhatsApp."
            },
            "electricity_disconnection": {
                "name": "Urgent Electricity Disconnection Threat",
                "keywords": ["electricity", "power", "disconnected", "power office", "bill unpaid", "officer at", "previous month bill"],
                "modus_operandi": "Pressures consumers with immediate nighttime power disconnection to induce panic and force calls to fraudulent personal mobile numbers.",
                "legal_fact": "Power discoms never send disconnection SMS with personal 10-digit mobile numbers for bill clearance."
            },
            "fake_kyc": {
                "name": "Fake Banking / KYC Block Threat",
                "keywords": ["kyc", "yono", "pan card", "card blocked", "debit card", "unblock", "suspended", "aadhaar mismatch"],
                "modus_operandi": "Tricks victims into downloading rogue APKs or entering netbanking credentials on lookalike domains to bypass 2FA.",
                "legal_fact": "Banks never require customers to update KYC via third-party APK downloads or unofficial websites."
            },
            "upi_collect_fraud": {
                "name": "UPI Collect Request / PIN Phishing",
                "keywords": ["upi collect", "enter upi pin", "receive money", "refund of rs", "cashback", "lottery"],
                "modus_operandi": "Deceptively sends a UPI Collect Request claiming the victim is receiving money, whereas entering the UPI PIN deducts money from their account.",
                "legal_fact": "You NEVER need to enter your UPI PIN to receive money in your bank account."
            },
            "part_time_task_scam": {
                "name": "Part-Time Task & Job Investment Fraud",
                "keywords": ["part-time work", "work from home", "earn rs", "liking youtube", "telegram @", "daily income", "part time"],
                "modus_operandi": "Offers easy money for small tasks (YouTube likes, Google ratings), builds trust with small payouts, then freezes deposits in high-yield investment traps.",
                "legal_fact": "Legitimate employers never recruit for daily payouts via Telegram or demand deposit money for task unlocking."
            }
        }

    # ==========================================
    # TOOL CAPABILITIES AVAILABLE TO THE AGENT
    # ==========================================

    def tool_inspect_nlp_semantics(self, text: str) -> Dict[str, Any]:
        """Tool: Evaluates semantic patterns using text_model.joblib."""
        return self.predictor.predict_text(text)

    def tool_inspect_url_infrastructure(self, url: str) -> Dict[str, Any]:
        """Tool: Inspects URL structural features using url_model.joblib."""
        return self.predictor.predict_url(url)

    def tool_match_cybercrime_signatures(self, text: str) -> List[Dict[str, str]]:
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
                    "legal_fact": sig["legal_fact"]
                })
        return matched

    def tool_extract_embedded_indicators(self, text: str) -> Dict[str, List[str]]:
        """Tool: Extracts actionable IOCs (URLs, phone numbers, UPI references)."""
        urls = self.predictor.preprocessor.url_pattern.findall(text)
        phones = self.predictor.preprocessor.phone_pattern.findall(text)
        currencies = self.predictor.preprocessor.currency_pattern.findall(text)
        return {
            "extracted_urls": urls,
            "extracted_phones": phones,
            "extracted_currencies": currencies
        }

    # ==========================================
    # AUTONOMOUS AGENT INVESTIGATION ENGINE
    # ==========================================

    def investigate(self, text: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes an autonomous, multi-step investigation loop:
        1. Observation -> Collect inputs and extract Indicators of Compromise (IOCs).
        2. Tool Invocation -> Run ML text model, URL inspector, and signature matcher.
        3. Deliberation -> Chain-of-thought evidence synthesis.
        4. Threat Verdict -> Calibrated risk scoring.
        5. Action Plan -> Prescriptive remediation and emergency contact generation.
        """
        investigation_log = []
        investigation_log.append("🔍 [AGENT OBSERVATION] Initializing threat investigation on incoming input.")
        
        # Step 1: IOC Extraction
        extracted_iocs = {"extracted_urls": [], "extracted_phones": [], "extracted_currencies": []}
        if text:
            extracted_iocs = self.tool_extract_embedded_indicators(text)
            if extracted_iocs["extracted_urls"] and not url:
                url = extracted_iocs["extracted_urls"][0]
                investigation_log.append(f"🔗 [IOC EXTRACTION] Extracted embedded URL from text: '{url}'")
            if extracted_iocs["extracted_phones"]:
                investigation_log.append(f"📞 [IOC EXTRACTION] Extracted contact phone/number: {extracted_iocs['extracted_phones']}")

        # Step 2: Tool Calls
        text_findings = None
        if text:
            investigation_log.append("🧠 [TOOL CALL] Invoking 'tool_inspect_nlp_semantics' on message text...")
            text_findings = self.tool_inspect_nlp_semantics(text)
            investigation_log.append(f"   -> Result: Semantic Scam Probability: {text_findings['risk_score']}% | Initial Verdict: {text_findings['verdict']}")

        url_findings = None
        if url:
            investigation_log.append(f"🌐 [TOOL CALL] Invoking 'tool_inspect_url_infrastructure' on target URL: '{url}'...")
            url_findings = self.tool_inspect_url_infrastructure(url)
            investigation_log.append(f"   -> Result: Infrastructure Phishing Score: {url_findings['risk_score']}% | Initial Verdict: {url_findings['verdict']}")

        signature_matches = []
        if text:
            investigation_log.append("📑 [TOOL CALL] Invoking 'tool_match_cybercrime_signatures' against known Indian fraud patterns...")
            signature_matches = self.tool_match_cybercrime_signatures(text)
            if signature_matches:
                names = [s["name"] for s in signature_matches]
                investigation_log.append(f"   -> Confirmed Threat Signatures: {', '.join(names)}")
            else:
                investigation_log.append("   -> No specific high-threat institutional signatures triggered.")

        # Step 3: Agent Deliberation & Chain of Thought
        investigation_log.append("⚖️ [AGENT DELIBERATION] Synthesizing cross-evidence from NLP, URL infrastructure, and signatures...")
        deliberation_notes = []
        
        # Case A: Signature Match
        if signature_matches:
            top_sig = signature_matches[0]
            deliberation_notes.append(
                f"Attack modus operandi matches '{top_sig['name']}'. {top_sig['legal_fact']}"
            )
            
        # Case B: Multi-Vector Confirmation (Text + URL)
        if text_findings and url_findings:
            if url_findings["risk_score"] >= 70:
                deliberation_notes.append(
                    f"High-threat malicious link detected. The infrastructure uses abnormal attributes: {', '.join(url_findings['reasons'][:2])}."
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

        # Step 4: Final Risk Assessment & Scoring
        combined_result = self.predictor.predict_combined(text=text, url=url)
        final_score = combined_result["risk_score"]
        
        # Elevate risk if high-severity signatures are confirmed
        if signature_matches and final_score < 75:
            final_score = max(final_score, 85)
            combined_result["verdict"] = "Scam"
            combined_result["status_color"] = "red"
            combined_result["icon"] = "🚨"

        combined_result["risk_score"] = final_score

        # Step 5: Synthesize Final Dossier
        all_reasons = list(dict.fromkeys(
            [d for d in deliberation_notes] + combined_result["reasons"]
        ))
        
        investigation_log.append(f"🎯 [DECISION] Final Consolidated Verdict: {combined_result['verdict']} ({combined_result['risk_score']}%)")

        return {
            "agent_name": self.agent_name,
            "verdict": combined_result["verdict"],
            "status_color": combined_result["status_color"],
            "icon": combined_result["icon"],
            "risk_score": final_score,
            "investigation_trace": investigation_log,
            "deliberation_summary": deliberation_notes,
            "reasons": all_reasons,
            "safety_tips": combined_result["safety_tips"],
            "matched_signatures": signature_matches,
            "iocs_extracted": extracted_iocs,
            "nlp_analysis": text_findings,
            "url_analysis": url_findings
        }


# Convenience factory
def get_agent() -> ScamInvestigatorAgent:
    return ScamInvestigatorAgent()


if __name__ == "__main__":
    print("=== Testing ScamLens Autonomous Cyber-Investigation Agent ===")
    agent = ScamInvestigatorAgent()
    sample = (
        "Delhi Police Cyber Cell: A parcel in your name containing illegal narcotics has been seized "
        "at Mumbai airport. Digital arrest warrant issued. Contact CBI Officer on Skype: http://cbi-investigation.top/court"
    )
    report = agent.investigate(text=sample)
    print("\n--- INVESTIGATION TRACE ---")
    for step in report["investigation_trace"]:
        print(step)
    print("\n--- AGENT VERDICT ---")
    print(f"Verdict: {report['verdict']} {report['icon']} ({report['risk_score']}%)")
    print("\n--- WHY WE THINK THIS (EXPLAINABLE REASONS) ---")
    for r in report["reasons"]:
        print(f"• {r}")
    print("\n--- SAFETY RECOMMENDATIONS ---")
    for tip in report["safety_tips"]:
        print(f"-> {tip}")
