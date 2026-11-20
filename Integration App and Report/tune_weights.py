"""
ScamLens — Member 3: Weight-Tuning & End-to-End Benchmark Suite
================================================================
Evaluates the unified analyze() function against Member 2's 36 ground-truth
eval cases.  Performs grid search across three weight profiles, selects the
best F1-score config, prints a full confusion-matrix summary, and writes
a Markdown report to evaluation/benchmark_results.md.

Usage:
    cd "Integration App and Report"
    python tune_weights.py
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_DETECTION_DIR = os.path.join(_PROJECT_ROOT, "Detection Logic")

for _p in [_THIS_DIR, _PROJECT_ROOT, _DETECTION_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scoring import ScamLensScoringEngine
from eval_cases import EVALUATION_CASES


# ═══════════════════════════════════════════════════════════════════════
#  Evaluation runner
# ═══════════════════════════════════════════════════════════════════════
def evaluate(weights: dict) -> dict:
    """Run all eval cases with the given weight profile and return metrics."""
    engine = ScamLensScoringEngine(weights=weights)

    tp = fp = tn = fn = 0
    rows = []

    for case in EVALUATION_CASES:
        res = engine.analyze(
            message_text=case.get("text"),
            url=case.get("url"),
        )
        predicted  = res["verdict"]
        risk_score = res["risk_score"]
        is_flagged = predicted in ("Scam", "Suspicious")
        truth      = case["ground_truth"]          # "Scam" | "Safe"

        if truth == "Scam":
            if is_flagged: tp += 1; tag = "PASS (TP)"
            else:          fn += 1; tag = "FAIL (FN)"
        else:
            if not is_flagged: tn += 1; tag = "PASS (TN)"
            else:              fp += 1; tag = "FAIL (FP)"

        rows.append({
            "id":       case["id"],
            "cat":      case["category"],
            "truth":    truth,
            "pred":     predicted,
            "score":    risk_score,
            "tag":      tag,
            "reasons":  res["reasons"][:2],
        })

    total = len(EVALUATION_CASES)
    acc  = (tp + tn) / total if total else 0
    prec = tp / (tp + fp)   if (tp + fp)   else 0
    rec  = tp / (tp + fn)   if (tp + fn)   else 0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    fpr  = fp / (fp + tn)   if (fp + tn)   else 0

    return {
        "total": total,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "accuracy":  round(acc * 100, 2),
        "precision": round(prec * 100, 2),
        "recall":    round(rec * 100, 2),
        "f1":        round(f1, 4),
        "fpr":       round(fpr * 100, 2),
        "rows":      rows,
    }


# ═══════════════════════════════════════════════════════════════════════
#  Main — grid-search + report
# ═══════════════════════════════════════════════════════════════════════
CANDIDATES = [
    {"label": "Balanced Hybrid", "text_ml": 0.30, "text_rule": 0.35, "url_ml": 0.15, "url_rule": 0.20},
    {"label": "ML Heavy",        "text_ml": 0.45, "text_rule": 0.25, "url_ml": 0.20, "url_rule": 0.10},
    {"label": "Rule Heavy",      "text_ml": 0.20, "text_rule": 0.45, "url_ml": 0.10, "url_rule": 0.25},
]


def main():
    print("=" * 70)
    print("🚀 SCAMLENS — MEMBER 3  TUNING & INTEGRATION BENCHMARK")
    print("=" * 70)

    best = None
    best_f1 = -1

    for c in CANDIDATES:
        w = {k: c[k] for k in ("text_ml", "text_rule", "url_ml", "url_rule")}
        m = evaluate(w)
        label = c["label"]
        print(f"\n[{label}]  weights={w}")
        print(f"  Accuracy {m['accuracy']}%  Precision {m['precision']}%  "
              f"Recall {m['recall']}%  FPR {m['fpr']}%  F1 {m['f1']}")
        if m["f1"] > best_f1:
            best_f1 = m["f1"]
            best = {"label": label, "weights": w, "metrics": m}

    m = best["metrics"]
    print("\n" + "=" * 70)
    print(f"🏆 BEST: [{best['label']}]  F1={m['f1']}")
    print(f"   TP={m['tp']}  TN={m['tn']}  FP={m['fp']}  FN={m['fn']}")
    print(f"   Accuracy={m['accuracy']}%  Precision={m['precision']}%  "
          f"Recall={m['recall']}%  FPR={m['fpr']}%")
    print("=" * 70)

    # Print case-level results
    print("\nPer-case results:")
    for r in m["rows"]:
        print(f"  [{r['tag']}] {r['id']} ({r['cat']}) → {r['pred']} {r['score']}%")

    # Write Markdown report
    eval_dir = os.path.join(_THIS_DIR, "evaluation")
    os.makedirs(eval_dir, exist_ok=True)
    report_path = os.path.join(eval_dir, "benchmark_results.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# ScamLens — Member 3: Integration Benchmark Report\n\n")
        f.write(f"**Selected Profile:** {best['label']}  \n")
        f.write(f"**Weights:** text_ml={best['weights']['text_ml']}, "
                f"text_rule={best['weights']['text_rule']}, "
                f"url_ml={best['weights']['url_ml']}, "
                f"url_rule={best['weights']['url_rule']}\n\n")
        f.write("## Performance Summary\n\n")
        f.write(f"| Metric | Value |\n| :--- | :---: |\n")
        f.write(f"| Total Cases | {m['total']} |\n")
        f.write(f"| Accuracy | **{m['accuracy']}%** |\n")
        f.write(f"| Precision | **{m['precision']}%** |\n")
        f.write(f"| Recall | **{m['recall']}%** |\n")
        f.write(f"| FPR | **{m['fpr']}%** |\n")
        f.write(f"| F1-Score | **{m['f1']}** |\n")
        f.write(f"| TP | {m['tp']} |\n")
        f.write(f"| TN | {m['tn']} |\n")
        f.write(f"| FP | {m['fp']} |\n")
        f.write(f"| FN | {m['fn']} |\n\n")
        f.write("## Detailed Results\n\n")
        f.write("| ID | Category | Truth | Predicted | Score | Status |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: |\n")
        for r in m["rows"]:
            f.write(f"| {r['id']} | {r['cat']} | {r['truth']} | "
                    f"{r['pred']} | {r['score']}% | {r['tag']} |\n")

    print(f"\n✅ Report written to {report_path}")


if __name__ == "__main__":
    main()
