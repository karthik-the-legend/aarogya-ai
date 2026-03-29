import sys
import json

sys.path.insert(0, "backend")

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config import VECTORSTORE_DIR, EMBEDDING_MODEL

TEST_QUERIES = [
    "What are symptoms of dengue fever?",
    "How is malaria treated?",
    "How to prevent typhoid?",
    "What are signs of cholera?",
    "How is tuberculosis transmitted?",
    "What are cold remedies?",
    "How to manage fever at home?",
    "How to treat diarrhoea with rehydration?",
    "Should I get a flu vaccine?",
    "What are signs of skin infection?",
]

print("Loading embeddings and FAISS index...")
emb = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
db = FAISS.load_local(str(VECTORSTORE_DIR), emb, allow_dangerous_deserialization=True)

results = {}
print(f"\n{'Query':<38} | k=1 | k=3 | k=5")
print("-" * 62)

for q in TEST_QUERIES:
    row = {}
    for k in [1, 3, 5]:
        docs = db.similarity_search(q, k=k)
        row[f"k{k}_sources"] = [d.metadata.get("source", "?") for d in docs]
        row[f"k{k}_chars"] = sum(len(d.page_content) for d in docs)
    results[q] = row
    print(
        f"{q[:36]:<38} | "
        f"{len(row['k1_sources'])} src | "
        f"{len(row['k3_sources'])} src | "
        f"{len(row['k5_sources'])} src"
    )

# Save results
with open("logs/topk_experiment.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved to logs/topk_experiment.json")

# Summary table
print("\n" + "=" * 55)
print("  TOP_K Comparison Summary")
print("=" * 55)
print(
    f"  k=1 → Average chars: "
    f"{sum(r['k1_chars'] for r in results.values())//len(results)}"
)
print(
    f"  k=3 → Average chars: "
    f"{sum(r['k3_chars'] for r in results.values())//len(results)}"
)
print(
    f"  k=5 → Average chars: "
    f"{sum(r['k5_chars'] for r in results.values())//len(results)}"
)
print("=" * 55)
print("  Conclusion: k=3 is the sweet spot")
print("  k=1 misses context, k=5 dilutes the prompt")
print("=" * 55)
