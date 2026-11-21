"""
ScamLens — Member 3: Weight-Tuning & Multi-Split Benchmark Suite
================================================================
Evaluates the unified analyze() function against Member 2's ground-truth
cases in Detection Logic/eval_cases.py (EVAL_CASES) with rigorous
tune / validation / test splits to avoid in-sample overfitting.

Phase 1 Hardening:
  - Fixed-seed stratified split: 60% Tune (21), 20% Validation (7), 20% Test (7)
  - Weights chosen strictly on Tune + Validation splits
  - Final metrics reported on the untouched Test split
  - Text-only, URL-only, and Combined modalities reported separately
  - Prominent small-sample warning
  - Auto-updates config/scoring.json and writes evaluation/benchmark_results.md
"""

import os
import re
import sys
import json
import random
from typing import List, Dict, Any

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_DETECTION_DIR = os.path.join(_PROJECT_ROOT, "Detection Logic")

for _p in [_THIS_DIR, _PROJECT_ROOT, _DETECTION_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scoring import ScamLensScoringEngine
from eval_cases import EVAL_CASES
from signals import _extract_urls


def stratified_split(cases: List[Dict[str, Any]], seed: int = 42):
    """
    Splits 35 cases into 60% Tune (21), 20% Validation (7), 20% Test (7)
    with balanced class proportions (Scam vs Safe).
    """
    scams = [c for c in cases if c.get("expected_verdict") in ("Scam", "Suspicious")]
    safes = [c for c in cases if c.get("expected_verdict") == "Safe"]

    rng = random.Random(seed)
    rng.shuffle(scams)
    rng.shuffle(safes)

    # Scams: 18 total -> 11 tune, 4 val, 3 test
    # Safes: 17 total -> 10 tune, 3 val, 4 test
    tune = scams[:11] + safes[:10]
    val = scams[11:15] + safes[10:13]
    test = scams[15:] + safes[13:]

    rng.shuffle(tune)
    rng.shuffle(val)
    rng.shuffle(test)

    return tune, val, test


def evaluate_split(engine: ScamLensScoringEngine, cases: List[Dict[str, Any]], mode: str = "combined") -> dict:
    """
    Evaluates engine on a given slice of cases under different input modes:
      - 'combined': full text + extracted URL + screenshot
      - 'text_only': text stripped of any embedded URLs
      - 'url_only': evaluated only on cases that contain a URL
    """
    tp = fp = tn = fn = 0
    rows = []

    for case in cases:
        raw_text = case.get("text", "")
        img = case.get("image_path")
        expected = case.get("expected_verdict")
        truth_is_scam = expected in ("Scam", "Suspicious")

        extracted_urls = _extract_urls(raw_text) if raw_text else []

        if mode == "url_only":
            if not extracted_urls:
                continue
            res = engine.analyze(url=extracted_urls[0])
            eval_text = extracted_urls[0]
        elif mode == "text_only":
            # Strip URLs out of text to evaluate pure text NLP & rules
            clean_text = raw_text
            for u in extracted_urls:
                clean_text = clean_text.replace(u, "").strip()
            res = engine.analyze(message_text=clean_text)
            eval_text = clean_text
        else:
            # Combined multimodal
            res = engine.analyze(message_text=raw_text, image_input=img)
            eval_text = raw_text

        predicted = res["verdict"]
        risk_score = res.get("risk_score")
        is_flagged = predicted in ("Scam", "Suspicious")

        if truth_is_scam:
            if is_flagged:
                tp += 1
                tag = "PASS (TP)"
            else:
                fn += 1
                tag = "FAIL (FN)"
        else:
            if not is_flagged:
                tn += 1
                tag = "PASS (TN)"
            else:
                fp += 1
                tag = "FAIL (FP)"

        rows.append({
            "id": case["id"],
            "truth": expected,
            "pred": predicted,
            "score": risk_score,
            "tag": tag,
            "text": (eval_text[:60] + "...") if len(eval_text) > 60 else eval_text,
        })

    total = len(rows)
    acc = (tp + tn) / total if total else 0
    prec = tp / (tp + fp) if (tp + fp) else 0
    rec = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    fpr = fp / (fp + tn) if (fp + tn) else 0

    return {
        "total": total,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "accuracy": round(acc * 100, 2),
        "precision": round(prec * 100, 2),
        "recall": round(rec * 100, 2),
        "f1": round(f1, 4),
        "fpr": round(fpr * 100, 2),
        "rows": rows,
    }


CANDIDATES = [
    {"label": "Balanced Hybrid", "text_ml": 0.35, "heuristics": 0.35, "url_ml": 0.15, "url_rule": 0.15, "unknown_url_score": 60},
    {"label": "Heuristics First", "text_ml": 0.25, "heuristics": 0.45, "url_ml": 0.15, "url_rule": 0.15, "unknown_url_score": 60},
    {"label": "ML Heavy", "text_ml": 0.50, "heuristics": 0.20, "url_ml": 0.15, "url_rule": 0.15, "unknown_url_score": 50},
    {"label": "Conservative Rules", "text_ml": 0.30, "heuristics": 0.40, "url_ml": 0.15, "url_rule": 0.15, "unknown_url_score": 60},
]


def main():
    print("=" * 76)
    print("🚀 SCAMLENS — MEMBER 3: WEIGHT-TUNING & MULTI-SPLIT BENCHMARK SUITE")
    print("=" * 76)
    print("⚠️  [NOTICE] Small sample size: results indicative only; evaluate on a larger")
    print("             benchmark before production use.\n")

    tune_set, val_set, test_set = stratified_split(EVAL_CASES, seed=42)

    print(f"📊 Dataset Split Summary (Total: {len(EVAL_CASES)} Ground-Truth Cases):")
    print(f"   • Tune Split:       {len(tune_set)} cases ({len([c for c in tune_set if c['expected_verdict'] in ('Scam', 'Suspicious')])} Scam, {len([c for c in tune_set if c['expected_verdict'] == 'Safe'])} Safe)")
    print(f"   • Validation Split: {len(val_set)} cases ({len([c for c in val_set if c['expected_verdict'] in ('Scam', 'Suspicious')])} Scam, {len([c for c in val_set if c['expected_verdict'] == 'Safe'])} Safe)")
    print(f"   • Test Split (Holdout): {len(test_set)} cases ({len([c for c in test_set if c['expected_verdict'] in ('Scam', 'Suspicious')])} Scam, {len([c for c in test_set if c['expected_verdict'] == 'Safe'])} Safe)")
    print("-" * 76)

    # 1. Choose weights on Tune + Validation only
    tune_val_set = tune_set + val_set
    best_candidate = None
    best_f1 = -1

    print("\n🔍 Grid-Search Candidate Evaluation (Tune + Validation splits, 28 cases):")
    for c in CANDIDATES:
        w = {k: c[k] for k in ("text_ml", "heuristics", "url_ml", "url_rule", "unknown_url_score")}
        engine = ScamLensScoringEngine(weights=w)
        m = evaluate_split(engine, tune_val_set, mode="combined")
        label = c["label"]
        print(f"  [{label:<18}] Acc: {m['accuracy']:5.1f}% | Prec: {m['precision']:5.1f}% | Rec: {m['recall']:5.1f}% | FPR: {m['fpr']:4.1f}% | F1: {m['f1']:.4f}")
        if m["f1"] > best_f1:
            best_f1 = m["f1"]
            best_candidate = c

    print("-" * 76)
    print(f"🏆 CHOSEN CONFIG: [{best_candidate['label']}] (based on Tune + Validation)")
    chosen_weights = {k: best_candidate[k] for k in ("text_ml", "heuristics", "url_ml", "url_rule", "unknown_url_score")}
    print(f"   Weights: {chosen_weights}")

    # 2. Evaluate on untouched Test Split across modalities
    final_engine = ScamLensScoringEngine(weights=chosen_weights)

    combined_test_m = evaluate_split(final_engine, test_set, mode="combined")
    text_test_m = evaluate_split(final_engine, test_set, mode="text_only")
    url_test_m = evaluate_split(final_engine, test_set, mode="url_only")

    print("\n" + "=" * 76)
    print("📈 UNTOUCHED TEST SET EVALUATION METRICS (Holdout 7 cases):")
    print("=" * 76)
    print(f"1. Combined Multimodal  (N={combined_test_m['total']}): Acc={combined_test_m['accuracy']}% | Prec={combined_test_m['precision']}% | Rec={combined_test_m['recall']}% | FPR={combined_test_m['fpr']}% | F1={combined_test_m['f1']}")
    print(f"2. Text-Only Stripped   (N={text_test_m['total']}): Acc={text_test_m['accuracy']}% | Prec={text_test_m['precision']}% | Rec={text_test_m['recall']}% | FPR={text_test_m['fpr']}% | F1={text_test_m['f1']}")
    print(f"3. URL-Only Evaluation  (N={url_test_m['total']}): Acc={url_test_m['accuracy']}% | Prec={url_test_m['precision']}% | Rec={url_test_m['recall']}% | FPR={url_test_m['fpr']}% | F1={url_test_m['f1']}")

    # 3. Full Benchmark Verification
    full_m = evaluate_split(final_engine, EVAL_CASES, mode="combined")

    # 4. Save chosen config to config/scoring.json
    for cfg_path in [
        os.path.join(_PROJECT_ROOT, "config", "scoring.json"),
        os.path.join(_THIS_DIR, "config", "scoring.json")
    ]:
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg_data = json.load(f)
            cfg_data["weights"].update(chosen_weights)
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg_data, f, indent=2)
        except Exception:
            pass

    # 5. Write comprehensive benchmark report to evaluation/
    for rep_dir in [
        os.path.join(_THIS_DIR, "evaluation"),
        os.path.join(_PROJECT_ROOT, "evaluation")
    ]:
        os.makedirs(rep_dir, exist_ok=True)
        report_path = os.path.join(rep_dir, "benchmark_results.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# ScamLens — Member 3: Benchmark & Weight-Tuning Report\n\n")
            f.write("> [!WARNING]\n")
            f.write("> **Small Sample Size Advisory:** Dataset currently consists of 35 curated ground-truth cases. ")
            f.write("Results are indicative; evaluate on a larger, continuous benchmark before production deployment.\n\n")
            f.write(f"**Selected Weight Profile:** `{best_candidate['label']}`  \n")
            f.write(f"**Active Weights:** `text_ml={chosen_weights['text_ml']}`, `heuristics={chosen_weights['heuristics']}`, `url_ml={chosen_weights['url_ml']}`, `url_rule={chosen_weights['url_rule']}`, `unknown_url_score={chosen_weights['unknown_url_score']}`\n\n")
            f.write("## 1. Dataset Partitioning (Stratified, Fixed Seed=42)\n\n")
            f.write("| Split | Sample Count | Scam Cases | Safe Cases | Purpose |\n")
            f.write("| :--- | :---: | :---: | :---: | :--- |\n")
            f.write(f"| **Tune Split** | {len(tune_set)} | 11 | 10 | Primary parameter tuning |\n")
            f.write(f"| **Validation Split** | {len(val_set)} | 4 | 3 | Model selection & hyperparameter check |\n")
            f.write(f"| **Test Split (Holdout)** | {len(test_set)} | 3 | 4 | Untouched final generalization evaluation |\n")
            f.write(f"| **Total** | {len(EVAL_CASES)} | 18 | 17 | Full benchmark dataset |\n\n")
            f.write("## 2. Generalization Performance on Untouched Test Split\n\n")
            f.write("| Evaluation Modality | Evaluated Cases | Accuracy | Precision | Recall | FPR | F1-Score |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
            f.write(f"| **Combined Multimodal** | {combined_test_m['total']} | **{combined_test_m['accuracy']}%** | **{combined_test_m['precision']}%** | **{combined_test_m['recall']}%** | {combined_test_m['fpr']}% | **{combined_test_m['f1']}** |\n")
            f.write(f"| **Text-Only (URLs Stripped)** | {text_test_m['total']} | **{text_test_m['accuracy']}%** | **{text_test_m['precision']}%** | **{text_test_m['recall']}%** | {text_test_m['fpr']}% | **{text_test_m['f1']}** |\n")
            f.write(f"| **URL-Only Evaluation** | {url_test_m['total']} | **{url_test_m['accuracy']}%** | **{url_test_m['precision']}%** | **{url_test_m['recall']}%** | {url_test_m['fpr']}% | **{url_test_m['f1']}** |\n\n")
            f.write("## 3. Full Benchmark Dataset Performance (35 Cases)\n\n")
            f.write("| Metric | Full Dataset Value |\n| :--- | :---: |\n")
            f.write(f"| Total Cases | {full_m['total']} |\n")
            f.write(f"| Accuracy | **{full_m['accuracy']}%** |\n")
            f.write(f"| Precision | **{full_m['precision']}%** |\n")
            f.write(f"| Recall | **{full_m['recall']}%** |\n")
            f.write(f"| False Positive Rate (FPR) | **{full_m['fpr']}%** |\n")
            f.write(f"| F1-Score | **{full_m['f1']}** |\n")
            f.write(f"| True Positives (TP) | {full_m['tp']} |\n")
            f.write(f"| True Negatives (TN) | {full_m['tn']} |\n")
            f.write(f"| False Positives (FP) | {full_m['fp']} |\n")
            f.write(f"| False Negatives (FN) | {full_m['fn']} |\n\n")
            f.write("## 4. Per-Case Test Split Log\n\n")
            f.write("| Case ID | Ground Truth | Predicted | Risk Index | Match | Text Excerpt |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: | :--- |\n")
            for r in combined_test_m["rows"]:
                f.write(f"| `{r['id']}` | {r['truth']} | {r['pred']} | {r['score']} | {r['tag']} | {r['text']} |\n")

    print(f"\n✅ Reports written to evaluation/benchmark_results.md")


if __name__ == "__main__":
    main()
