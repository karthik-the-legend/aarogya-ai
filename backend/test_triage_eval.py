import sys
import json
sys.path.insert(0, 'backend')
from triage import classify

with open('logs/evaluation_dataset.json', encoding='utf-8') as f:
    d = json.load(f)

correct  = 0
failures = []

print("=" * 55)
print("  Triage Evaluation — 20 Emergency Cases")
print("=" * 55)

for t in d['triage_tests']:
    r  = classify(t['query'])
    ok = r.level.value == t['expected']
    correct += 1 if ok else 0
    if not ok:
        failures.append(t['query'])
    status = "PASS" if ok else "FAIL"
    print(f"  {status} [{t['lang']}] {t['query'][:45]}")

print("=" * 55)
print(f"  Triage: {correct}/20 = {correct/20:.0%}")
if failures:
    print(f"  FAILED: {failures}")
else:
    print("  All RED cases detected correctly!")
print("=" * 55)