# ================================================================
# backend\test_triage_v2_safety.py
# Safety regression suite for the V2 triage upgrade: negation
# handling, misspelling/colloquial coverage, new emergency
# categories (choking, burns, mental health), and the multilingual
# emergency-message script-detection bugfix.
#
# Run: python backend/test_triage_v2_safety.py
# Exits non-zero if ANY red-case regression is found — wire this
# into CI so a future change can never silently reduce RED recall.
# ================================================================
import sys

sys.path.insert(0, "backend")
from triage import classify, TriageLevel

RED = TriageLevel.RED
YELLOW = TriageLevel.YELLOW
GREEN = TriageLevel.GREEN

CASES = [
    # ── Negation: must NOT fire RED ──────────────────────────────
    ("I don't have chest pain", GREEN),
    ("no chest pain, just tired", GREEN),
    ("he is not unconscious, just sleepy", GREEN),
    ("not experiencing any breathing problems", GREEN),
    ("मुझे सीने में दर्द नहीं है", GREEN),
    # ── Negation must NOT suppress a real report ─────────────────
    ("I have chest pain", RED),
    ("My father has chest pain", RED),  # third-person still RED by design
    ("Does chest pain mean heart attack?", RED),  # conservative over-trigger, by design
    # ── Misspellings / colloquial (task 9) ───────────────────────
    ("cant breathe properly", RED),
    ("cant breath since morning", RED),
    ("breathing problem right now", RED),
    ("unable to breathe at all", RED),
    # ── Newly added categories (task 6) ───────────────────────────
    ("choking on food right now", RED),
    ("lips turning blue", RED),
    ("severe burns on the arm", RED),
    ("I want to kill myself", RED),
    ("I want to die", RED),
    # ── Existing behaviour must be unchanged ──────────────────────
    ("I have chest pain", RED),
    ("difficulty breathing", RED),
    ("सीने में दर्द है", RED),
    ("மார்பு வலி இருக்கிறது", RED),
    ("ఛాతీ నొప్పి ఉంది", RED),
    ("ಎದೆ ನೋವು ಇದೆ", RED),
    ("patient is unconscious", RED),
    ("he had a seizure", RED),
    ("bleeding won't stop", RED),
    ("105 fever since morning", RED),
    ("can't breathe properly", RED),
    ("stroke symptoms arm weakness", RED),
    ("fever for 3 days and rash", YELLOW),
    ("3 दिन से बुखार और उल्टी", YELLOW),
    ("vomiting and diarrhoea", YELLOW),
    ("joint pain with high fever", YELLOW),
    ("mild cold and runny nose", GREEN),
    ("sore throat mild fever", GREEN),
    ("stomach ache after eating", GREEN),
    ("I have a headache", GREEN),
]

# Multilingual emergency-message script bug: previously every Indic
# script resolved to the Hindi message because of an open-ended
# codepoint check. Verify each language now gets its OWN message.
MESSAGE_CASES = [
    ("மார்பு வலி இருக்கிறது", "108"),  # must not be the Devanagari string
    ("ఛాతీ నొప్పి ఉంది", "108"),
    ("ಎದೆ ನೋವು ಇದೆ", "108"),
]


def run():
    print("=" * 60)
    print("  Triage V2 Safety Regression")
    print("=" * 60)

    passed = 0
    critical_failures = []  # a RED case that was missed — build-breaking

    for query, expected in CASES:
        result = classify(query)
        ok = result.level == expected
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {query[:55]:<55} -> {result.level.value} (expected {expected.value})")
        if ok:
            passed += 1
        elif expected == RED:
            critical_failures.append(query)

    print()
    print("  --- Multilingual emergency-message check ---")
    hindi_msg = classify("सीने में दर्द है").message
    for query, must_contain in MESSAGE_CASES:
        msg = classify(query).message
        distinct_from_hindi = msg != hindi_msg
        ok = must_contain in msg and distinct_from_hindi
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {query[:30]:<30} -> language-distinct message: {distinct_from_hindi}")
        if not ok:
            critical_failures.append(f"[message] {query}")

    total = len(CASES)
    print()
    print(f"  Result: {passed}/{total} triage cases passed")
    if critical_failures:
        print(f"  CRITICAL FAILURES (RED/safety regression): {critical_failures}")
        print("=" * 60)
        sys.exit(1)

    print("  All safety-critical checks passed.")
    print("=" * 60)


if __name__ == "__main__":
    run()
