# ============================================================
# backend\test_faiss.py
# Verifies the FAISS index retrieves correct medical content
# Run: python backend\test_faiss.py
# ============================================================

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config import VECTORSTORE_DIR, EMBEDDING_MODEL

# Load the embedding model (same as ingestion)
print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# Load the FAISS index from disk
print("Loading FAISS index...")
db = FAISS.load_local(
    str(VECTORSTORE_DIR), embeddings, allow_dangerous_deserialization=True
)
print(f"Index loaded. Total vectors: {db.index.ntotal}")

# ── Test 1: Dengue symptoms query ───────────────────────────
print("\n--- TEST 1: Dengue Symptoms ---")
results = db.similarity_search("symptoms of dengue fever", k=3)
for i, doc in enumerate(results):
    src = doc.metadata.get("source", "unknown")
    pg = doc.metadata.get("page", "?")
    print(f"  Result {i+1}: {src} | page {pg}")
    print(f"  Text: {doc.page_content[:180]}\n")

# ── Test 2: THE MOST IMPORTANT TEST ─────────────────────────
# This query must return a warning about ibuprofen/NSAIDs
# If it does NOT, your knowledge base is missing critical data
print("--- TEST 2: Dengue Drug Warning (Critical) ---")
results2 = db.similarity_search("can I take ibuprofen for dengue", k=3)
found_warning = False
for i, doc in enumerate(results2):
    text_lower = doc.page_content.lower()
    if any(w in text_lower for w in ["ibuprofen", "nsaid", "avoid", "paracetamol"]):
        found_warning = True
        print(f"  Result {i+1}: {doc.page_content[:200]}\n")

if found_warning:
    print("  ✓ PASSED: Drug warning found in results")
else:
    print("  ✗ WARNING: No drug warning found — re-check your PDFs")

# ── Test 3: Malaria treatment query ─────────────────────────
print("\n--- TEST 3: Malaria Treatment ---")
results3 = db.similarity_search("malaria treatment medicines", k=2)
for i, doc in enumerate(results3):
    print(f"  Result {i+1}: {doc.page_content[:200]}\n")

# ── Test 4: Out-of-knowledge query ──────────────────────────
# Query not in your PDFs — still returns something, but
# it should NOT be confidently correct (RAG handles this)
print("--- TEST 4: Out-of-scope query ---")
results4 = db.similarity_search("how to treat a broken bone", k=1)
print(f"  Closest match: {results4[0].page_content[:200]}")
print("  (This is acceptable — shows graceful fallback)")

print("\n✓ All FAISS tests complete.")
