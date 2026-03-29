import sys
import json
import time
from datetime import datetime

sys.path.insert(0, "backend")

from rag_pipeline import RAGPipeline
from triage import classify

print("=" * 55)
print("  Aarogya AI — Manual Evaluation")
print("=" * 55)

pipeline = RAGPipeline()

with open("logs/evaluation_dataset.json", encoding="utf-8") as f:
    DATASET = json.load(f)

# ── Part 1: 50 query accuracy ────────────────────────────────────
print("\n[1/2] RAG Accuracy — 50 queries")
correct = 0
results = []

for i, item in enumerate(DATASET["queries"], 1):
    try:
        result = pipeline.ask(item["query"])
        answer = result["answer"].lower()
        key_hit = any(k.lower() in answer for k in item["key_terms"])
        correct += 1 if key_hit else 0
        status = "✓" if key_hit else "✗"
        print(f"  [{i:02d}/50] {status} {item['query'][:50]}")
        results.append(
            {
                "id": item["id"],
                "disease": item["disease"],
                "query": item["query"],
                "key_hit": key_hit,
                "answer": result["answer"][:200],
                "sources": len(result["sources"]),
            }
        )
        time.sleep(0.5)
    except Exception as e:
        print(f"  [{i:02d}/50] ✗ Error: {e}")
        results.append(
            {
                "id": item["id"],
                "disease": item["disease"],
                "query": item["query"],
                "key_hit": False,
                "answer": "Error",
                "sources": 0,
            }
        )
        time.sleep(2)

accuracy = correct / 50

# ── Part 2: Triage accuracy ──────────────────────────────────────
print("\n[2/2] Triage Accuracy — 20 Emergency Cases")
triage_correct = 0
failures = []

for t in DATASET["triage_tests"]:
    result = classify(t["query"])
    ok = result.level.value == t["expected"]
    triage_correct += 1 if ok else 0
    if not ok:
        failures.append(t["query"])
    print(f"  {'✓' if ok else '✗'} [{t['lang']}] {t['query'][:45]}")

triage_accuracy = triage_correct / 20

# ── Disease breakdown ────────────────────────────────────────────
from collections import defaultdict

disease_scores = defaultdict(lambda: {"correct": 0, "total": 0})
for r in results:
    disease_scores[r["disease"]]["total"] += 1
    if r["key_hit"]:
        disease_scores[r["disease"]]["correct"] += 1

# ── Save report ──────────────────────────────────────────────────
report = {
    "timestamp": datetime.now().isoformat(),
    "rag_accuracy": round(accuracy, 4),
    "correct_queries": correct,
    "total_queries": 50,
    "triage_accuracy": round(triage_accuracy, 4),
    "triage_passed": triage_correct,
    "triage_failures": failures,
    "disease_breakdown": {k: v for k, v in disease_scores.items()},
    "results": results,
    "model": "llama-3.1-8b-instant via Groq + FAISS",
    "knowledge_base": "WHO + CDC + NIH (12 PDFs)",
}

with open("logs/evaluation_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

# ── Final summary ────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  EVALUATION RESULTS")
print("=" * 55)
print(f"  RAG Accuracy    : {correct}/50 = {accuracy:.0%}")
print(f"  Triage Accuracy : {triage_correct}/20 = {triage_accuracy:.0%}")
print()
print("  Disease Breakdown:")
for disease, scores in disease_scores.items():
    pct = scores["correct"] / scores["total"]
    print(f"    {disease:<20} {scores['correct']}/{scores['total']} = {pct:.0%}")
print()
if failures:
    print(f"  Triage failures : {triage_failures}")
else:
    print("  Triage : All 20 RED cases detected!")
print()
print("  Saved → logs/evaluation_report.json")
print("=" * 55)
