# ================================================================
# backend\evaluate.py
# Runs RAGAS evaluation + triage accuracy on full dataset.
# Run: python backend\evaluate.py
# ================================================================

import sys
import json
import os
import time
from datetime import datetime

sys.path.insert(0, "backend")

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from langchain_groq import ChatGroq
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_community.embeddings import HuggingFaceEmbeddings

from rag_pipeline import RAGPipeline
from triage import classify, TriageLevel
from config import GROQ_API_KEY, LLM_MODEL

# ── Load dataset ─────────────────────────────────────────────────
with open("logs/evaluation_dataset.json", encoding="utf-8") as f:
    DATASET = json.load(f)


def run_ragas_evaluation(pipeline: RAGPipeline) -> dict:
    print("\n[1/3] RAGAS Evaluation on 50 queries...")
    print("  Takes 5-15 minutes. Do not interrupt.\n")

    data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

    for i, item in enumerate(DATASET["queries"], 1):
        try:
            result = pipeline.ask(item["query"])
            data["question"].append(item["query"])
            data["answer"].append(result["answer"])
            data["contexts"].append([s["content"] for s in result["sources"]])
            data["ground_truth"].append(item["ground_truth"])
            print(f"  [{i:02d}/50] ✓ {item['query'][:55]}")
        except Exception as e:
            print(f"  [{i:02d}/50] ✗ Error: {e}")
            data["question"].append(item["query"])
            data["answer"].append("Error")
            data["contexts"].append([""])
            data["ground_truth"].append(item["ground_truth"])
        time.sleep(2)  # avoid rate limits

    dataset = Dataset.from_dict(data)

    # Use Groq as the LLM for RAGAS scoring
    groq_llm = LangchainLLMWrapper(
        ChatGroq(
            model="llama-3.1-8b-instant",  # smaller model — uses fewer tokens
            api_key=GROQ_API_KEY,
            temperature=0,
        )
    )
    emb = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    )

    scores = evaluate(
        dataset, metrics=[faithfulness, answer_relevancy], llm=groq_llm, embeddings=emb
    )

    # Handle both float and list return types
    faith_raw = scores["faithfulness"]
    relev_raw = scores["answer_relevancy"]

    if isinstance(faith_raw, list):
        faith_raw = [
            x
            for x in faith_raw
            if x is not None and not (isinstance(x, float) and x != x)
        ]
        faith = round(sum(faith_raw) / len(faith_raw), 4) if faith_raw else 0.0
    else:
        faith = round(float(faith_raw), 4)

    if isinstance(relev_raw, list):
        relev_raw = [
            x
            for x in relev_raw
            if x is not None and not (isinstance(x, float) and x != x)
        ]
        relev = round(sum(relev_raw) / len(relev_raw), 4) if relev_raw else 0.0
    else:
        relev = round(float(relev_raw), 4)

    print(f"\n  ✓ Faithfulness      : {faith}")
    print(f"  ✓ Answer Relevancy  : {relev}")
    print(f"  ✓ Hallucination Rate: {round(1 - faith, 4)}")

    return {
        "faithfulness": faith,
        "answer_relevancy": relev,
        "hallucination_rate": round(1 - faith, 4),
    }


def run_triage_accuracy() -> dict:
    """
    Test all 20 emergency cases.
    ALL 20 must return RED — zero false negatives allowed.
    """
    print("\n[2/3] Triage Accuracy — 20 Emergency Cases")
    correct = 0
    failures = []

    for t in DATASET["triage_tests"]:
        result = classify(t["query"])
        ok = result.level.value == t["expected"]
        correct += 1 if ok else 0
        if not ok:
            failures.append(t)
        status = "✓" if ok else "✗ FAIL"
        print(f"  {status} [{t['lang']:2}] {t['query'][:50]}")

    accuracy = correct / len(DATASET["triage_tests"])
    print(f"\n  Triage: {correct}/20 = {accuracy:.0%}")
    if failures:
        print(f"  FAILURES: {[f['query'][:30] for f in failures]}")

    return {"accuracy": accuracy, "passed": correct, "failures": failures}


def run_baseline_comparison(pipeline: RAGPipeline) -> dict:
    """Compare RAG vs plain Groq LLM on treatment + emergency queries."""
    print("\n[3/3] Baseline Comparison — RAG vs Plain LLM")

    plain_llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.1)

    critical = [
        q for q in DATASET["queries"] if q["category"] in ["treatment", "emergency"]
    ][:10]

    plain_wrong = 0
    rag_wrong = 0
    comparison = []

    for q in critical:
        try:
            plain_ans = plain_llm.invoke(q["query"]).content
            rag_ans = pipeline.ask(q["query"])["answer"]

            plain_ok = any(k.lower() in plain_ans.lower() for k in q["key_terms"])
            rag_ok = any(k.lower() in rag_ans.lower() for k in q["key_terms"])

            if not plain_ok:
                plain_wrong += 1
            if not rag_ok:
                rag_wrong += 1

            comparison.append(
                {
                    "question": q["query"],
                    "plain_llm": plain_ans[:200],
                    "rag": rag_ans[:200],
                    "plain_correct": plain_ok,
                    "rag_correct": rag_ok,
                }
            )
            print(
                f"  {'✓' if plain_ok else '✗'} Plain / {'✓' if rag_ok else '✗'} RAG | {q['query'][:45]}"
            )
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Error on: {q['query'][:40]} — {e}")

    return {
        "plain_wrong": plain_wrong,
        "rag_wrong": rag_wrong,
        "plain_error_rate": round(plain_wrong / 10, 2),
        "rag_error_rate": round(rag_wrong / 10, 2),
        "comparison": comparison,
    }


if __name__ == "__main__":
    print("=" * 58)
    print("  Aarogya AI — Phase 4 Evaluation")
    print("=" * 58)
    t0 = time.time()

    pipeline = RAGPipeline()

    ragas = run_ragas_evaluation(pipeline)
    triage = run_triage_accuracy()
    baseline = run_baseline_comparison(pipeline)

    report = {
        "timestamp": datetime.now().isoformat(),
        "ragas": ragas,
        "triage": triage,
        "baseline": baseline,
        "total_time_min": round((time.time() - t0) / 60, 1),
        "model": f"{LLM_MODEL} + FAISS + MiniLM-L12",
        "knowledge_base": "WHO + CDC + NIH (12 PDFs, 87 chunks)",
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 58)
    print(f"  Faithfulness      : {ragas['faithfulness']}")
    print(f"  Answer Relevancy  : {ragas['answer_relevancy']}")
    print(f"  Hallucination Rate: {ragas['hallucination_rate']}")
    print(f"  Triage RED        : {triage['accuracy']:.0%}")
    print(f"  Plain LLM errors  : {baseline['plain_wrong']}/10")
    print(f"  RAG errors        : {baseline['rag_wrong']}/10")
    print(f"  Total time        : {report['total_time_min']} min")
    print("  Saved → logs/evaluation_report.json")
    print("=" * 58)
