import sys
from pathlib import Path

sys.path.insert(0, "backend")

print("=" * 45)
print("  Day 7 Startup Checks")
print("=" * 45)

# Check 1: FAISS index exists
faiss_ok = Path("vectorstore/index.faiss").exists()
print(f"{'✓' if faiss_ok else '✗'} FAISS index exists: {faiss_ok}")

# Check 2: Gemini key is set
try:
    from config import GEMINI_API_KEY

    key_ok = bool(GEMINI_API_KEY)
    print(f"{'✓' if key_ok else '✗'} Gemini API key: {'OK' if key_ok else 'MISSING'}")
except Exception as e:
    print(f"✗ config.py error: {e}")
    key_ok = False

# Check 3: FAISS loads and retrieves
try:
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    from config import VECTORSTORE_DIR, EMBEDDING_MODEL

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    db = FAISS.load_local(
        str(VECTORSTORE_DIR), embeddings, allow_dangerous_deserialization=True
    )
    results = db.similarity_search("dengue fever symptoms", k=1)
    faiss_search_ok = len(results) > 0
    print(f"✓ FAISS search works: {db.index.ntotal} vectors loaded")
except Exception as e:
    print(f"✗ FAISS load error: {e}")
    faiss_search_ok = False

# Summary
print("=" * 45)
all_ok = faiss_ok and key_ok and faiss_search_ok
if all_ok:
    print("  ✓ All checks passed — ready to code!")
else:
    print("  ✗ Fix failing checks before continuing.")
print("=" * 45)
