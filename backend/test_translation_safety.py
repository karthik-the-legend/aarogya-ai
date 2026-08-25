# ================================================================
# backend\test_translation_safety.py
# V2 Phase 4 (multilingual) regression: medical numbers, dosages, and
# emergency phone numbers must survive translation exactly — a
# mistranslated "500mg" or a dropped "108" is a safety bug, not a
# cosmetic one.
#
# Run: python backend/test_translation_safety.py
# Exits non-zero if any expected number is missing from the output.
# ================================================================
import re
import sys

sys.path.insert(0, "backend")
from dotenv import load_dotenv

load_dotenv()
from translate import from_english

# Each case: (English text, target language code, numbers that MUST
# appear unchanged in the translated output).
CASES = [
    ("Take 500mg of paracetamol every 6 hours.", "hi", ["500", "6"]),
    ("The fever should not exceed 104 degrees F.", "hi", ["104"]),
    ("Give 2.5ml of syrup twice a day for a child under 5 years old.", "hi", ["2.5", "5"]),
    ("Call 108 immediately if bleeding does not stop within 10 minutes.", "hi", ["108", "10"]),
    ("Take 500mg of paracetamol every 6 hours.", "ta", ["500", "6"]),
    ("The dose is 250mg twice daily for 5 days.", "te", ["250", "5"]),
    ("Call 108 if temperature exceeds 104 degrees.", "kn", ["108", "104"]),
]


def numbers_in(text: str) -> set:
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def run():
    print("=" * 60)
    print("  Translation Safety — numbers/dosages must survive")
    print("=" * 60)

    failures = []
    for text, lang, required in CASES:
        translated = from_english(text, lang)
        found = numbers_in(translated)
        missing = [n for n in required if n not in found]
        status = "PASS" if not missing else "FAIL"
        print(f"  [{status}] [{lang}] {text[:50]}")
        if missing:
            print(f"           missing: {missing}  |  got: {translated}")
            failures.append((text, lang, missing))

    print()
    print(f"  Result: {len(CASES) - len(failures)}/{len(CASES)} passed")
    if failures:
        print(f"  FAILURES: {failures}")
        print("=" * 60)
        sys.exit(1)

    print("  All medical numbers survived translation intact.")
    print("=" * 60)


if __name__ == "__main__":
    run()
