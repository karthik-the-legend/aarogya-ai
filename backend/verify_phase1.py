import os, sys
from pathlib import Path

passed = 0
failed = 0


def check(name, condition, fix=""):
    global passed, failed
    if condition:
        print(f"  ✓ {name}")
        passed += 1
    else:
        print(f"  ✗ {name}")
        if fix:
            print(f"    FIX: {fix}")
        failed += 1


print("=" * 55)
print("  PHASE 1 VERIFICATION")
print("=" * 55)

# Check 1: PDFs
pdfs = list(Path("data").glob("*.pdf"))
check(
    "12 PDFs in data\\ folder", len(pdfs) == 12, f"Found {len(pdfs)} — go back to Day 2"
)

# Check 2: sources.txt
check(
    "data\\sources.txt exists",
    Path("data/sources.txt").exists(),
    "Create it — Day 2 Step 6",
)

# Check 3: FAISS index
check(
    "vectorstore\\index.faiss exists",
    Path("vectorstore/index.faiss").exists(),
    "Run: python backend\\ingest.py",
)

# Check 4: config.py imports
try:
    sys.path.insert(0, "backend")
    from config import GEMINI_API_KEY, CHUNK_SIZE, TOP_K_RETRIEVAL

    check("config.py imports cleanly", True)
except Exception as e:
    check("config.py imports cleanly", False, str(e))

# Check 5: models.py validation
try:
    from models import QueryRequest

    r = QueryRequest(query="test query ok", lang_code="hi", language_name="Hindi")
    check("models.py Pydantic validation works", True)
except Exception as e:
    check("models.py Pydantic validation works", False, str(e))

# Check 6: translate.py Hindi
try:
    from translate import to_english

    r = to_english("बुखार", "hi")
    check(
        "translate.py Hindi→English works",
        "fever" in r.lower() or "temperature" in r.lower(),
    )
except Exception as e:
    check("translate.py Hindi→English works", False, str(e))

# Check 7: translate.py Telugu
try:
    from translate import to_english

    r = to_english("నాకు తలనొప్పి ఉంది", "te")
    check("translate.py Telugu→English works", len(r) > 3)
except Exception as e:
    check("translate.py Telugu→English works", False, str(e))

# Check 8: Git is initialised
check("Git repository initialised", Path(".git").exists(), "Run: git init")

print("=" * 55)
print(f"  Result: {passed}/8 checks passed")
if passed == 8:
    print("  ✓ PHASE 1 COMPLETE. Start Phase 2!")
else:
    print(f"  ✗ Fix {failed} issues before continuing.")
print("=" * 55)
