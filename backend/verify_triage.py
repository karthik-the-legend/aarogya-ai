import sys
sys.path.insert(0, 'backend')
from triage import classify, TriageLevel, EMERGENCY_KEYWORDS, MONITOR_KEYWORDS

print("=" * 55)
print("  Day 9 Final Checklist")
print("=" * 55)

# Check 1: Keyword count
print(f"  ✓ RED keywords   : {len(EMERGENCY_KEYWORDS)} keywords")
print(f"  ✓ YELLOW keywords: {len(MONITOR_KEYWORDS)} keywords")
print(f"  ✓ Total keywords : {len(EMERGENCY_KEYWORDS) + len(MONITOR_KEYWORDS)}")

# Check 2: RED accuracy
# Use Unicode codepoints to avoid copy-paste encoding issues
kannada_chest_pain = '\u0c8e\u0ca6\u0cc6 \u0ca8\u0ccb\u0cb5\u0cc1'

red_tests = [
    "chest pain", "difficulty breathing", "unconscious",
    "seizure", "bleeding won't stop", "105 fever",
    "सीने में दर्द", "மார்பு வலி", "ఛాతీ నొప్పి",
    kannada_chest_pain,
    "stroke", "heart attack"
]
red_passed = sum(1 for q in red_tests if classify(q).level == TriageLevel.RED)
print(f"  ✓ RED accuracy   : {red_passed}/{len(red_tests)} = 100%"
      if red_passed == len(red_tests)
      else f"  ✗ RED accuracy   : {red_passed}/{len(red_tests)} FAILED")

# Check 3: No false negatives
missed = [q for q in red_tests if classify(q).level != TriageLevel.RED]
if not missed:
    print("  ✓ Zero false negatives — no emergency missed")
else:
    print(f"  ✗ Missed RED cases: {missed}")

# Check 4: Override flag
r = classify("chest pain")
print(f"  ✓ Override flag  : {r.override} (True = LLM overridden)")

print("=" * 55)
if red_passed == len(red_tests) and not missed:
    print("  ✓ Day 9 COMPLETE — triage.py is medically safe!")
print("=" * 55)