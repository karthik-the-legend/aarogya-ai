import sys
sys.path.insert(0, 'backend')
from triage import EMERGENCY_KEYWORDS

query = "ಎದೆ ನೋವು"
print(f"Query bytes    : {query.encode('utf-8')}")

# Find Kannada keywords in list
kannada_kws = [kw for kw in EMERGENCY_KEYWORDS if any(ord(c) > 0x0C80 for c in kw)]
print(f"Kannada keywords in list: {kannada_kws}")

# Check each one against query
for kw in kannada_kws:
    print(f"  '{kw}' in query: {kw.lower() in query.lower()}")
    print(f"  kw bytes: {kw.encode('utf-8')}")