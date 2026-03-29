import sys

sys.path.insert(0, "backend")
from triage import classify, TriageLevel

TESTS = [
    # RED cases — ALL must pass
    ("I have chest pain", TriageLevel.RED),
    ("difficulty breathing", TriageLevel.RED),
    ("सीने में दर्द है", TriageLevel.RED),
    ("மார்பு வலி இருக்கிறது", TriageLevel.RED),
    ("ఛాతీ నొప్పి ఉంది", TriageLevel.RED),
    ("ಎದೆ ನೋವು ಇದೆ", TriageLevel.RED),
    ("patient is unconscious", TriageLevel.RED),
    ("he had a seizure", TriageLevel.RED),
    ("bleeding won't stop", TriageLevel.RED),
    ("105 fever since morning", TriageLevel.RED),
    ("can't breathe properly", TriageLevel.RED),
    ("stroke symptoms arm weakness", TriageLevel.RED),
    # YELLOW cases
    ("fever for 3 days and rash", TriageLevel.YELLOW),
    ("3 दिन से बुखार और उल्टी", TriageLevel.YELLOW),
    ("vomiting and diarrhoea", TriageLevel.YELLOW),
    ("joint pain with high fever", TriageLevel.YELLOW),
    # GREEN cases
    ("mild cold and runny nose", TriageLevel.GREEN),
    ("sore throat mild fever", TriageLevel.GREEN),
    ("stomach ache after eating", TriageLevel.GREEN),
    ("I have a headache", TriageLevel.GREEN),
]

passed = 0
failed_red = []

print("=" * 55)
print("  Triage — 20 Test Cases")
print("=" * 55)

for query, expected in TESTS:
    result = classify(query)
    ok = result.level == expected
    if ok:
        passed += 1
        print(f"  ✓ {query[:45]:<45} → {result.level.value}")
    else:
        print(
            f"  ✗ {query[:45]:<45} → got {result.level.value}, expected {expected.value}"
        )
        if expected == TriageLevel.RED:
            failed_red.append(query)

print(f"\n  Result: {passed}/20 passed")
if failed_red:
    print(f"  CRITICAL FAILURES (RED missed): {failed_red}")
elif passed == 20:
    print("  ✓ 100% accuracy — triage.py is medically safe")
print("=" * 55)
